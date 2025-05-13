from collections import Counter
import json
import pandas as pd
import duckdb
from typing import Dict, Any, Optional, List
import numpy as np


class CSVScraper:
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

    def _extract_components_info(self) -> None:
        """Extract information about unique components and their actions"""
        # Get unique component IDs and their types
        if self.df is None:
            return
        unique_components = self.df[
            ["component_id", "component_type"]
        ].drop_duplicates()

        for _, row in unique_components.iterrows():
            component_id = row["component_id"]
            component_type = row["component_type"]

            # Initialize component data structure
            self.components_data[component_id] = {
                "type": component_type,
                "actions": self._get_component_actions(component_id),
                "metrics": {},
            }

        # Extract container information from PDV
        self._extract_container_info()

    def _extract_container_info(self) -> None:
        """Extract container information from the PDV field"""

        if self.df is None:
            return

        for _, row in self.df.iterrows():
            if isinstance(row["PDV"], dict) and "containerId" in row["PDV"]:
                container_id = row["PDV"]["containerId"]
                if container_id not in self.containers_data:
                    self.containers_data[container_id] = {
                        "first_seen": row["time"],
                        "components_interacted": set(),
                        "actions": [],
                    }

                # Add component to container's interaction list
                self.containers_data[container_id]["components_interacted"].add(
                    row["component_id"]
                )

                # Add action to container's action list
                self.containers_data[container_id]["actions"].append(
                    {
                        "time": row["time"],
                        "component_id": row["component_id"],
                        "action": row["action"],
                    }
                )

    def _get_component_actions(self, component_id: str) -> Dict[str, int]:
        """Get all actions performed by a specific component and their counts"""
        if self.df is None:
            return {}

        actions = (
            self.df[self.df["component_id"] == component_id]["action"]
            .value_counts()
            .to_dict()
        )
        return actions

    def get_component_actions(self, component_id: str) -> pd.DataFrame:
        """
        Get all actions for a specific component.

        Args:
            component_id: The ID of the component to filter by

        Returns:
            DataFrame containing filtered actions
        """
        query = f"""
        SELECT time, component_type, action, values
        FROM csv_data
        WHERE component_id = '{component_id}'
        ORDER BY time ASC
        """
        return self.conn.execute(query).fetchdf()

    def get_action_counts(self) -> pd.DataFrame:
        """
        Count the number of each action type.

        Returns:
            DataFrame with action counts
        """
        query = """
        SELECT action, COUNT(*) as count
        FROM csv_data
        GROUP BY action
        ORDER BY count DESC
        """
        return self.conn.execute(query).fetchdf()

    def get_component_types(self) -> pd.DataFrame:
        """
        Get unique component types and their counts.

        Returns:
            DataFrame with component types and counts
        """
        query = """
        SELECT component_type, COUNT(DISTINCT component_id) as unique_components
        FROM csv_data
        GROUP BY component_type
        """
        return self.conn.execute(query).fetchdf()

    def get_time_range(self) -> Dict[str, int]:
        """
        Get the minimum and maximum time values.

        Returns:
            Dict with min and max time values
        """
        query = """
        SELECT MIN(time) as min_time, MAX(time) as max_time
        FROM csv_data
        """
        result = self.conn.execute(query).fetchdf()
        # Fix the return type issue by explicitly casting to int
        return {
            "min_time": int(result["min_time"].iloc[0]),
            "max_time": int(result["max_time"].iloc[0]),
        }

    def get_container_stats(self) -> pd.DataFrame:
        """
        Extract container IDs and count their occurrences.

        Returns:
            DataFrame with container statistics
        """
        # This query extracts containerId from the PDV JSON column
        query = """
        SELECT 
            json_extract(PDV, '$.containerId') as container_id,
            COUNT(*) as occurrence_count
        FROM csv_data
        WHERE PDV IS NOT NULL
        GROUP BY container_id
        ORDER BY occurrence_count DESC
        """
        return self.conn.execute(query).fetchdf()

    def get_component_timeline(self, component_id: str) -> pd.DataFrame:
        """
        Get a timeline of actions for a specific component.

        Args:
            component_id: The ID of the component

        Returns:
            DataFrame with the component's action timeline
        """
        query = f"""
        SELECT 
            time,
            action,
            json_extract(values, '$.input_count') as input_count,
            json_extract(values, '$.run_count') as run_count,
            json_extract(values, '$.queue_length') as queue_length
        FROM csv_data
        WHERE component_id = '{component_id}'
        ORDER BY time ASC
        """
        return self.conn.execute(query).fetchdf()

    def extract_container_data(self) -> List[Dict[str, Any]]:
        """
        Extract all container data into a more accessible format.

        Returns:
            List of dictionaries with container data
        """
        container_data = []

        # Check if DataFrame is loaded before iterating
        if self.df is None:
            return container_data

        for _, row in self.df.iterrows():
            pdv = row.get("PDV", {})
            if isinstance(pdv, dict) and "containerId" in pdv:
                container_info = {
                    "time": row["time"],
                    "container_id": pdv["containerId"],
                    "component_id": row["component_id"],
                    "action": row["action"],
                }

                # Extract type information if available
                if "types" in pdv:
                    type_info = []
                    # Ensure types is a dictionary before calling items()
                    if isinstance(pdv["types"], dict):
                        for type_id, type_data in pdv["types"].items():
                            type_info_item = {
                                "type_id": type_id,
                                "type_name": type_data.get("typeName"),
                                "gen_component_id": type_data.get("genComponentId"),
                            }
                            # Handle attributes safely
                            if isinstance(type_data.get("attributes"), dict):
                                type_info_item["attributes"] = type_data.get(
                                    "attributes", {}
                                )
                            else:
                                type_info_item["attributes"] = {}

                            type_info.append(type_info_item)

                    container_info["types"] = type_info

                container_data.append(container_info)

        return container_data

    def analyze_flow_efficiency(self) -> Dict[str, Any]:
        """
        Analyze the efficiency of the process flow.

        Returns:
            Dictionary with efficiency metrics
        """
        # Check if DataFrame is loaded
        if self.df is None:
            return {
                "error": "No data loaded",
                "avg_processing_time": 0,
                "avg_queue_time": 0,
                "max_processing_time": 0,
                "max_queue_time": 0,
                "total_processing_time": 0,
                "total_queue_time": 0,
                "processing_efficiency": 0,
            }

        # Calculate time in queue vs time in processing
        resource_entries = self.df[self.df["action"] == "ENTER"]
        resource_exits = self.df[self.df["action"] == "Exit"]
        queue_entries = self.df[self.df["action"] == "QUEUED"]

        # Calculate average processing time
        processing_times = []
        for _, entry in resource_entries.iterrows():
            component_id = entry["component_id"]
            entry_time = entry["time"]

            # Find corresponding exit
            exits = resource_exits[
                (resource_exits["component_id"] == component_id)
                & (resource_exits["time"] > entry_time)
            ]
            # Properly handle DataFrame filtering results
            if isinstance(exits, pd.DataFrame) and not exits.empty:
                exit_time = exits.iloc[0]["time"]
                processing_times.append(exit_time - entry_time)

        # Calculate average queue time
        queue_times = []
        for _, queue in queue_entries.iterrows():
            component_id = queue["component_id"]
            queue_time = queue["time"]

            # Find next entry for this component after queueing
            entries = resource_entries[
                (resource_entries["component_id"] == component_id)
                & (resource_entries["time"] >= queue_time)
            ]
            # Properly handle DataFrame filtering results
            if isinstance(entries, pd.DataFrame) and not entries.empty:
                entry_time = entries.iloc[0]["time"]
                queue_times.append(entry_time - queue_time)

        return {
            "avg_processing_time": sum(processing_times) / len(processing_times)
            if processing_times
            else 0,
            "avg_queue_time": sum(queue_times) / len(queue_times) if queue_times else 0,
            "max_processing_time": max(processing_times) if processing_times else 0,
            "max_queue_time": max(queue_times) if queue_times else 0,
            "total_processing_time": sum(processing_times),
            "total_queue_time": sum(queue_times),
            "processing_efficiency": sum(processing_times)
            / (sum(processing_times) + sum(queue_times))
            if (processing_times and queue_times)
            else 0,
        }

    def get_component_stats(self) -> pd.DataFrame:
        """
        Get statistics for each component.

        Returns:
            DataFrame with component statistics
        """
        query = """
        SELECT 
            component_id,
            component_type,
            COUNT(*) as action_count,
            MIN(time) as first_seen,
            MAX(time) as last_seen
        FROM csv_data
        GROUP BY component_id, component_type
        ORDER BY action_count DESC
        """
        return self.conn.execute(query).fetchdf()

    def get_ph_value_stats(self) -> Dict[str, Any]:
        """
        Analyze the pH values in the Water type attributes.

        Returns:
            Dictionary with pH value statistics
        """
        ph_values = []

        # Check if DataFrame is loaded
        if self.df is None:
            return {"error": "No data loaded"}

        for _, row in self.df.iterrows():
            pdv = row.get("PDV", {})
            if isinstance(pdv, dict) and "types" in pdv:
                # Ensure types is a dictionary before calling items()
                if isinstance(pdv["types"], dict):
                    for _, type_data in pdv["types"].items():
                        if type_data.get("typeName") == "Water" and isinstance(
                            type_data.get("attributes"), dict
                        ):
                            attr = type_data["attributes"]
                            if (
                                "ph" in attr
                                and isinstance(attr["ph"], dict)
                                and "value" in attr["ph"]
                            ):
                                ph_values.append(attr["ph"]["value"])

        if not ph_values:
            return {"error": "No pH values found"}

        return {
            "count": len(ph_values),
            "min": min(ph_values),
            "max": max(ph_values),
            "avg": sum(ph_values) / len(ph_values),
            "unique_values": list(set(ph_values)),
        }

    def run_custom_query(self, query: str) -> pd.DataFrame:
        """
        Run a custom DuckDB query on the data.

        Args:
            query: SQL query string

        Returns:
            DataFrame with query results
        """
        try:
            return self.conn.execute(query).fetchdf()
        except Exception as e:
            print(f"Query error: {e}")
            raise

    def close(self) -> None:
        """Close the DuckDB connection."""
        self.conn.close()

    def get_table_data(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_column: Optional[str] = None,
        sort_direction: str = "asc",
        search_query: Optional[str] = None,
        search_columns: Optional[List[str]] = None,
        filter_conditions: Optional[Dict[str, Any]] = None,
        include_columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Prepare data for a React table with advanced search, sorting, and pagination.

        Args:
            page: Current page number (1-based)
            page_size: Number of records per page
            sort_column: Column to sort by
            sort_direction: Sort direction ("asc" or "desc")
            search_query: Text to search for across specified columns
            search_columns: Columns to include in text search (defaults to all string columns)
            filter_conditions: Dictionary of column-value pairs for filtering
            include_columns: List of columns to include in the result (defaults to all)

        Returns:
            Dictionary with paginated data, total count, and metadata
        """
        if self.df is None:
            return {
                "data": [],
                "total": 0,
                "page": page,
                "pageSize": page_size,
                "totalPages": 0,
                "columns": [],
            }

        # Make a copy to avoid modifying the original
        # Explicitly cast to DataFrame to help type checking
        filtered_df: pd.DataFrame = self.df.copy()

        # Apply column filtering if specified
        if include_columns:
            # Ensure all requested columns exist
            existing_columns = [
                col for col in include_columns if col in filtered_df.columns
            ]
            if existing_columns:
                # Explicitly create a new DataFrame to ensure type consistency
                filtered_df = pd.DataFrame(filtered_df[existing_columns])

        # Determine searchable columns if not specified
        if search_query and search_columns is None:
            # Default to string-type columns for search
            search_columns = []
            for col in filtered_df.columns:
                # Use Series-specific methods for type checking
                col_series = filtered_df[col]
                # Check if column contains string data
                if pd.api.types.is_object_dtype(col_series):
                    # Use a safer approach to check for string values
                    if col_series.dropna().astype(str).str.len().any():
                        search_columns.append(col)

        # Apply text search across specified columns
        if search_query and search_columns:
            # Initialize mask as a pandas Series with proper index alignment
            search_mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
            search_query_lower = search_query.lower()

            for col in search_columns:
                if col in filtered_df.columns:
                    # Create a Series from the column for safe operations
                    col_series = filtered_df[col]
                    # Convert column to string and search - handle properly as a Series
                    col_search = (
                        col_series.astype(str)
                        .str.lower()
                        .str.contains(search_query_lower, na=False)
                    )
                    search_mask = search_mask | col_search

            # Filter using the mask - explicitly cast to ensure DataFrame type
            filtered_df = pd.DataFrame(
                filtered_df.loc[search_mask]
            )  # Use .loc[] and explicit cast

        # Apply specific filter conditions
        if filter_conditions:
            for col, value in filter_conditions.items():
                if col in filtered_df.columns:
                    col_series = filtered_df[
                        col
                    ]  # Extract as Series for proper methods

                    if isinstance(value, list):
                        # Handle list of values (IN condition)
                        filtered_df = pd.DataFrame(
                            filtered_df.loc[col_series.isin(value)]
                        )  # Explicit cast
                    elif isinstance(value, dict) and ("min" in value or "max" in value):
                        # Handle range filter
                        mask = pd.Series(True, index=filtered_df.index)
                        if "min" in value and value["min"] is not None:
                            mask = mask & (col_series >= value["min"])
                        if "max" in value and value["max"] is not None:
                            mask = mask & (col_series <= value["max"])
                        filtered_df = pd.DataFrame(
                            filtered_df.loc[mask]
                        )  # Explicit cast
                    elif isinstance(value, dict) and "regex" in value:
                        # Handle regex matching
                        pattern = value["regex"]
                        regex_mask = col_series.astype(str).str.match(pattern, na=False)
                        filtered_df = pd.DataFrame(
                            filtered_df.loc[regex_mask]
                        )  # Explicit cast
                    else:
                        # Exact match
                        filtered_df = pd.DataFrame(
                            filtered_df.loc[col_series == value]
                        )  # Explicit cast

        # Calculate total records after filtering
        total_records = len(filtered_df)
        total_pages = (
            (total_records + page_size - 1) // page_size if page_size > 0 else 1
        )

        # Apply sorting - ensure we're working with a DataFrame
        if sort_column and sort_column in filtered_df.columns:
            ascending = sort_direction.lower() == "asc"
            # Sort values returns a DataFrame, so this is safe
            filtered_df = filtered_df.sort_values(by=[sort_column], ascending=ascending)

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        # iloc returns a DataFrame when slicing rows
        paginated_df = filtered_df.iloc[start_idx:end_idx]

        # Convert to list of dictionaries (JSON-serializable)
        records = []
        for _, row in paginated_df.iterrows():
            # Handle non-serializable objects
            record = {}
            for col, val in row.items():
                if isinstance(val, (dict, list, str, int, float, bool)) or val is None:
                    record[col] = val
                else:
                    # Convert to string representation
                    record[col] = str(val)
            records.append(record)

        # Prepare column metadata
        columns = []
        for col in paginated_df.columns:
            # Get the Series for this column to check type
            col_series = paginated_df[col]
            is_numeric = pd.api.types.is_numeric_dtype(col_series)
            is_datetime = pd.api.types.is_datetime64_dtype(col_series)

            columns.append(
                {
                    "field": col,
                    "headerName": col.replace("_", " ").title(),
                    "type": "number"
                    if is_numeric
                    else "date"
                    if is_datetime
                    else "string",
                    "sortable": True,
                    "filterable": True,
                }
            )

        return {
            "data": records,
            "total": total_records,
            "page": page,
            "pageSize": page_size,
            "totalPages": total_pages,
            "columns": columns,
        }

    def count_containers_duckdb(self) -> Dict[str, Any]:
        """
        Count all unique containers using DuckDB query.

        Returns:
            Dictionary with container count statistics
        """
        if self.df is None:
            return {"error": "No data loaded", "total_containers": 0}

        # Query to get basic container statistics
        query = """
        SELECT 
            json_extract(PDV, '$.containerId') as container_id,
            COUNT(*) as occurrence_count,
            MIN(time) as first_seen,
            MAX(time) as last_seen,
            MAX(time) - MIN(time) as lifespan
        FROM csv_data
        WHERE PDV IS NOT NULL
        GROUP BY container_id
        ORDER BY occurrence_count DESC
        """

        container_stats = self.conn.execute(query).fetchdf()

        # Further process the results to get component and action counts
        container_details = []

        for _, container in container_stats.iterrows():
            container_id = container["container_id"]

            # Query to get unique components for this container
            components_query = f"""
            SELECT 
                DISTINCT component_id
            FROM csv_data
            WHERE json_extract(PDV, '$.containerId') = '{container_id}'
            """
            components = self.conn.execute(components_query).fetchdf()

            # Query to get unique actions for this container
            actions_query = f"""
            SELECT 
                DISTINCT action
            FROM csv_data
            WHERE json_extract(PDV, '$.containerId') = '{container_id}'
            """
            actions = self.conn.execute(actions_query).fetchdf()

            container_details.append(
                {
                    "container_id": container_id,
                    "occurrence_count": int(container["occurrence_count"]),
                    "first_seen": int(container["first_seen"]),
                    "last_seen": int(container["last_seen"]),
                    "lifespan": int(container["lifespan"]),
                    "component_interactions": components["component_id"].tolist(),
                    "component_interaction_count": len(components),
                    "actions": actions["action"].tolist(),
                    "action_count": len(actions),
                }
            )

        return {
            "total_containers": len(container_stats),
            "containers": container_details,
            "container_with_most_occurrences": container_details[0]
            if container_details
            else None,
            "container_with_longest_lifespan": max(
                container_details, key=lambda x: x["lifespan"]
            )
            if container_details
            else None,
        }

    def _extract_components_data(self) -> Dict[str, Dict[str, Any]]:
        """Extract component data from the DataFrame."""
        components = {}
        for _, row in self.df.iterrows():
            comp_id = row["component_id"]
            comp_type = row["component_type"]

            if comp_id not in components:
                components[comp_id] = {
                    "type": comp_type,
                    "actions": [],
                    "container_interactions": set(),
                    "processing_times": [],
                }

            # Add action to the component
            action_data = {
                "time": row["time"],
                "action": row["action"],
                "values": row["values"] if isinstance(row["values"], dict) else {},
            }
            components[comp_id]["actions"].append(action_data)

            # Track container interactions
            if isinstance(row["PDV"], dict) and "containerId" in row["PDV"]:
                components[comp_id]["container_interactions"].add(
                    row["PDV"]["containerId"]
                )

        return components

    def _extract_containers_data(self) -> Dict[str, Dict[str, Any]]:
        """Extract container data from the DataFrame."""
        containers = {}
        for _, row in self.df.iterrows():
            if isinstance(row["PDV"], dict) and "containerId" in row["PDV"]:
                container_id = row["PDV"]["containerId"]

                if container_id not in containers:
                    containers[container_id] = {
                        "types": {},
                        "components_interacted": set(),
                        "timeline": [],
                    }

                # Add component to the container's interacted components
                containers[container_id]["components_interacted"].add(
                    row["component_id"]
                )

                # Add to timeline
                containers[container_id]["timeline"].append(
                    {
                        "time": row["time"],
                        "component_id": row["component_id"],
                        "action": row["action"],
                    }
                )

                # Extract types data
                if "types" in row["PDV"]:
                    for type_id, type_data in row["PDV"]["types"].items():
                        if type_id not in containers[container_id]["types"]:
                            containers[container_id]["types"][type_id] = type_data

        return containers

    def calculate_component_efficiency(
        self, component_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate efficiency metrics for components.
        Efficiency is calculated as the ratio of productive actions to total actions.

        Args:
            component_id: Optional specific component to analyze

        Returns:
            Dictionary of component IDs mapped to their efficiency scores
        """
        component_efficiency = {}

        components_to_analyze = (
            [component_id] if component_id else self.components_data.keys()
        )

        for comp_id in components_to_analyze:
            if comp_id not in self.components_data:
                continue

            actions = self.components_data[comp_id]["actions"]

            # Count actions by type
            action_counts = Counter(action["action"] for action in actions)

            # Calculate different types of efficiency
            if comp_id.startswith("b"):  # Generator components
                # For generators, efficiency is the ratio of successful GENERATEs to total actions
                total_actions = len(actions)
                productive_actions = action_counts.get("GENERATE", 0)

            elif "resource" in self.components_data[comp_id]["type"]:
                # For resources, efficiency is based on ENTER to Exit ratio
                enters = action_counts.get("ENTER", 0)
                exits = action_counts.get("Exit", 0)

                if enters > 0:
                    productive_actions = exits
                    total_actions = enters
                else:
                    productive_actions = 0
                    total_actions = 1  # Avoid division by zero
            else:
                # Generic case
                total_actions = len(actions)
                productive_actions = total_actions - action_counts.get("QUEUED", 0)

            # Calculate efficiency (avoid division by zero)
            if total_actions > 0:
                efficiency = productive_actions / total_actions
            else:
                efficiency = 0.0

            component_efficiency[comp_id] = round(efficiency, 2)

        return (
            component_efficiency
            if not component_id
            else component_efficiency.get(component_id, 0.0)
        )

    def calculate_processing_time(
        self, component_id: Optional[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate processing time metrics for components.

        Args:
            component_id: Optional specific component to analyze

        Returns:
            Dictionary with component processing time statistics
        """
        processing_times = {}

        # Get components to analyze
        components_to_analyze = (
            [component_id] if component_id else self.components_data.keys()
        )

        for comp_id in components_to_analyze:
            if comp_id not in self.components_data:
                continue

            # Process by component type
            comp_type = self.components_data[comp_id]["type"]
            actions = self.components_data[comp_id]["actions"]

            # Sort actions by time
            sorted_actions = sorted(actions, key=lambda x: x["time"])

            times = []

            if comp_type == "generator":
                # For generators, processing time is the time between GENERATEs
                generate_times = [
                    action["time"]
                    for action in sorted_actions
                    if action["action"] == "GENERATE"
                ]

                if len(generate_times) > 1:
                    # Calculate intervals between consecutive generates
                    times = [
                        generate_times[i] - generate_times[i - 1]
                        for i in range(1, len(generate_times))
                    ]

            elif comp_type == "resource":
                # For resources, processing time is ENTER to Exit time
                # Create pairs of ENTER and Exit actions
                enter_exit_pairs = []
                current_enter = None

                for action in sorted_actions:
                    if action["action"] == "ENTER":
                        current_enter = action
                    elif action["action"] == "Exit" and current_enter:
                        enter_exit_pairs.append((current_enter, action))
                        current_enter = None

                # Calculate processing time for each pair
                times = [
                    exit_action["time"] - enter_action["time"]
                    for enter_action, exit_action in enter_exit_pairs
                ]

            # Calculate statistics if we have times
            if times:
                processing_times[comp_id] = {
                    "mean": round(np.mean(times), 2),
                    "median": round(np.median(times), 2),
                    "min": round(min(times), 2),
                    "max": round(max(times), 2),
                    "count": len(times),
                }
            else:
                processing_times[comp_id] = {
                    "mean": 0,
                    "median": 0,
                    "min": 0,
                    "max": 0,
                    "count": 0,
                }

        return (
            processing_times
            if not component_id
            else processing_times.get(component_id, {})
        )

    def calculate_wait_times(
        self, component_id: Optional[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate wait time metrics for components.
        Wait time is the time from QUEUED to ENTER.

        Args:
            component_id: Optional specific component to analyze

        Returns:
            Dictionary with component wait time statistics
        """
        wait_times = {}

        # Get components to analyze
        components_to_analyze = (
            [component_id] if component_id else self.components_data.keys()
        )

        for comp_id in components_to_analyze:
            if (
                comp_id not in self.components_data
                or self.components_data[comp_id]["type"] != "resource"
            ):
                continue

            actions = self.components_data[comp_id]["actions"]

            # Sort actions by time
            sorted_actions = sorted(actions, key=lambda x: x["time"])

            # Create pairs of QUEUED and ENTER actions
            queued_enter_pairs = []
            current_queued = None

            for action in sorted_actions:
                if action["action"] == "QUEUED":
                    current_queued = action
                elif action["action"] == "ENTER" and current_queued:
                    queued_enter_pairs.append((current_queued, action))
                    current_queued = None

            # Calculate wait time for each pair
            times = [
                enter_action["time"] - queued_action["time"]
                for queued_action, enter_action in queued_enter_pairs
            ]

            # Calculate statistics if we have times
            if times:
                wait_times[comp_id] = {
                    "mean": round(np.mean(times), 2),
                    "median": round(np.median(times), 2),
                    "min": round(min(times), 2),
                    "max": round(max(times), 2),
                    "count": len(times),
                }
            else:
                wait_times[comp_id] = {
                    "mean": 0,
                    "median": 0,
                    "min": 0,
                    "max": 0,
                    "count": 0,
                }

        return wait_times if not component_id else wait_times.get(component_id, {})

    def calculate_frequency(
        self, component_id: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate frequency metrics for components.

        Args:
            component_id: Optional specific component to analyze

        Returns:
            Dictionary with component frequency statistics
        """
        frequency_data = {}

        # Get components to analyze
        components_to_analyze = (
            [component_id] if component_id else self.components_data.keys()
        )

        for comp_id in components_to_analyze:
            if comp_id not in self.components_data:
                continue

            actions = self.components_data[comp_id]["actions"]

            # Count action types
            action_counts = Counter(action["action"] for action in actions)

            # Calculate time range
            times = [action["time"] for action in actions]
            if times:
                time_range = max(times) - min(times)
                if time_range > 0:
                    # Calculate actions per time unit
                    actions_per_time = len(actions) / time_range
                else:
                    actions_per_time = 0
            else:
                time_range = 0
                actions_per_time = 0

            frequency_data[comp_id] = {
                "action_counts": dict(action_counts),
                "total_actions": len(actions),
                "time_range": round(time_range, 2),
                "actions_per_time_unit": round(actions_per_time, 2),
            }

        return (
            frequency_data if not component_id else frequency_data.get(component_id, {})
        )

    def get_component_utilization(
        self, component_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate utilization metrics for components.
        Utilization is calculated as the percentage of time a component is active.

        Args:
            component_id: Optional specific component to analyze

        Returns:
            Dictionary of component IDs mapped to their utilization scores
        """
        utilization = {}

        # Get components to analyze
        components_to_analyze = (
            [component_id] if component_id else self.components_data.keys()
        )

        # Find total simulation time
        all_times = [
            action["time"]
            for comp in self.components_data.values()
            for action in comp["actions"]
        ]
        if all_times:
            total_time = max(all_times) - min(all_times)
        else:
            total_time = 1  # Avoid division by zero

        for comp_id in components_to_analyze:
            if comp_id not in self.components_data:
                continue

            comp_type = self.components_data[comp_id]["type"]
            actions = self.components_data[comp_id]["actions"]

            # Sort actions by time
            sorted_actions = sorted(actions, key=lambda x: x["time"])

            active_time = 0

            if comp_type == "generator":
                # For generators, active time is time spent generating
                # Assume each GENERATE takes 1 time unit
                active_time = sum(
                    1 for action in sorted_actions if action["action"] == "GENERATE"
                )

            elif comp_type == "resource":
                # For resources, active time is ENTER to Exit time
                current_enter = None

                for action in sorted_actions:
                    if action["action"] == "ENTER":
                        current_enter = action
                    elif action["action"] == "Exit" and current_enter:
                        active_time += action["time"] - current_enter["time"]
                        current_enter = None

            # Calculate utilization as a percentage
            if total_time > 0:
                utilization[comp_id] = round((active_time / total_time) * 100, 2)
            else:
                utilization[comp_id] = 0

        return utilization if not component_id else utilization.get(component_id, 0)

    def get_container_flow(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Track container flow through the system.

        Returns:
            Dictionary with container flow data
        """
        container_flow = {}

        for container_id, container_data in self.containers_data.items():
            timeline = sorted(container_data["timeline"], key=lambda x: x["time"])

            flow_data = []
            for entry in timeline:
                comp_id = entry["component_id"]
                comp_type = self.components_data.get(comp_id, {}).get("type", "unknown")

                flow_data.append(
                    {
                        "time": entry["time"],
                        "component_id": comp_id,
                        "component_type": comp_type,
                        "action": entry["action"],
                    }
                )

            container_flow[container_id] = flow_data

        return container_flow

    def get_component_bottlenecks(self) -> Dict[str, Dict[str, Any]]:
        """
        Identify potential bottlenecks in the system.

        Returns:
            Dictionary with bottleneck analysis
        """
        bottlenecks = {}

        # Calculate wait times for all components
        wait_times = self.calculate_wait_times()

        # Calculate processing times for all components
        processing_times = self.calculate_processing_time()

        # Identify resource components with high wait times
        for comp_id, data in wait_times.items():
            if data["mean"] > 0:
                wait_to_process_ratio = data["mean"] / processing_times.get(
                    comp_id, {}
                ).get("mean", 1)

                if wait_to_process_ratio > 1:  # If wait time exceeds processing time
                    bottlenecks[comp_id] = {
                        "type": "resource bottleneck",
                        "wait_time_mean": data["mean"],
                        "processing_time_mean": processing_times.get(comp_id, {}).get(
                            "mean", 0
                        ),
                        "wait_to_process_ratio": round(wait_to_process_ratio, 2),
                        "severity": "high" if wait_to_process_ratio > 2 else "medium",
                    }

        return bottlenecks

    def get_ep_chart_data(self) -> Dict[str, Any]:
        """
        Prepare data for charts.

        Returns:
            Dictionary with data formatted for various charts
        """
        chart_data = {
            "component_efficiency": self.calculate_component_efficiency(),
            "processing_times": {},
            "wait_times": {},
            "component_utilization": self.get_component_utilization(),
            "action_counts": {},
            "container_flow": {},
        }

        # Format processing times for chart
        proc_times = self.calculate_processing_time()
        for comp_id, data in proc_times.items():
            chart_data["processing_times"][comp_id] = data["mean"]

        # Format wait times for chart
        wait_times = self.calculate_wait_times()
        for comp_id, data in wait_times.items():
            chart_data["wait_times"][comp_id] = data["mean"]

        # Format action counts for chart
        freq_data = self.calculate_frequency()
        for comp_id, data in freq_data.items():
            chart_data["action_counts"][comp_id] = data["action_counts"]

        # Format container flow for timeline chart
        container_flow = self.get_container_flow()
        for container_id, flow in container_flow.items():
            if len(flow) > 0:
                chart_data["container_flow"][container_id] = {
                    "components": list(set(entry["component_id"] for entry in flow)),
                    "timeline": flow,
                }

        return chart_data

    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the system performance.

        Returns:
            Dictionary with summary report data
        """
        report = {
            "system_overview": {
                "total_components": len(self.components_data),
                "total_containers": len(self.containers_data),
                "generator_components": len(
                    [
                        c
                        for c, data in self.components_data.items()
                        if data["type"] == "generator"
                    ]
                ),
                "resource_components": len(
                    [
                        c
                        for c, data in self.components_data.items()
                        if data["type"] == "resource"
                    ]
                ),
                "simulation_duration": max(
                    [
                        action["time"]
                        for comp in self.components_data.values()
                        for action in comp["actions"]
                    ]
                ),
            },
            "efficiency": {
                "system_efficiency": np.mean(
                    list(self.calculate_component_efficiency().values())
                ),
                "component_efficiency": self.calculate_component_efficiency(),
            },
            "processing": {
                "avg_processing_times": {
                    comp_id: data["mean"]
                    for comp_id, data in self.calculate_processing_time().items()
                },
                "total_processing_time": sum(
                    data["mean"] * data["count"]
                    for data in self.calculate_processing_time().values()
                ),
            },
            "bottlenecks": self.get_component_bottlenecks(),
        }

        return report

    def get_component_processing_time_chart_data(self) -> Dict[str, Any]:
        """
        Extract and format component processing time data for line chart visualization.

        This method tracks the processing time of each component over time, providing
        data suitable for creating a line chart where each component is represented
        as a line showing its processing time.

        Returns:
            Dictionary with component processing time data formatted for line charts
        """
        if self.df is None:
            return {"error": "No data loaded"}

        # Initialize result structure
        result = {
            "components": {},
            "time_range": self.get_time_range(),
            "component_types": {},
            "chart_data": {"labels": [], "datasets": []},
        }

        # Get unique components
        unique_components = self.df[
            ["component_id", "component_type"]
        ].drop_duplicates()

        # Initialize data structure for each component
        for _, row in unique_components.iterrows():
            comp_id = row["component_id"]
            comp_type = row["component_type"]

            result["components"][comp_id] = {
                "type": comp_type,
                "processing_data": [],
                "name": f"{comp_type} ({comp_id[:8]}...)",
            }

            # Track component types
            if comp_type not in result["component_types"]:
                result["component_types"][comp_type] = []
            result["component_types"][comp_type].append(comp_id)

        # Process data for each component
        for comp_id in result["components"]:
            # Filter data for this component
            comp_data = self.df[self.df["component_id"] == comp_id].sort_values("time")

            # Track processing times based on component type
            comp_type = result["components"][comp_id]["type"]

            if comp_type == "generator":
                # For generators, track time between GENERATE actions
                generate_actions = comp_data[comp_data["action"] == "GENERATE"]

                for i, row in generate_actions.iterrows():
                    # Extract out_time from values if available
                    out_time = None
                    if isinstance(row["values"], dict) and "out_time" in row["values"]:
                        out_time = row["values"]["out_time"]

                    # Add data point
                    result["components"][comp_id]["processing_data"].append(
                        {
                            "time": row["time"],
                            "processing_time": out_time - row["time"]
                            if out_time
                            else 0,
                            "container_id": row["PDV"].get("containerId")
                            if isinstance(row["PDV"], dict)
                            else None,
                            "action": row["action"],
                        }
                    )

            elif comp_type == "resource":
                # For resources, track ENTER to Exit time
                # Create a dictionary to track enter times for containers
                container_enter_times = {}

                for _, row in comp_data.iterrows():
                    # Get container ID
                    container_id = None
                    if isinstance(row["PDV"], dict) and "containerId" in row["PDV"]:
                        container_id = row["PDV"]["containerId"]

                    if container_id:
                        if row["action"] == "ENTER":
                            # Record enter time for this container
                            container_enter_times[container_id] = row["time"]
                        elif (
                            row["action"] == "Exit"
                            and container_id in container_enter_times
                        ):
                            # Calculate processing time
                            enter_time = container_enter_times[container_id]
                            exit_time = row["time"]
                            processing_time = exit_time - enter_time

                            # Add data point
                            result["components"][comp_id]["processing_data"].append(
                                {
                                    "time": enter_time,  # Use enter time as the reference point
                                    "processing_time": processing_time,
                                    "container_id": container_id,
                                    "action": "PROCESS",  # Custom action to represent processing
                                    "exit_time": exit_time,
                                }
                            )

                            # Remove from tracking
                            del container_enter_times[container_id]

                    # Also track in_time and out_time from values
                    in_time = None
                    out_time = None
                    if isinstance(row["values"], dict):
                        if "in_time" in row["values"]:
                            in_time = row["values"]["in_time"]
                        if "out_time" in row["values"]:
                            out_time = row["values"]["out_time"]

                    # If both in_time and out_time are available, calculate processing time
                    if in_time is not None and out_time is not None:
                        processing_time = out_time - in_time

                        # Add data point if not already tracked through ENTER/Exit
                        if container_id and container_id not in container_enter_times:
                            result["components"][comp_id]["processing_data"].append(
                                {
                                    "time": in_time,
                                    "processing_time": processing_time,
                                    "container_id": container_id,
                                    "action": "PROCESS_VALUES",  # Custom action to represent processing from values
                                    "exit_time": out_time,
                                }
                            )

            # Sort processing data by time
            result["components"][comp_id]["processing_data"].sort(
                key=lambda x: x["time"]
            )

            # Calculate average processing time
            processing_times = [
                entry["processing_time"]
                for entry in result["components"][comp_id]["processing_data"]
            ]
            result["components"][comp_id]["avg_processing_time"] = (
                sum(processing_times) / len(processing_times) if processing_times else 0
            )

        # Prepare chart data in a format suitable for line charts
        # Create a unified timeline for all components
        all_times = []
        for comp_id, comp_data in result["components"].items():
            for entry in comp_data["processing_data"]:
                all_times.append(entry["time"])

        # Sort and deduplicate times
        all_times = sorted(list(set(all_times)))
        result["chart_data"]["labels"] = all_times

        # Create datasets for each component
        for comp_id, comp_data in result["components"].items():
            # Create a mapping of time to processing time for this component
            time_to_processing = {
                entry["time"]: entry["processing_time"]
                for entry in comp_data["processing_data"]
            }

            # Create dataset
            dataset = {
                "label": comp_data["name"],
                "data": [time_to_processing.get(time, None) for time in all_times],
                "component_id": comp_id,
                "component_type": comp_data["type"],
            }

            result["chart_data"]["datasets"].append(dataset)

        # Add a simplified format for direct chart use
        result["line_chart_data"] = {"components": [], "timeline": all_times}

        # Group by component type
        for comp_type, comp_ids in result["component_types"].items():
            component_group = {"type": comp_type, "components": []}

            for comp_id in comp_ids:
                comp_data = result["components"][comp_id]

                # Create a mapping of time to processing time
                time_to_processing = {
                    entry["time"]: entry["processing_time"]
                    for entry in comp_data["processing_data"]
                }

                # Create component data
                component = {
                    "id": comp_id,
                    "name": comp_data["name"],
                    "processing_times": [
                        time_to_processing.get(time, 0) for time in all_times
                    ],
                    "avg_processing_time": comp_data["avg_processing_time"],
                }

                component_group["components"].append(component)

            result["line_chart_data"]["components"].append(component_group)

        return result
