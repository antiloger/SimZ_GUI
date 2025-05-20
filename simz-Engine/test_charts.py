#!/usr/bin/env python3
"""
Test file to verify chart generation in the simulation output.
This version directly tests the chart generation without loading component store.
"""

from src.sim.build import SimulationBuilder
from src.sim.csvpaser import CSVScraper
from src.sim.comp import Component
from src.sim.sim_types import SimOutput, GenTypeState
import os
import json
from pathlib import Path

# Create a simplified version of SimulationBuilder that doesn't require loading files
class TestSimulationBuilder(SimulationBuilder):
    def __init__(self, runName):
        self.runName = runName
        # Initialize minimal required attributes
        self.genState = GenTypeState(root={})

    def output(self, csvScraper):
        """Generate visualization output without loading component store."""
        from src.sim.chart import ChartBuilder, Series, DataPoint, CardConfig, ValueFormatting, ChartSize

        output = SimOutput(id=self.runName)

        # Get time range with error handling
        try:
            simTime = csvScraper.get_time_range()
            max_time = simTime.get("max_time", 0)
            print(f"Simulation time range: {simTime}")

            # Create time card
            time_card = CardConfig(
                header="Simulation Time",
                description="Maximum time in the simulation",
                value=max_time,
                valueFormatting=ValueFormatting.NUMBER,
                size=ChartSize(cols=1, rows=1)
            )
            output.add_card(time_card)
        except Exception as e:
            print(f"Warning: Could not get time range: {e}")

        # Get container count
        try:
            direct_count = len(csvScraper.get_unique_container_ids())
            print(f"Direct container count from CSV: {direct_count}")

            # Create container count card
            container_card = CardConfig(
                header="Total Containers",
                description="Number of unique containers in the simulation",
                value=direct_count,
                valueFormatting=ValueFormatting.NUMBER,
                size=ChartSize(cols=1, rows=1)
            )
            output.add_card(container_card)
        except Exception as e:
            print(f"Warning: Could not get container count: {e}")

        # Get component processing time chart data
        try:
            proc_time_chart_data = csvScraper.get_component_processing_time_chart_data()
            print(f"Got processing time chart data with keys: {proc_time_chart_data.keys()}")

            # Check for continuous data
            if "continuous_data" in proc_time_chart_data:
                print(f"Found continuous data for {len(proc_time_chart_data['continuous_data'])} components")

                # Create continuous processing state chart
                continuous_series = []
                timeline = proc_time_chart_data.get("continuous_chart_data", {}).get("timeline", [])

                if timeline:
                    # Create a series for each component
                    for comp_id, state_data in proc_time_chart_data["continuous_data"].items():
                        # Create data points for this component's processing state
                        data_points = []

                        for i, time in enumerate(timeline):
                            if i < len(state_data["processing_state"]):
                                # 1 = processing, 0 = idle
                                state = state_data["processing_state"][i]

                                # Create a data point for this time
                                data_points.append(DataPoint(x=str(time), y=float(state)))

                        # Add a series for this component
                        if data_points:
                            continuous_series.append(Series(name=state_data["name"], data=data_points))

                    # Create the chart
                    if continuous_series:
                        continuous_chart = ChartBuilder.create_line_chart(
                            header="Component Processing State Over Time",
                            description="Shows when each component is actively processing (1) or idle (0)",
                            series=continuous_series,
                            y_axis_label="Processing State (1=active, 0=idle)",
                            x_axis_label="Simulation Time",
                            show_legend=True,
                            cols=4,
                            rows=1
                        )
                        output.add_chart(continuous_chart)
                        print("Created continuous processing state chart")

            # Check for discrete data
            if "discrete_chart_data" in proc_time_chart_data:
                discrete_data = proc_time_chart_data["discrete_chart_data"]
                timeline = discrete_data.get("timeline", [])
                print(f"Found discrete chart data with timeline of {len(timeline)} points")

                if timeline and "components" in discrete_data:
                    # Create series for each component type
                    for comp_group in discrete_data["components"]:
                        comp_type = comp_group.get("type", "unknown")
                        components = comp_group.get("components", [])

                        for component in components:
                            # Create data points for this component
                            data_points = []
                            processing_times = component.get("processing_times", [])

                            for i, time in enumerate(timeline):
                                if i < len(processing_times):
                                    proc_time = processing_times[i]
                                    if proc_time > 0:  # Only include non-zero processing times
                                        data_points.append(DataPoint(x=str(time), y=float(proc_time)))

                            # Create a series for this component
                            if data_points:
                                series = Series(name=component.get("name", "unknown"), data=data_points)

                                # Create a chart for this component
                                chart = ChartBuilder.create_line_chart(
                                    header=f"Processing Times for {component.get('name', 'Component')}",
                                    description="Processing time between IN and OUT actions",
                                    series=[series],
                                    y_axis_label="Processing Time",
                                    x_axis_label="Simulation Time",
                                    cols=2,
                                    rows=1
                                )
                                output.add_chart(chart)
                                print(f"Created processing time chart for {component.get('name', 'unknown')}")

            # Create a chart showing average processing time by component
            if "components" in proc_time_chart_data:
                avg_data_points = []

                for comp_id, comp_data in proc_time_chart_data["components"].items():
                    if "avg_processing_time" in comp_data and comp_data["avg_processing_time"] > 0:
                        avg_data_points.append(DataPoint(
                            x=str(comp_data.get("name", comp_id)),
                            y=float(comp_data["avg_processing_time"])
                        ))

                if avg_data_points:
                    avg_chart = ChartBuilder.create_bar_chart(
                        header="Average Processing Time by Component",
                        description="Average time between IN and OUT actions for each component",
                        series=[Series(name="Avg Processing Time", data=avg_data_points)],
                        y_axis_label="Processing Time",
                        x_axis_label="Component",
                        cols=2,
                        rows=1
                    )
                    output.add_chart(avg_chart)
                    print("Created average processing time chart")

            # Save the raw chart data for inspection
            with open("chart_data_debug.json", "w") as f:
                # Convert numpy values to Python types for JSON serialization
                import numpy as np
                def convert_numpy(obj):
                    if isinstance(obj, np.integer):
                        return int(obj)
                    elif isinstance(obj, np.floating):
                        return float(obj)
                    elif isinstance(obj, np.ndarray):
                        return obj.tolist()
                    elif isinstance(obj, dict):
                        return {k: convert_numpy(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_numpy(i) for i in obj]
                    else:
                        return obj

                # Save a simplified version of the data for debugging
                simplified_data = {
                    "components": list(proc_time_chart_data.get("components", {}).keys()),
                    "timeline_length": len(proc_time_chart_data.get("continuous_chart_data", {}).get("timeline", [])),
                    "has_continuous_data": "continuous_data" in proc_time_chart_data,
                    "has_discrete_data": "discrete_chart_data" in proc_time_chart_data,
                    "num_charts_created": len(output.charts)
                }
                json.dump(simplified_data, f, indent=2, default=convert_numpy)

            print("Saved chart data debug information to chart_data_debug.json")
        except Exception as e:
            print(f"Warning: Could not get processing time chart data: {e}")

        # Print summary of created charts and cards
        charts = [item for item in output.dashboradData if item.type == "chart"]
        cards = [item for item in output.dashboradData if item.type == "card"]

        print(f"\nCreated {len(charts)} charts:")
        for i, chart in enumerate(charts):
            print(f"{i+1}. {chart.header}")

        print(f"\nCreated {len(cards)} cards:")
        for i, card in enumerate(cards):
            print(f"{i+1}. {card.header}: {card.value}")

        return output

    def save_output(self, output, file_path):
        """Save output to a file."""
        with open(file_path, "w") as f:
            json.dump(output.model_dump(), f, indent=4)
        print(f"Output saved to {file_path}")

def test_charts():
    """Test chart generation from CSV data."""
    # Reset component registry to avoid conflicts
    Component.registry = {}

    # Use the generated test data file
    csv_file = "test_data.csv"
    if not os.path.exists(csv_file):
        print(f"CSV file {csv_file} not found. Please run generate_test_data.py first.")
        return

    print(f"Using CSV file: {csv_file}")

    # Create a CSV scraper
    csv_scraper = CSVScraper(csv_file)

    # Create a test simulation builder
    builder = TestSimulationBuilder("test_charts")

    # Generate output
    print("Generating simulation output...")
    output = builder.output(csv_scraper)

    # Save the output to a file
    output_file = "test_charts_output.json"
    builder.save_output(output, output_file)
    print(f"\nSaved output to {output_file}")

if __name__ == "__main__":
    test_charts()
