#!/usr/bin/env python3
"""
Test file to verify chart generation in the simulation output.
"""

from src.sim.build import SimulationBuilder
from src.sim.csvpaser import CSVScraper
from src.sim.comp import Component
import os
import json

class TestSimulationBuilder(SimulationBuilder):
    """Test simulation builder for chart generation."""

    def __init__(self, runName):
        """Initialize with just a run name."""
        self.runName = runName
        self.components = {}

    def get_component_with_name(self, id):
        """Return the component ID as the name for testing."""
        return id

    def save_output(self, output, file_path):
        """Save the output to a file."""
        with open(file_path, "w") as f:
            try:
                json.dump(output.model_dump(), f, indent=4)
            except AttributeError:
                # Fallback for older versions that might not have model_dump
                json.dump(output.dict(), f, indent=4)
        print(f"Output saved to {file_path}")

    def output(self, csvScraper):
        """Generate visualization output without loading component store."""
        from src.sim.chart import ChartBuilder, Series, DataPoint, CardConfig, ValueFormatting, ChartSize
        from src.sim.sim_types import SimOutput

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

        # Container Count Timeline Chart
        try:
            # Get container count timeline data
            container_count_data = csvScraper.get_container_count_timeline()

            # Check if we have the expected data structure
            if "data_points" in container_count_data and container_count_data["data_points"]:
                # Create data points for the chart
                container_count_series = Series(
                    name="Container Count",
                    data=[
                        DataPoint(x=str(point["x"]), y=float(point["y"]))
                        for point in container_count_data["data_points"]
                    ],
                )

                # Create the container count timeline chart
                container_count_chart = ChartBuilder.create_line_chart(
                    header="Container Count Timeline",
                    description="Number of containers being processed at each time point",
                    series=[container_count_series],
                    y_axis_label="Number of Containers",
                    x_axis_label="Simulation Time",
                    show_legend=True,
                    show_grid=True,
                    show_tooltip=True,
                    cols=4,
                    rows=1,
                )

                # Add the chart to output
                output.add_chart(container_count_chart)
                print(f"Created container count timeline chart with {len(container_count_series.data)} data points")
        except Exception as e:
            print(f"Warning: Could not create container count timeline chart: {e}")

        # GenType Distribution Pie Chart
        try:
            # Get GenType distribution data
            gentype_data = csvScraper.get_gentype_distribution()

            # Check if we have the expected data structure
            if "data_points" in gentype_data and gentype_data["data_points"]:
                # Create data points for the chart
                gentype_series = Series(
                    name="GenType Distribution",
                    data=[
                        DataPoint(x=point["x"], y=float(point["y"]))
                        for point in gentype_data["data_points"]
                    ],
                )

                # Create the GenType distribution pie chart
                gentype_chart = ChartBuilder.create_pie_chart(
                    header="GenType Distribution",
                    description="Percentage breakdown of different GenTypes in the simulation",
                    series=[gentype_series],
                    show_legend=True,
                    show_tooltip=True,
                    show_labels=True,
                    cols=2,
                    rows=1,
                )

                # Add the chart to output
                output.add_chart(gentype_chart)
                print(f"Created GenType distribution pie chart with {len(gentype_series.data)} data points")
        except Exception as e:
            print(f"Warning: Could not create GenType distribution pie chart: {e}")

        return output

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

    # Test our new methods
    print("\nTesting container count timeline method...")
    container_count_data = csv_scraper.get_container_count_timeline()
    print(f"Container count timeline data points: {len(container_count_data.get('data_points', []))}")
    print(f"Max container count: {container_count_data.get('max_count', 0)}")

    # Print some sample data points
    if container_count_data.get('data_points'):
        print("Sample container count data points:")
        for i, point in enumerate(container_count_data.get('data_points')[:5]):
            print(f"  Time {point['x']}: {point['y']} containers")

    print("\nTesting GenType distribution method...")
    gentype_data = csv_scraper.get_gentype_distribution()
    print(f"GenType distribution data points: {len(gentype_data.get('data_points', []))}")
    print(f"GenTypes found: {list(gentype_data.get('counts', {}).keys())}")

    # Print the percentages
    if gentype_data.get('percentages'):
        print("GenType distribution percentages:")
        for gentype, percentage in gentype_data.get('percentages').items():
            print(f"  {gentype}: {percentage}%")

    # Create a test simulation builder
    builder = TestSimulationBuilder("test_charts")

    # Generate output
    print("\nGenerating simulation output...")
    output = builder.output(csv_scraper)

    # Print information about the generated charts
    print(f"\nGenerated {len(output.dashboradData)} dashboard items:")
    chart_count = 0
    card_count = 0

    for item in output.dashboradData:
        if item.get("type") == "chart":
            chart_count += 1
            print(f"{chart_count}. Chart: {item.get('header')}")
        elif item.get("type") == "card":
            card_count += 1
            print(f"{card_count}. Card: {item.get('header')}: {item.get('value')}")

    print(f"\nTotal: {chart_count} charts and {card_count} cards")

    # Save the output to a file
    output_file = "test_charts_output.json"
    builder.save_output(output, output_file)
    print(f"\nSaved output to {output_file}")

if __name__ == "__main__":
    test_charts()
