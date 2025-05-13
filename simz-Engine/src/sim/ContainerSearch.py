import json
import pandas as pd
import duckdb
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
import numpy as np


class ContainerScraper:
    """
    A class to scrape and analyze CSV data using DuckDB, particularly for processing
    time series data with complex nested JSON structures.
    """

    def __init__(self, csv_filepath: str):
        """
        Initialize the scraper with a CSV file path.
        Args:
            csv_filepath: Path to the CSV file
        """
        self.csv_filepath = csv_filepath
        self.conn = duckdb.connect(database=":memory:")
        self.df: Optional[pd.DataFrame] = None
        self.components_data = {}
        self.containers_data = {}
        self.load_data()

    def load_data(self) -> None:
        """Load the CSV data and prepare it for querying."""
        try:
            # Read the CSV data
            self.df = pd.read_csv(self.csv_filepath)

            # Parse the JSON strings in values and PDV columns
            self.df["values"] = self.df["values"].apply(
                lambda x: json.loads(x.replace("'", '"')) if isinstance(x, str) else x
            )
            self.df["PDV"] = self.df["PDV"].apply(
                lambda x: json.loads(x.replace("'", '"')) if isinstance(x, str) else x
            )

            # Extract component IDs and types for easier access
            self.components_data = self._extract_components_data()
            self.containers_data = self._extract_containers_data()

            # Register the DataFrame as a view in DuckDB
            self.conn.register("csv_data", self.df)
            print(f"Data loaded successfully: {len(self.df)} rows")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _extract_components_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract component information from the DataFrame.

        Returns:
            Dict mapping component_id to component metadata
        """
        components = {}
        for _, row in self.df.iterrows():
            comp_id = row["component_id"]
            comp_type = row["component_type"]

            if comp_id not in components:
                components[comp_id] = {"type": comp_type, "actions": set()}

            # Add the action to the component's set of actions
            if "action" in row and pd.notna(row["action"]):
                components[comp_id]["actions"].add(row["action"])

        return components

    def _extract_containers_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract container information from the PDV field.

        Returns:
            Dict mapping container_id to container metadata
        """
        containers = {}

        for _, row in self.df.iterrows():
            if not isinstance(row["PDV"], dict) or "containerId" not in row["PDV"]:
                continue

            container_id = row["PDV"]["containerId"]

            if container_id not in containers:
                containers[container_id] = {
                    "types": row["PDV"].get("types", {}),
                    "first_seen": row["time"],
                    "last_seen": row["time"],
                }
            else:
                # Update the last seen time
                containers[container_id]["last_seen"] = max(
                    containers[container_id]["last_seen"], row["time"]
                )

        return containers

    def analyze_container_workflow_enhanced(self, container_id: str) -> Dict[str, Any]:
        """
        Analyze the workflow of a specific container with optimized data structure.
        Creates a combined workflow that is component-centric, with each component
        containing its actions and associated container attributes.

        Args:
            container_id: The ID of the container to analyze

        Returns:
            Dict containing the workflow analysis results with component-centric organization
        """
        if self.df is None:
            return {}

        if container_id not in self.containers_data:
            return {"error": f"Container ID {container_id} not found"}

        # Filter data for this container directly
        container_df = self.df[
            self.df["PDV"].apply(
                lambda pdv: isinstance(pdv, dict)
                and "containerId" in pdv
                and pdv["containerId"] == container_id
            )
        ]

        if container_df.empty:
            return {"error": f"No data found for container ID {container_id}"}

        # Sort by time
        container_df = container_df.sort_values("time")

        # Extract container attributes and types
        container_attributes = self._extract_container_attributes(container_id)
        container_types = self.containers_data[container_id].get("types", {})

        # For bottleneck analysis - not included in the result
        component_times = self._calculate_component_times(container_df)

        # Initialize results dictionary with container information
        result = {
            "container_id": container_id,
            "start_time": self.containers_data[container_id]["first_seen"],
            "end_time": self.containers_data[container_id]["last_seen"],
            "total_processing_time": (
                self.containers_data[container_id]["last_seen"]
                - self.containers_data[container_id]["first_seen"]
            ),
            "attributes": container_attributes,
            "types": container_types,
        }

        # Store component_times internally for bottleneck analysis
        # This won't be included in the final output
        self._temp_component_times = component_times

        # Create a component-centric workflow structure
        component_workflow = {}

        # First pass: collect all actions by component
        for _, row in container_df.sort_values("time").iterrows():
            comp_id = row["component_id"]
            comp_type = row["component_type"]
            action = row["action"]
            timestamp = row["time"]

            # Initialize component entry if not exists
            if comp_id not in component_workflow:
                component_workflow[comp_id] = {
                    "component_id": comp_id,
                    "component_type": comp_type,
                    "actions": [],
                }

            # Create action entry
            action_entry = {
                "action": action,
                "timestamp": timestamp,
                "attributes": container_attributes,
            }

            # Add values if available
            if isinstance(row["values"], dict):
                action_entry["values"] = row["values"]

            # Add action to component
            component_workflow[comp_id]["actions"].append(action_entry)

        # Convert the component workflow dictionary to a list
        combined_workflow = list(component_workflow.values())

        # Add the combined workflow to the result
        result["combined_workflow"] = combined_workflow

        return result

    def _get_component_path(self, container_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Extract the path a container takes through components.

        Args:
            container_df: DataFrame containing data for a single container

        Returns:
            List of components visited in order with metadata
        """
        path = []
        visited_components = set()

        for _, row in container_df.iterrows():
            comp_id = row["component_id"]
            comp_type = row["component_type"]
            action = row["action"]
            timestamp = row["time"]
            # Create a unique key for this component+action combination
            path_key = f"{comp_id}:{action}"

            if path_key not in visited_components:
                visited_components.add(path_key)

                component_info = {
                    "component_id": comp_id,
                    "component_type": comp_type,
                    "action": action,
                    "timestamp": timestamp,
                }

                # Add values data if available
                if isinstance(row["values"], dict):
                    component_info["values"] = row["values"]

                path.append(component_info)

        return path

    def _calculate_component_times(
        self, container_df: pd.DataFrame
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate time spent in each component by action.

        Args:
            container_df: DataFrame containing data for a single container

        Returns:
            Dict mapping component_id to processing time details
        """
        component_times = {}

        # Group by component and action
        for comp_id, comp_df in container_df.groupby("component_id"):
            if comp_id not in component_times:
                component_times[comp_id] = {
                    "type": comp_df["component_type"].iloc[0],
                    "actions": {},
                }

            # Process each action type for this component
            for action, action_df in comp_df.groupby("action"):
                # Handle ENTER/Exit pairs to calculate processing time
                if action == "ENTER" or action == "Exit":
                    # Extract in_time and out_time
                    enter_rows = action_df[action_df["action"] == "ENTER"]
                    exit_rows = action_df[action_df["action"] == "Exit"]

                    if not enter_rows.empty and not exit_rows.empty:
                        # Get the values dictionaries
                        for _, enter_row in enter_rows.iterrows():
                            values = enter_row.get("values", {})
                            if isinstance(values, dict) and "in_time" in values:
                                in_time = values["in_time"]

                                # Find matching exit row
                                for _, exit_row in exit_rows.iterrows():
                                    exit_values = exit_row.get("values", {})
                                    if (
                                        isinstance(exit_values, dict)
                                        and "out_time" in exit_values
                                        and exit_values.get("input_count")
                                        == values.get("input_count")
                                    ):
                                        out_time = exit_values["out_time"]
                                        processing_time = out_time - in_time

                                        # Add to component times
                                        if (
                                            action
                                            not in component_times[comp_id]["actions"]
                                        ):
                                            component_times[comp_id]["actions"][
                                                action
                                            ] = []

                                        component_times[comp_id]["actions"][
                                            action
                                        ].append(
                                            {
                                                "in_time": in_time,
                                                "out_time": out_time,
                                                "processing_time": processing_time,
                                                "input_count": values.get(
                                                    "input_count"
                                                ),
                                            }
                                        )

                # For other actions like GENERATE, QUEUED
                else:
                    for _, row in action_df.iterrows():
                        values = row.get("values", {})

                        if action not in component_times[comp_id]["actions"]:
                            component_times[comp_id]["actions"][action] = []

                        action_info = {"timestamp": row["time"]}

                        # Add any relevant values
                        if isinstance(values, dict):
                            for key, val in values.items():
                                action_info[key] = val

                        component_times[comp_id]["actions"][action].append(action_info)

        return component_times

    def _calculate_efficiency_metrics(
        self,
        container_df: pd.DataFrame,
        component_times: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate efficiency metrics for container processing.

        Args:
            container_df: DataFrame containing data for a single container
            component_times: Dictionary of component processing times

        Returns:
            Dict of efficiency metrics
        """
        metrics = {}

        # Total time from first to last event
        start_time = container_df["time"].min()
        end_time = container_df["time"].max()
        total_time = end_time - start_time
        metrics["total_time"] = total_time

        # Calculate active processing time (sum of all component processing times)
        active_time = 0
        for comp_id, comp_data in component_times.items():
            for action, action_data in comp_data.get("actions", {}).items():
                for entry in action_data:
                    if "processing_time" in entry:
                        active_time += entry["processing_time"]

        metrics["active_processing_time"] = active_time

        # Calculate queue times
        queue_times = []
        for comp_id, comp_data in component_times.items():
            if "QUEUED" in comp_data.get("actions", {}):
                for queue_entry in comp_data["actions"]["QUEUED"]:
                    if "queue_length" in queue_entry:
                        queue_times.append(queue_entry["queue_length"])

        if queue_times:
            metrics["avg_queue_length"] = sum(queue_times) / len(queue_times)
            metrics["max_queue_length"] = max(queue_times)
        else:
            metrics["avg_queue_length"] = 0
            metrics["max_queue_length"] = 0

        # Calculate throughput (operations per time unit)
        # Count the number of operations (GENERATE, ENTER, Exit, etc.)
        num_operations = len(container_df)
        metrics["throughput"] = num_operations / total_time if total_time > 0 else 0

        # Calculate efficiency ratio (active time / total time)
        metrics["efficiency_ratio"] = active_time / total_time if total_time > 0 else 0

        return metrics

    def _extract_container_attributes(self, container_id: str) -> Dict[str, Any]:
        """
        Extract attributes for a specific container from PDV data.

        Args:
            container_id: The ID of the container to extract attributes for

        Returns:
            Dict of container attributes
        """
        if container_id not in self.containers_data:
            return {}

        container_data = self.containers_data[container_id]
        attributes = {}

        # Extract type information and attributes
        if "types" in container_data:
            types_data = container_data["types"]
            for type_id, type_info in types_data.items():
                type_name = type_info.get("typeName")

                if type_name:
                    attributes[type_name] = {}

                    # Extract attributes if they exist
                    if "attributes" in type_info:
                        for attr_name, attr_data in type_info["attributes"].items():
                            if isinstance(attr_data, dict) and "value" in attr_data:
                                attributes[type_name][attr_name] = attr_data["value"]

        return attributes

    def get_all_container_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        Get workflow analysis for all containers.

        Returns:
            Dict mapping container_id to workflow analysis
        """
        results = {}

        for container_id in self.containers_data.keys():
            results[container_id] = self.analyze_container_workflow_enhanced(
                container_id
            )

        return results

    def get_container_component_dependencies(
        self, container_id: str
    ) -> List[Tuple[str, str]]:
        """
        Get the sequence of component interactions for a container.

        Args:
            container_id: The ID of the container to analyze

        Returns:
            List of component pairs representing the flow (from_component, to_component)
        """
        if container_id not in self.containers_data:
            return []

        # Filter data for this container
        container_rows = []
        for _, row in self.df.iterrows():
            if (
                isinstance(row["PDV"], dict)
                and "containerId" in row["PDV"]
                and row["PDV"]["containerId"] == container_id
            ):
                container_rows.append(row)

        if not container_rows:
            return []

        # Convert to DataFrame and sort by time
        container_df = pd.DataFrame(container_rows)
        container_df = container_df.sort_values("time")

        # Build the sequence of component interactions
        components_sequence = []
        prev_component = None

        for _, row in container_df.iterrows():
            curr_component = row["component_id"]

            if prev_component is not None and prev_component != curr_component:
                components_sequence.append((prev_component, curr_component))

            prev_component = curr_component

        return components_sequence

    def get_bottleneck_analysis(self) -> Dict[str, Any]:
        """
        Identify bottlenecks in the processing pipeline.

        Returns:
            Dict containing bottleneck analysis
        """
        bottlenecks = {
            "components": {},
            "longest_queue_times": [],
            "longest_processing_times": [],
        }

        # Analyze each container workflow
        for container_id in self.containers_data.keys():
            # Call analyze_container_workflow_enhanced to populate _temp_component_times
            self.analyze_container_workflow_enhanced(container_id)

            # Now use the internal _temp_component_times attribute
            for comp_id, comp_data in getattr(
                self, "_temp_component_times", {}
            ).items():
                if comp_id not in bottlenecks["components"]:
                    bottlenecks["components"][comp_id] = {
                        "type": comp_data.get("type"),
                        "total_processing_time": 0,
                        "total_queue_time": 0,
                        "count": 0,
                    }

                # Update processing times
                for action_name, action_data in comp_data.get("actions", {}).items():
                    for entry in action_data:
                        if action_name == "ENTER" or action_name == "Exit":
                            if "processing_time" in entry:
                                bottlenecks["components"][comp_id][
                                    "total_processing_time"
                                ] += entry["processing_time"]
                                bottlenecks["components"][comp_id]["count"] += 1

                                # Track individual long processing times
                                bottlenecks["longest_processing_times"].append(
                                    {
                                        "container_id": container_id,
                                        "component_id": comp_id,
                                        "processing_time": entry["processing_time"],
                                        "input_count": entry.get("input_count"),
                                    }
                                )

                        elif action_name == "QUEUED":
                            if "queue_length" in entry and entry["queue_length"] > 0:
                                bottlenecks["components"][comp_id][
                                    "total_queue_time"
                                ] += 1

                                # Track individual long queue times
                                bottlenecks["longest_queue_times"].append(
                                    {
                                        "container_id": container_id,
                                        "component_id": comp_id,
                                        "queue_length": entry["queue_length"],
                                        "timestamp": entry.get(
                                            "timestamp", entry.get("in_time")
                                        ),
                                    }
                                )

        # Calculate averages
        for comp_id, comp_data in bottlenecks["components"].items():
            if comp_data["count"] > 0:
                comp_data["avg_processing_time"] = (
                    comp_data["total_processing_time"] / comp_data["count"]
                )
            else:
                comp_data["avg_processing_time"] = 0

        # Sort the longest processing times and queue times
        bottlenecks["longest_processing_times"] = sorted(
            bottlenecks["longest_processing_times"],
            key=lambda x: x["processing_time"],
            reverse=True,
        )[:10]  # Top 10

        bottlenecks["longest_queue_times"] = sorted(
            bottlenecks["longest_queue_times"],
            key=lambda x: x["queue_length"],
            reverse=True,
        )[:10]  # Top 10

        return bottlenecks
