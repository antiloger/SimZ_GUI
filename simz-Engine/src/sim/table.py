"""
Table data generation and formatting for SimZ visualizations.

This module provides classes and functions for generating and formatting
tabular data for both component-specific and simulation-wide metrics.

The table structure follows the TypeScript interface:

```typescript
export type TableData = Record<string, any>[]

export interface DynamicTableProps {
  data: TableData
  className?: string
  tableClassName?: string
  headerClassName?: string
  rowClassName?: (index: number) => string | undefined
  cellClassName?: (key: string, value: any, index: number) => string | undefined
  excludeColumns?: string[]
  columnOrder?: string[]
  columnLabels?: Record<string, string>
  emptyMessage?: string
}
```
"""

import uuid
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


def log_console(message: str, logger_console: bool = False) -> None:
    """
    Utility function to control console output.

    Args:
        message: The message to print
        logger_console: Whether to print the message to the console (default: False)
    """
    if logger_console:
        print(message)


class TableProps(BaseModel):
    """
    Properties for the dynamic table component.
    Matches the TypeScript DynamicTableProps interface.
    """
    data: List[Dict[str, Any]]
    className: Optional[str] = None
    tableClassName: Optional[str] = None
    headerClassName: Optional[str] = None
    excludeColumns: Optional[List[str]] = None
    columnOrder: Optional[List[str]] = None
    columnLabels: Optional[Dict[str, str]] = None
    emptyMessage: Optional[str] = None


class Table:
    """
    Class for generating and formatting tabular data.
    """

    @staticmethod
    def create_table_props(
        data: List[Dict[str, Any]],
        class_name: Optional[str] = None,
        table_class_name: Optional[str] = None,
        header_class_name: Optional[str] = None,
        exclude_columns: Optional[List[str]] = None,
        column_order: Optional[List[str]] = None,
        column_labels: Optional[Dict[str, str]] = None,
        empty_message: Optional[str] = None
    ) -> TableProps:
        """
        Create table props that match the TypeScript DynamicTableProps interface.

        Args:
            data: List of data rows
            class_name: CSS class for the table container
            table_class_name: CSS class for the table element
            header_class_name: CSS class for the table header
            exclude_columns: List of column keys to exclude from the table
            column_order: List specifying the order of columns
            column_labels: Dictionary mapping column keys to display labels
            empty_message: Message to display when the table is empty

        Returns:
            TableProps object
        """
        return TableProps(
            data=data,
            className=class_name,
            tableClassName=table_class_name,
            headerClassName=header_class_name,
            excludeColumns=exclude_columns,
            columnOrder=column_order,
            columnLabels=column_labels,
            emptyMessage=empty_message
        )

    @staticmethod
    def create_table(
        data: List[Dict[str, Any]],
        title: Optional[str] = None,
        description: Optional[str] = None,
        exclude_columns: Optional[List[str]] = None,
        column_order: Optional[List[str]] = None,
        column_labels: Optional[Dict[str, str]] = None,
        table_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a table definition that matches the TypeScript interface.

        Args:
            data: List of data rows
            title: Table title (optional)
            description: Table description (optional)
            exclude_columns: List of column keys to exclude from the table
            column_order: List specifying the order of columns
            column_labels: Dictionary mapping column keys to display labels
            table_id: Unique identifier for the table

        Returns:
            Dictionary containing the table definition
        """
        table_props = Table.create_table_props(
            data=data,
            exclude_columns=exclude_columns,
            column_order=column_order,
            column_labels=column_labels,
            empty_message="No data available"
        )

        result = {
            "id": table_id or f"table_{uuid.uuid4().hex[:8]}",
            "data": data
        }

        # Add optional fields if provided
        if title:
            result["title"] = title
        if description:
            result["description"] = description
        if exclude_columns:
            result["excludeColumns"] = exclude_columns
        if column_order:
            result["columnOrder"] = column_order
        if column_labels:
            result["columnLabels"] = column_labels

        return result

    @staticmethod
    def create_component_table(
        components_data: List[Dict[str, Any]],
        title: str = "Component Summary",
        description: str = "Summary of components in the simulation",
        include_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a table with component data.

        Args:
            components_data: List of component data dictionaries
            title: Table title
            description: Table description
            include_fields: List of fields to include (if None, includes all common fields)

        Returns:
            Dictionary containing the component table definition
        """
        # Determine fields to include
        if not include_fields:
            # Find common fields across all components
            all_fields = set()
            for comp in components_data:
                all_fields.update(comp.keys())

            # Default fields to include
            include_fields = ["id", "name", "type"]

            # Add other common fields
            for field in all_fields:
                if field not in include_fields and not field.startswith("_"):
                    include_fields.append(field)

        # Create column labels (mapping from field name to display name)
        column_labels = {}
        for field in include_fields:
            column_labels[field] = field.replace("_", " ").title()

        # Create the table with the new structure
        return Table.create_table(
            data=components_data,
            title=title,
            description=description,
            column_order=include_fields,
            column_labels=column_labels,
            table_id="component_summary_table"
        )

    @staticmethod
    def create_metrics_table(
        metrics_data: List[Dict[str, Any]],
        title: str = "Simulation Metrics",
        description: str = "Key metrics from the simulation",
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a table with simulation metrics.

        Args:
            metrics_data: List of metric data dictionaries
            title: Table title
            description: Table description
            group_by: Field to group metrics by (optional)

        Returns:
            Dictionary containing the metrics table definition
        """
        # Determine fields to include
        all_fields = set()
        for metric in metrics_data:
            all_fields.update(metric.keys())

        # Remove internal fields
        fields = [f for f in all_fields if not f.startswith("_")]

        # Create column labels (mapping from field name to display name)
        column_labels = {}
        for field in fields:
            column_labels[field] = field.replace("_", " ").title()

        # Set column order with group_by field first if specified
        column_order = fields
        if group_by and group_by in fields:
            column_order = [group_by] + [f for f in fields if f != group_by]

        # Create the table with the new structure
        return Table.create_table(
            data=metrics_data,
            title=title,
            description=description,
            column_order=column_order,
            column_labels=column_labels,
            table_id="simulation_metrics_table"
        )
