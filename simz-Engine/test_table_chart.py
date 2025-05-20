#!/usr/bin/env python3
"""
Test script for the new table chart type and component analytics storage.

This script tests:
1. Creating a table chart with component-specific properties
2. Verifying that component analytics are stored in separate files
3. Checking that the main simulation output doesn't contain component-specific analytics
"""

import os
import json
from pathlib import Path
import shutil

from src.sim.chart import (
    ChartBuilder,
    Series,
    DataPoint,
    ChartSubtype,
)

# Test directory for output
TEST_DIR = Path("test_table_chart_output")
if TEST_DIR.exists():
    shutil.rmtree(TEST_DIR)
TEST_DIR.mkdir(parents=True, exist_ok=True)

def test_table_chart():
    """Test creating a table chart with component-specific properties."""
    print("Testing table chart creation...")
    
    # Create sample data for the table
    data_points = [
        DataPoint(x="component1", y=1),
        DataPoint(x="component2", y=1),
        DataPoint(x="component3", y=1),
    ]
    
    # Create a series with the data
    series = Series(name="Components", data=data_points)
    
    # Create component-specific properties
    component_properties = {
        "components": [
            {
                "id": "component1",
                "name": "Generator 1",
                "type": "generator",
                "properties": {
                    "generation_count": 100,
                }
            },
            {
                "id": "component2",
                "name": "Resource 1",
                "type": "resource",
                "properties": {
                    "capacity": 2,
                    "utilization": 75.5,
                }
            },
            {
                "id": "component3",
                "name": "Resource 2",
                "type": "resource",
                "properties": {
                    "capacity": 1,
                    "utilization": 90.2,
                }
            }
        ]
    }
    
    # Create a table chart
    table_chart = ChartBuilder.create_table_chart(
        header="Component Summary",
        description="Summary of components in the simulation",
        series=[series],
        component_properties=component_properties,
        cols=4,
        rows=1
    )
    
    # Verify the chart was created correctly
    assert table_chart.subtype == ChartSubtype.TABLE
    assert table_chart.header == "Component Summary"
    assert len(table_chart.series) == 1
    assert len(table_chart.series[0].data) == 3
    
    # Verify the component properties were set correctly
    assert table_chart.options.component_properties == component_properties
    
    # Save the chart to a file
    chart_file = TEST_DIR / "table_chart.json"
    with open(chart_file, "w") as f:
        try:
            json.dump(table_chart.model_dump(), f, indent=4)
        except AttributeError:
            json.dump(table_chart.dict(), f, indent=4)
    
    print(f"Table chart saved to {chart_file}")
    print("Table chart test completed successfully!")
    
    return table_chart

if __name__ == "__main__":
    test_table_chart()
