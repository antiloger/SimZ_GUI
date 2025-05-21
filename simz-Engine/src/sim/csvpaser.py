from collections import Counter
import json
import os
import pandas as pd
import duckdb
from typing import Dict, Any, Optional, List, Set, Tuple, Union
import numpy as np


def log_console(message: str, logger_console: bool = False) -> None:
    """
    Utility function to control console output.

    Args:
        message: The message to print
        logger_console: Whether to print the message to the console (default: False)
    """
    if logger_console:
        print(message)


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
            # First, read the CSV file without parsing the JSON columns
            self.df = pd.read_csv(self.csv_filepath)

            # Define a safer JSON parsing function
            def safe_parse_json(text):
                if not isinstance(text, str):
                    return text

                try:
                    # Try direct json.loads first
                    return json.loads(text)
                except json.JSONDecodeError:
                    try:
                        # Try replacing single quotes with double quotes
                        return json.loads(text.replace("'", '"'))
                    except json.JSONDecodeError:
                        try:
                            # Try using ast.literal_eval as a fallback
                            import ast

                            return ast.literal_eval(text)
                        except (ValueError, SyntaxError):
                            # If all parsing attempts fail, return the original string
                            print(
                                f"Warning: Failed to parse JSON-like string: {text[:50]}..."
                            )
                            return text

            # Apply the safe parsing function to both columns
            if "values" in self.df.columns:
                self.df["values"] = self.df["values"].apply(safe_parse_json)

            if "PDV" in self.df.columns:
                self.df["PDV"] = self.df["PDV"].apply(safe_parse_json)

            # Extract component IDs and types for easier access
            self.components_data = self._extract_components_data()
            self.containers_data = self._extract_containers_data()

            # Register the DataFrame as a view in DuckDB
            self.conn.register("csv_data", self.df)
            print(f"Data loaded successfully: {len(self.df)} rows")
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback

            traceback.print_exc()  # Print the full traceback for debugging
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

    def get_unique_container_ids(self) -> List[str]:
        """
        Get a list of all unique container IDs in the CSV data.
        Uses a more robust approach to extract container IDs from PDV.

        Returns:
            List of unique container IDs
        """
        if self.df is None:
            return []

        try:
            # Use a more robust query to extract container IDs
            query = """
            WITH extracted_data AS (
                SELECT
                    CASE
                        WHEN PDV LIKE '%"containerId": "%' THEN regexp_extract(PDV, '"containerId": "([^"]+)"', 1)
                        WHEN PDV LIKE "%'containerId': '%" THEN regexp_extract(PDV, "'containerId': '([^']+)'", 1)
                        ELSE NULL
                    END as container_id
                FROM csv_data
                WHERE PDV IS NOT NULL
            )
            SELECT DISTINCT container_id
            FROM extracted_data
            WHERE container_id IS NOT NULL
            """

            result = self.conn.execute(query).fetchdf()
            container_ids = result["container_id"].tolist()
            log_console(
                f"Found {len(container_ids)} unique container IDs using direct query",
                logger_console=False,
            )
            return container_ids

        except Exception as e:
            log_console(
                f"Error getting unique container IDs: {e}", logger_console=False
            )

            # Fallback method using Python
            container_ids = set()
            for _, row in self.df.iterrows():
                if isinstance(row.get("PDV"), dict) and "containerId" in row["PDV"]:
                    container_ids.add(row["PDV"]["containerId"])

            log_console(
                f"Found {len(container_ids)} unique container IDs using fallback method",
                logger_console=False,
            )
            return list(container_ids)

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
            log_console(f"Query error: {e}", logger_console=False)
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
        Enhanced with better error handling for malformed JSON.

        Returns:
            Dictionary with container count statistics
        """
        if self.df is None:
            return {"error": "No data loaded", "total_containers": 0}

        try:
            # First, ensure we can extract container IDs properly
            log_console(
                "Extracting container IDs from CSV data...", logger_console=False
            )

            # Query to get basic container statistics with better error handling
            # Use string replacement to handle both single and double quotes in JSON
            query = """
            WITH extracted_data AS (
                SELECT
                    CASE
                        WHEN PDV LIKE '%"containerId": "%' THEN regexp_extract(PDV, '"containerId": "([^"]+)"', 1)
                        WHEN PDV LIKE "%'containerId': '%" THEN regexp_extract(PDV, "'containerId': '([^']+)'", 1)
                        ELSE NULL
                    END as container_id,
                    time
                FROM csv_data
                WHERE PDV IS NOT NULL
            )
            SELECT
                container_id,
                COUNT(*) as occurrence_count,
                MIN(time) as first_seen,
                MAX(time) as last_seen,
                MAX(time) - MIN(time) as lifespan
            FROM extracted_data
            WHERE container_id IS NOT NULL
            GROUP BY container_id
            ORDER BY occurrence_count DESC
            """

            container_stats = self.conn.execute(query).fetchdf()

            # Further process the results to get component and action counts
            container_details = []

            for _, container in container_stats.iterrows():
                try:
                    container_id = container["container_id"]
                    if container_id is None:
                        continue

                    # Query to get unique components for this container using the same extraction method
                    components_query = f"""
                    SELECT
                        DISTINCT component_id
                    FROM csv_data
                    WHERE (PDV LIKE '%"containerId": "{container_id}"%' OR PDV LIKE "%'containerId': '{container_id}'%")
                    """
                    components = self.conn.execute(components_query).fetchdf()

                    # Query to get unique actions for this container using the same extraction method
                    actions_query = f"""
                    SELECT
                        DISTINCT action
                    FROM csv_data
                    WHERE (PDV LIKE '%"containerId": "{container_id}"%' OR PDV LIKE "%'containerId': '{container_id}'%")
                    """
                    actions = self.conn.execute(actions_query).fetchdf()

                    # Safely convert values to integers with fallbacks
                    try:
                        occurrence_count = int(container["occurrence_count"])
                    except (ValueError, TypeError):
                        occurrence_count = 0

                    try:
                        first_seen = int(container["first_seen"])
                    except (ValueError, TypeError):
                        first_seen = 0

                    try:
                        last_seen = int(container["last_seen"])
                    except (ValueError, TypeError):
                        last_seen = 0

                    try:
                        lifespan = int(container["lifespan"])
                    except (ValueError, TypeError):
                        lifespan = 0

                    container_details.append(
                        {
                            "container_id": container_id,
                            "occurrence_count": occurrence_count,
                            "first_seen": first_seen,
                            "last_seen": last_seen,
                            "lifespan": lifespan,
                            "component_interactions": components[
                                "component_id"
                            ].tolist(),
                            "component_interaction_count": len(components),
                            "actions": actions["action"].tolist(),
                            "action_count": len(actions),
                        }
                    )
                except Exception as e:
                    log_console(
                        f"Warning: Error processing container: {e}",
                        logger_console=False,
                    )
                    continue

            # Create a safe result dictionary with proper fallbacks
            result = {
                "total_containers": len(container_details),
                "containers": container_details,
            }

            # Safely add most occurrences container
            if container_details:
                result["container_with_most_occurrences"] = container_details[0]
            else:
                result["container_with_most_occurrences"] = None

            # Safely add longest lifespan container
            if container_details:
                try:
                    result["container_with_longest_lifespan"] = max(
                        container_details, key=lambda x: x["lifespan"]
                    )
                except Exception:
                    result["container_with_longest_lifespan"] = None
            else:
                result["container_with_longest_lifespan"] = None

            return result

        except Exception as e:
            log_console(f"Error in count_containers_duckdb: {e}", logger_console=False)
            return {"error": str(e), "total_containers": 0}

    def _extract_components_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract component data from the DataFrame.
        Enhanced to handle dynamic data structures and missing fields.
        """
        components = {}
        for _, row in self.df.iterrows():
            # Safely extract component ID and type with fallbacks
            comp_id = row.get("component_id", "unknown")
            comp_type = row.get("component_type", "unknown")

            if not comp_id or comp_id == "unknown":
                continue  # Skip rows without valid component ID

            # Initialize component entry if not exists
            if comp_id not in components:
                components[comp_id] = {
                    "type": comp_type,
                    "actions": [],
                    "container_interactions": set(),
                    "processing_times": [],
                    "metrics": {},  # For storing calculated metrics
                }

            # Add action to the component with safe extraction
            action_data = {
                "time": row.get("time", 0),
                "action": row.get("action", "unknown"),
            }

            # Safely handle values field
            if "values" in row and row["values"] is not None:
                if isinstance(row["values"], dict):
                    action_data["values"] = row["values"]
                elif isinstance(row["values"], str):
                    # Try to parse string as JSON if it's not already a dict
                    try:
                        action_data["values"] = json.loads(
                            row["values"].replace("'", '"')
                        )
                    except (json.JSONDecodeError, AttributeError):
                        action_data["values"] = {}
                else:
                    action_data["values"] = {}
            else:
                action_data["values"] = {}

            # Add any additional fields that might be present
            for key, value in row.items():
                if key not in [
                    "time",
                    "component_id",
                    "component_type",
                    "action",
                    "values",
                    "PDV",
                ]:
                    if value is not None:
                        action_data[key] = value

            components[comp_id]["actions"].append(action_data)

            # Track container interactions with safe extraction
            if "PDV" in row and row["PDV"] is not None:
                if isinstance(row["PDV"], dict) and "containerId" in row["PDV"]:
                    components[comp_id]["container_interactions"].add(
                        row["PDV"]["containerId"]
                    )
                elif isinstance(row["PDV"], str):
                    # Try to parse string as JSON if it's not already a dict
                    try:
                        pdv_data = json.loads(row["PDV"].replace("'", '"'))
                        if isinstance(pdv_data, dict) and "containerId" in pdv_data:
                            components[comp_id]["container_interactions"].add(
                                pdv_data["containerId"]
                            )
                    except (json.JSONDecodeError, AttributeError):
                        pass

        return components

    def _extract_containers_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract container data from the DataFrame.
        Enhanced to handle dynamic data structures and missing fields.
        """
        containers = {}
        for _, row in self.df.iterrows():
            pdv_data = None

            # Safely extract PDV data
            if "PDV" in row and row["PDV"] is not None:
                if isinstance(row["PDV"], dict):
                    pdv_data = row["PDV"]
                elif isinstance(row["PDV"], str):
                    # Try to parse string as JSON if it's not already a dict
                    try:
                        pdv_data = json.loads(row["PDV"].replace("'", '"'))
                    except (json.JSONDecodeError, AttributeError):
                        pdv_data = None

            # Skip if no valid PDV data or no containerId
            if (
                not pdv_data
                or not isinstance(pdv_data, dict)
                or "containerId" not in pdv_data
            ):
                continue

            container_id = pdv_data["containerId"]

            # Initialize container entry if not exists
            if container_id not in containers:
                containers[container_id] = {
                    "types": {},
                    "components_interacted": set(),
                    "timeline": [],
                    "first_seen": row.get("time", 0),
                    "last_seen": row.get("time", 0),
                    "attributes": {},  # For storing extracted attributes
                }
            else:
                # Update last_seen time if this row has a later timestamp
                if (
                    "time" in row
                    and row["time"] > containers[container_id]["last_seen"]
                ):
                    containers[container_id]["last_seen"] = row["time"]

            # Add component to the container's interacted components (with safe extraction)
            if "component_id" in row and row["component_id"]:
                containers[container_id]["components_interacted"].add(
                    row["component_id"]
                )

            # Add to timeline with safe extraction
            timeline_entry = {
                "time": row.get("time", 0),
                "component_id": row.get("component_id", "unknown"),
                "action": row.get("action", "unknown"),
            }

            # Add values data if available
            if "values" in row and isinstance(row["values"], dict):
                timeline_entry["values"] = row["values"]

            containers[container_id]["timeline"].append(timeline_entry)

            # Extract types data with safe handling
            if "types" in pdv_data and isinstance(pdv_data["types"], dict):
                for type_id, type_data in pdv_data["types"].items():
                    if type_id not in containers[container_id]["types"]:
                        containers[container_id]["types"][type_id] = type_data

                        # Extract attributes for easier access
                        if isinstance(type_data, dict) and "attributes" in type_data:
                            type_name = type_data.get("typeName", "unknown_type")
                            if type_name not in containers[container_id]["attributes"]:
                                containers[container_id]["attributes"][type_name] = {}

                            # Extract attribute values
                            if isinstance(type_data["attributes"], dict):
                                for attr_name, attr_data in type_data[
                                    "attributes"
                                ].items():
                                    if (
                                        isinstance(attr_data, dict)
                                        and "value" in attr_data
                                    ):
                                        containers[container_id]["attributes"][
                                            type_name
                                        ][attr_name] = attr_data["value"]

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
                # First try to use IN and OUT actions for efficiency
                ins = action_counts.get("IN", 0)
                outs = action_counts.get("OUT", 0)

                # If we have IN/OUT actions, use those for efficiency
                if ins > 0:
                    productive_actions = outs
                    total_actions = ins
                else:
                    # Fallback to ENTER/Exit if no IN/OUT actions
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

    def calculate_all_processing_times(self) -> Dict[str, float]:
        """
        Calculate overall processing time metrics across all components.

        Returns:
            Dictionary with overall processing time statistics
        """
        # Get processing times for all components
        all_component_times = self.calculate_processing_time()

        # Collect all processing times into a single list
        all_times = []
        for comp_data in all_component_times.values():
            if "count" in comp_data and comp_data["count"] > 0:
                # If we have individual times, add them
                if "times" in comp_data and comp_data["times"]:
                    all_times.extend(comp_data["times"])

        # Calculate statistics if we have times
        if all_times:
            return {
                "mean": round(np.mean(all_times), 2),
                "median": round(np.median(all_times), 2),
                "min": round(min(all_times), 2),
                "max": round(max(all_times), 2),
                "count": len(all_times),
                "times": all_times,
            }
        else:
            return {"mean": 0, "median": 0, "min": 0, "max": 0, "count": 0, "times": []}

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
                # Prioritize IN and OUT actions for processing time calculation
                # as per user requirements
                in_out_pairs = []
                in_input_counts = {}  # Track input_count for IN actions
                in_container_ids = {}  # Track container IDs for IN actions

                # First pass: collect all IN actions with their input_count and container ID
                for action in sorted_actions:
                    if action["action"] == "IN":
                        # Get input_count if available
                        input_count = None
                        container_id = None

                        if isinstance(action.get("values"), dict):
                            input_count = action["values"].get("input_count")

                        # Try to extract container ID from PDV if available
                        pdv = action.get("PDV", {})
                        if isinstance(pdv, dict) and "containerId" in pdv:
                            container_id = pdv["containerId"]

                        # Store by both input_count and container_id for better matching
                        if input_count is not None:
                            in_input_counts[input_count] = action

                        if container_id is not None:
                            in_container_ids[container_id] = action

                # Second pass: match OUT actions with IN actions
                for action in sorted_actions:
                    if action["action"] == "OUT":
                        matched = False

                        # Try to match by input_count first
                        input_count = None
                        if isinstance(action.get("values"), dict):
                            input_count = action["values"].get("input_count")

                        if input_count is not None and input_count in in_input_counts:
                            in_action = in_input_counts[input_count]
                            # Only pair if OUT comes after IN
                            if action["time"] > in_action["time"]:
                                in_out_pairs.append((in_action, action))
                                # Remove from tracking to avoid duplicate matches
                                del in_input_counts[input_count]
                                matched = True

                        # If not matched by input_count, try to match by container ID
                        if not matched:
                            container_id = None
                            pdv = action.get("PDV", {})
                            if isinstance(pdv, dict) and "containerId" in pdv:
                                container_id = pdv["containerId"]

                            if (
                                container_id is not None
                                and container_id in in_container_ids
                            ):
                                in_action = in_container_ids[container_id]
                                # Only pair if OUT comes after IN
                                if action["time"] > in_action["time"]:
                                    in_out_pairs.append((in_action, action))
                                    # Remove from tracking to avoid duplicate matches
                                    del in_container_ids[container_id]

                # Calculate processing time for IN/OUT pairs
                in_out_times = [
                    out_action["time"] - in_action["time"]
                    for in_action, out_action in in_out_pairs
                ]

                # If we found IN/OUT pairs, use those times
                if in_out_times:
                    log_console(
                        f"Using {len(in_out_times)} IN/OUT pairs for processing time calculation for {comp_id}",
                        logger_console=False,
                    )
                    times = in_out_times
                else:
                    # Fallback to ENTER/Exit pairs if no IN/OUT pairs were found
                    log_console(
                        f"No IN/OUT pairs found for {comp_id}, falling back to ENTER/Exit pairs",
                        logger_console=False,
                    )
                    enter_exit_pairs = []
                    current_enter = None

                    for action in sorted_actions:
                        if action["action"] == "ENTER":
                            current_enter = action
                        elif action["action"] == "Exit" and current_enter:
                            enter_exit_pairs.append((current_enter, action))
                            current_enter = None

                    # Calculate processing time for ENTER/Exit pairs
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
                    "times": times,  # Store the individual times for aggregation
                }
            else:
                processing_times[comp_id] = {
                    "mean": 0,
                    "median": 0,
                    "min": 0,
                    "max": 0,
                    "count": 0,
                    "times": [],
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
                # First try to use IN and OUT actions for active time
                in_input_counts = {}  # Track input_count for IN actions

                # First pass: collect all IN actions with their input_count
                for action in sorted_actions:
                    if action["action"] == "IN":
                        # Get input_count if available
                        input_count = None
                        if isinstance(action.get("values"), dict):
                            input_count = action["values"].get("input_count")

                        if input_count is not None:
                            in_input_counts[input_count] = action

                # Second pass: match OUT actions with IN actions by input_count
                in_out_active_time = 0
                for action in sorted_actions:
                    if action["action"] == "OUT":
                        # Get input_count if available
                        input_count = None
                        if isinstance(action.get("values"), dict):
                            input_count = action["values"].get("input_count")

                        # If we have a matching IN action with the same input_count
                        if input_count is not None and input_count in in_input_counts:
                            in_action = in_input_counts[input_count]
                            # Only pair if OUT comes after IN
                            if action["time"] > in_action["time"]:
                                in_out_active_time += action["time"] - in_action["time"]
                                # Remove from tracking to avoid duplicate matches
                                del in_input_counts[input_count]

                # If we found IN/OUT pairs, use that active time
                if in_out_active_time > 0:
                    active_time = in_out_active_time
                else:
                    # Fallback to ENTER/Exit pairs if no IN/OUT pairs were found
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

    def get_container_count_timeline(self) -> Dict[str, Any]:
        """
        Calculate the number of containers being processed at each time point in the simulation.

        This method tracks when containers enter and exit processing (using IN and OUT actions)
        to determine how many containers are in the system at each time point.

        Returns:
            Dictionary with timeline data showing container counts at each time point
        """
        if self.df is None:
            return {"error": "No data loaded"}

        print("Generating container count timeline data...")

        # Get time range
        time_range = self.get_time_range()
        min_time = time_range.get("min_time", 0)
        max_time = time_range.get("max_time", 100)

        # Create timeline with appropriate time steps
        # If the simulation is very long, use larger time steps
        time_span = max_time - min_time
        if time_span > 1000:
            # Use larger time steps for very long simulations
            step_size = max(1, time_span // 500)  # Limit to ~500 data points
        else:
            step_size = 1

        timeline = list(range(min_time, max_time + 1, step_size))

        # Initialize container count at each time point
        container_counts = {t: 0 for t in timeline}

        # Track container entry and exit events
        container_events = []

        # Process all container events from the CSV data
        for _, row in self.df.iterrows():
            # Skip rows without PDV or containerId
            if not isinstance(row["PDV"], dict) or "containerId" not in row["PDV"]:
                continue

            container_id = row["PDV"]["containerId"]
            action = row["action"]
            time = row["time"]

            # Track when containers enter processing (IN action)
            if action == "IN":
                container_events.append(
                    {"time": time, "event": "enter", "container_id": container_id}
                )

            # Track when containers exit processing (OUT action)
            elif action == "OUT":
                container_events.append(
                    {"time": time, "event": "exit", "container_id": container_id}
                )

        # Sort events by time
        container_events.sort(key=lambda x: x["time"])

        # Process events to calculate container count at each time point
        active_containers = set()
        last_count = 0
        last_time = min_time

        for event in container_events:
            time = event["time"]
            container_id = event["container_id"]

            # Update counts for all time points between last_time and current time
            for t in timeline:
                if last_time <= t < time:
                    container_counts[t] = len(active_containers)

            # Update active containers based on event type
            if event["event"] == "enter":
                active_containers.add(container_id)
            elif event["event"] == "exit" and container_id in active_containers:
                active_containers.remove(container_id)

            last_time = time
            last_count = len(active_containers)

        # Fill in remaining time points after the last event
        for t in timeline:
            if t >= last_time:
                container_counts[t] = last_count

        # Format data for chart
        data_points = [{"x": t, "y": container_counts[t]} for t in timeline]

        return {
            "timeline": timeline,
            "container_counts": container_counts,
            "data_points": data_points,
            "max_count": max(container_counts.values()) if container_counts else 0,
        }

    def get_gentype_distribution(self) -> Dict[str, Any]:
        """
        Analyze the distribution of GenTypes in the simulation.

        This method identifies all unique containers and their GenTypes during the simulation
        and calculates their percentage distribution. It counts each container only once
        to provide an accurate representation of the GenType distribution.

        Returns:
            Dictionary with GenType distribution data
        """
        if self.df is None:
            return {"error": "No data loaded"}

        print("Analyzing GenType distribution...")

        # Track unique containers and their GenTypes
        container_gentypes = {}  # Maps container IDs to their GenType

        # Process all rows to identify unique containers and their GenTypes
        for _, row in self.df.iterrows():
            # Skip rows without PDV
            if not isinstance(row["PDV"], dict) or "types" not in row["PDV"]:
                continue

            # Get container ID
            container_id = row["PDV"].get("containerId")
            if not container_id:
                continue

            # Extract types data
            types_data = row["PDV"]["types"]

            # Handle different formats of types data
            if isinstance(types_data, dict):
                # Format: {"type1": {...}, "type2": {...}}
                for type_name, type_data in types_data.items():
                    # Extract the actual type name from the data if available
                    if isinstance(type_data, dict) and "typeName" in type_data:
                        actual_type_name = type_data["typeName"]
                    else:
                        actual_type_name = type_name

                    # Store the GenType for this container
                    container_gentypes[container_id] = actual_type_name
                    # We only need one GenType per container, so break after finding the first one
                    break
            elif isinstance(types_data, list):
                # Format: [{"name": "type1", ...}, {"name": "type2", ...}]
                for type_item in types_data:
                    if isinstance(type_item, dict):
                        # Try different possible field names for type name
                        type_name = type_item.get("name") or type_item.get("typeName")
                        if type_name:
                            # Store the GenType for this container
                            container_gentypes[container_id] = type_name
                            # We only need one GenType per container, so break after finding the first one
                            break

        # Count GenTypes based on unique containers
        gentype_counts = {}
        for gentype in container_gentypes.values():
            if gentype not in gentype_counts:
                gentype_counts[gentype] = 0
            gentype_counts[gentype] += 1

        # Calculate total count of unique containers
        total_count = len(container_gentypes)

        # Calculate percentages
        gentype_percentages = {}
        for type_name, count in gentype_counts.items():
            percentage = (count / total_count * 100) if total_count > 0 else 0
            gentype_percentages[type_name] = round(percentage, 2)

        # Format data for pie chart
        data_points = [
            {"x": type_name, "y": percentage}
            for type_name, percentage in gentype_percentages.items()
        ]

        print(f"Found {total_count} unique containers with the following GenType distribution:")
        for type_name, count in gentype_counts.items():
            print(f"  {type_name}: {count} containers ({gentype_percentages[type_name]}%)")

        return {
            "counts": gentype_counts,
            "percentages": gentype_percentages,
            "data_points": data_points,
            "total_count": total_count,
        }

    def get_component_processing_time_chart_data(self) -> Dict[str, Any]:
        """
        Extract and format component processing time data for line chart visualization.

        This method tracks the processing time of each component over time, providing
        data suitable for creating a line chart where each component is represented
        as a line showing its processing time.

        Prioritizes IN/OUT action pairs for processing time calculation as per requirements.

        Creates a continuous timeline showing component processing states.

        Returns:
            Dictionary with component processing time data formatted for line charts
        """
        if self.df is None:
            return {"error": "No data loaded"}

        print("Generating component processing time chart data...")

        # Initialize result structure
        result = {
            "components": {},
            "time_range": self.get_time_range(),
            "component_types": {},
            "chart_data": {"labels": [], "datasets": []},
            "continuous_data": {},  # For continuous timeline representation
        }

        # Get unique components
        unique_components = self.df[
            ["component_id", "component_type"]
        ].drop_duplicates()

        print(f"Found {len(unique_components)} unique components in the CSV data")

        # Initialize data structure for each component
        for _, row in unique_components.iterrows():
            comp_id = row["component_id"]
            comp_type = row["component_type"]

            # Use a more readable name format
            if len(comp_id) > 8:
                display_name = f"{comp_type} ({comp_id[:8]}...)"
            else:
                display_name = f"{comp_type} ({comp_id})"

            result["components"][comp_id] = {
                "type": comp_type,
                "processing_data": [],
                "name": display_name,
            }

            print(
                f"Initialized component: {display_name} (ID: {comp_id}, Type: {comp_type})"
            )

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
                # IMPORTANT: For resource components, we MUST use IN and OUT actions for processing time
                # as per user requirements
                print(f"Processing resource component: {comp_id}")

                # Create dictionaries to track container processing
                container_in_times = {}
                container_in_input_counts = {}

                # Count IN and OUT actions for debugging
                in_count = len(comp_data[comp_data["action"] == "IN"])
                out_count = len(comp_data[comp_data["action"] == "OUT"])
                print(
                    f"Component {comp_id} has {in_count} IN actions and {out_count} OUT actions"
                )

                # First pass: collect all IN actions with their input_count and container_id
                for _, row in comp_data.iterrows():
                    if row["action"] != "IN":
                        continue

                    # Get container ID
                    container_id = None
                    if isinstance(row["PDV"], dict) and "containerId" in row["PDV"]:
                        container_id = row["PDV"]["containerId"]
                    else:
                        continue  # Skip if no container ID

                    # Get input_count if available
                    input_count = None
                    if isinstance(row["values"], dict):
                        input_count = row["values"].get("input_count")

                    # Record IN time by both container_id and input_count for better matching
                    container_in_times[container_id] = row["time"]

                    if input_count is not None:
                        container_in_input_counts[(container_id, input_count)] = row[
                            "time"
                        ]
                        print(
                            f"Recorded IN action for container {container_id} with input_count {input_count} at time {row['time']}"
                        )
                    else:
                        print(
                            f"Recorded IN action for container {container_id} without input_count at time {row['time']}"
                        )

                # Second pass: match OUT actions with IN actions
                matched_pairs = 0
                for _, row in comp_data.iterrows():
                    if row["action"] != "OUT":
                        continue

                    # Get container ID
                    container_id = None
                    if isinstance(row["PDV"], dict) and "containerId" in row["PDV"]:
                        container_id = row["PDV"]["containerId"]
                    else:
                        continue  # Skip if no container ID

                    # Get input_count if available
                    input_count = None
                    if isinstance(row["values"], dict):
                        input_count = row["values"].get("input_count")

                    # Try to match by container_id and input_count first (more precise)
                    matched = False
                    if (
                        input_count is not None
                        and (container_id, input_count) in container_in_input_counts
                    ):
                        in_time = container_in_input_counts[(container_id, input_count)]
                        out_time = row["time"]

                        # Only calculate if OUT comes after IN
                        if out_time > in_time:
                            processing_time = out_time - in_time
                            matched_pairs += 1

                            print(
                                f"Matched OUT action for container {container_id} with input_count {input_count} - processing time: {processing_time}"
                            )

                            # Add data point
                            result["components"][comp_id]["processing_data"].append(
                                {
                                    "time": in_time,  # Use IN time as the reference point
                                    "processing_time": processing_time,
                                    "container_id": container_id,
                                    "action": "PROCESS",  # Custom action to represent processing
                                    "exit_time": out_time,
                                    "input_count": input_count,
                                }
                            )

                            # Remove from tracking to avoid duplicate matches
                            del container_in_input_counts[(container_id, input_count)]
                            if container_id in container_in_times:
                                del container_in_times[container_id]

                            matched = True

                    # Fallback to just container_id if no input_count match
                    if not matched and container_id in container_in_times:
                        in_time = container_in_times[container_id]
                        out_time = row["time"]

                        # Only calculate if OUT comes after IN
                        if out_time > in_time:
                            processing_time = out_time - in_time
                            matched_pairs += 1

                            print(
                                f"Matched OUT action for container {container_id} by container ID only - processing time: {processing_time}"
                            )

                            # Add data point
                            result["components"][comp_id]["processing_data"].append(
                                {
                                    "time": in_time,  # Use IN time as the reference point
                                    "processing_time": processing_time,
                                    "container_id": container_id,
                                    "action": "PROCESS",  # Custom action to represent processing
                                    "exit_time": out_time,
                                }
                            )

                            # Remove from tracking
                            del container_in_times[container_id]

                print(
                    f"Successfully matched {matched_pairs} IN/OUT pairs for component {comp_id}"
                )

                # If no IN/OUT pairs were found, fallback to ENTER/Exit
                if not result["components"][comp_id]["processing_data"]:
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

        # Create a continuous timeline for all simulation times
        time_range = result["time_range"]
        min_time = time_range.get("min_time", 0)
        max_time = time_range.get("max_time", 100)

        # Create a more granular timeline for better visualization
        all_times = list(range(min_time, max_time + 1))
        result["chart_data"]["labels"] = all_times

        print(f"Created continuous timeline from {min_time} to {max_time}")

        # Track component processing states over time
        component_states = {}

        # Initialize component states
        for comp_id, comp_data in result["components"].items():
            component_states[comp_id] = {
                "name": comp_data["name"],
                "type": comp_data["type"],
                "processing_state": [0] * len(all_times),  # 0 = idle, 1 = processing
                "active_containers": {},  # Track containers being processed at each time
            }

        # Fill in processing states based on IN/OUT pairs
        for comp_id, comp_data in result["components"].items():
            print(f"Creating continuous timeline for component {comp_id}")

            # Process each IN/OUT pair to mark active processing periods
            for entry in comp_data["processing_data"]:
                in_time = entry["time"]
                out_time = entry.get("exit_time", in_time + entry["processing_time"])
                container_id = entry.get("container_id", "unknown")

                # Find indices in the timeline
                try:
                    start_idx = all_times.index(in_time)
                    # Ensure out_time is within the timeline range
                    end_idx = min(
                        all_times.index(out_time)
                        if out_time in all_times
                        else len(all_times) - 1,
                        len(all_times) - 1,
                    )

                    # Mark the component as processing during this period
                    for i in range(start_idx, end_idx + 1):
                        component_states[comp_id]["processing_state"][i] = 1

                        # Track which container is being processed
                        if i not in component_states[comp_id]["active_containers"]:
                            component_states[comp_id]["active_containers"][i] = []
                        component_states[comp_id]["active_containers"][i].append(
                            container_id
                        )

                    print(
                        f"  Marked processing from time {in_time} to {out_time} for container {container_id}"
                    )
                except ValueError as e:
                    print(
                        f"  Warning: Could not mark processing time for {comp_id}: {e}"
                    )

        # Create datasets for continuous processing state visualization
        for comp_id, state_data in component_states.items():
            # Create dataset for processing state (0 or 1)
            state_dataset = {
                "label": state_data["name"],
                "data": state_data["processing_state"],
                "component_id": comp_id,
                "component_type": state_data["type"],
            }

            result["chart_data"]["datasets"].append(state_dataset)

        # Store the continuous data for additional charts
        result["continuous_data"] = component_states

        # Create a new format for the continuous processing time chart
        result["continuous_chart_data"] = {"timeline": all_times, "components": []}

        # Group by component type for the continuous chart
        for comp_type, comp_ids in result["component_types"].items():
            component_group = {"type": comp_type, "components": []}

            for comp_id in comp_ids:
                if comp_id in component_states:
                    state_data = component_states[comp_id]
                    comp_data = result["components"][comp_id]

                    # Create component data with continuous processing state
                    component = {
                        "id": comp_id,
                        "name": state_data["name"],
                        "processing_state": state_data["processing_state"],
                        "avg_processing_time": comp_data.get("avg_processing_time", 0),
                    }

                    component_group["components"].append(component)

            result["continuous_chart_data"]["components"].append(component_group)

        # Also keep the original discrete data points for reference
        # Create a unified timeline for all discrete data points
        discrete_times = []
        for comp_id, comp_data in result["components"].items():
            for entry in comp_data["processing_data"]:
                discrete_times.append(entry["time"])

        # Sort and deduplicate discrete times
        discrete_times = sorted(list(set(discrete_times)))
        result["discrete_chart_data"] = {"timeline": discrete_times, "components": []}

        # Group by component type for the discrete chart
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
                        time_to_processing.get(time, 0) for time in discrete_times
                    ],
                    "avg_processing_time": comp_data.get("avg_processing_time", 0),
                }

                component_group["components"].append(component)

            result["discrete_chart_data"]["components"].append(component_group)

        return result
