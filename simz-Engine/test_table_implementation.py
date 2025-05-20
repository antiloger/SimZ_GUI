#!/usr/bin/env python3
"""
Test script for the new table implementation.

This script tests:
1. Creating a table with the Table class
2. Adding table data to SimOutput
3. Verifying that table data is properly serialized to JSON
"""

import os
import json
from pathlib import Path
import shutil

from src.sim.table import Table, TableColumn, TableOptions
from src.sim.sim_types import SimOutput

# Test directory for output
TEST_DIR = Path("test_table_implementation_output")
if TEST_DIR.exists():
    shutil.rmtree(TEST_DIR)
TEST_DIR.mkdir(parents=True, exist_ok=True)

def test_table_creation():
    """Test creating a table with the Table class."""
    print("Testing table creation...")
    
    # Create sample columns
    columns = [
        Table.create_column(
            header="ID",
            accessor="id",
            column_type="string"
        ),
        Table.create_column(
            header="Name",
            accessor="name",
            column_type="string"
        ),
        Table.create_column(
            header="Type",
            accessor="type",
            column_type="string"
        ),
        Table.create_column(
            header="Value",
            accessor="value",
            column_type="number",
            align="right"
        )
    ]
    
    # Create sample data
    data = [
        {"id": "comp1", "name": "Component 1", "type": "generator", "value": 100},
        {"id": "comp2", "name": "Component 2", "type": "resource", "value": 75.5},
        {"id": "comp3", "name": "Component 3", "type": "resource", "value": 90.2}
    ]
    
    # Create table options
    options = Table.create_options(
        show_pagination=True,
        show_search=True,
        default_sort_field="name"
    )
    
    # Create the table
    table = Table.create_table(
        title="Test Table",
        description="A test table for the new implementation",
        columns=columns,
        data=data,
        options=options,
        table_id="test_table"
    )
    
    # Verify the table was created correctly
    assert table["id"] == "test_table"
    assert table["title"] == "Test Table"
    assert len(table["columns"]) == 4
    assert len(table["data"]) == 3
    
    # Save the table to a file
    table_file = TEST_DIR / "test_table.json"
    with open(table_file, "w") as f:
        json.dump(table, f, indent=4)
    
    print(f"Table saved to {table_file}")
    print("Table creation test completed successfully!")
    
    return table

def test_component_table():
    """Test creating a component table."""
    print("Testing component table creation...")
    
    # Create sample component data
    components_data = [
        {
            "id": "comp1",
            "name": "Generator 1",
            "type": "generator",
            "generation_count": 100,
            "avg_processing_time": 2.5
        },
        {
            "id": "comp2",
            "name": "Resource 1",
            "type": "resource",
            "capacity": 2,
            "utilization": 75.5,
            "avg_processing_time": 3.2
        },
        {
            "id": "comp3",
            "name": "Resource 2",
            "type": "resource",
            "capacity": 1,
            "utilization": 90.2,
            "avg_processing_time": 4.1
        }
    ]
    
    # Create the component table
    component_table = Table.create_component_table(
        components_data=components_data,
        title="Component Summary",
        description="Summary of components in the simulation"
    )
    
    # Verify the table was created correctly
    assert component_table["title"] == "Component Summary"
    assert len(component_table["data"]) == 3
    
    # Save the table to a file
    table_file = TEST_DIR / "component_table.json"
    with open(table_file, "w") as f:
        json.dump(component_table, f, indent=4)
    
    print(f"Component table saved to {table_file}")
    print("Component table test completed successfully!")
    
    return component_table

def test_metrics_table():
    """Test creating a metrics table."""
    print("Testing metrics table creation...")
    
    # Create sample metrics data
    metrics_data = [
        {
            "metric": "Simulation Duration",
            "value": 100.5,
            "unit": "time units",
            "category": "Time"
        },
        {
            "metric": "Total Components",
            "value": 10,
            "unit": "count",
            "category": "Components"
        },
        {
            "metric": "Total Containers",
            "value": 50,
            "unit": "count",
            "category": "Containers"
        },
        {
            "metric": "Average Processing Time",
            "value": 3.2,
            "unit": "time units",
            "category": "Processing"
        },
        {
            "metric": "Maximum Processing Time",
            "value": 8.5,
            "unit": "time units",
            "category": "Processing"
        }
    ]
    
    # Create the metrics table
    metrics_table = Table.create_metrics_table(
        metrics_data=metrics_data,
        title="Simulation Metrics",
        description="Key metrics from the simulation run",
        group_by="category"
    )
    
    # Verify the table was created correctly
    assert metrics_table["title"] == "Simulation Metrics"
    assert len(metrics_table["data"]) == 5
    
    # Save the table to a file
    table_file = TEST_DIR / "metrics_table.json"
    with open(table_file, "w") as f:
        json.dump(metrics_table, f, indent=4)
    
    print(f"Metrics table saved to {table_file}")
    print("Metrics table test completed successfully!")
    
    return metrics_table

def test_sim_output_with_tables():
    """Test adding tables to SimOutput."""
    print("Testing SimOutput with tables...")
    
    # Create a SimOutput instance
    sim_output = SimOutput(id="test_sim")
    
    # Create and add tables
    table1 = test_table_creation()
    table2 = test_component_table()
    table3 = test_metrics_table()
    
    # Add tables to SimOutput
    sim_output.add_table(table1)
    sim_output.add_table(table2)
    sim_output.add_table(table3)
    
    # Verify tables were added correctly
    assert len(sim_output.dashboardTable) == 3
    
    # Save the SimOutput to a file
    output_file = TEST_DIR / "sim_output_with_tables.json"
    with open(output_file, "w") as f:
        try:
            json.dump(sim_output.model_dump(), f, indent=4)
        except AttributeError:
            json.dump(sim_output.dict(), f, indent=4)
    
    print(f"SimOutput with tables saved to {output_file}")
    print("SimOutput with tables test completed successfully!")

if __name__ == "__main__":
    test_sim_output_with_tables()
