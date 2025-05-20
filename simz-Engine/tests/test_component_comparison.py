import unittest
from unittest.mock import MagicMock, patch
import json
from src.sim.build import SimulationBuilder
from src.sim.csvpaser import CSVScraper
from src.sim.sim_types import ComponentOutput
from src.sim.chart import ChartConfig, CardConfig, Series, DataPoint


class TestComponentComparison(unittest.TestCase):
    """Test the component comparison visualization."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock CSVScraper
        self.csv_scraper = MagicMock(spec=CSVScraper)

        # Set up mock data for the CSVScraper
        self.csv_scraper.components_data = {
            "generator1": {
                "type": "generator",
                "actions": [
                    {"action": "GENERATE", "time": 10.0, "values": {"output_count": 1}},
                    {"action": "GENERATE", "time": 15.0, "values": {"output_count": 1}},
                ],
                "container_interactions": {"container1", "container2"}
            },
            "resource1": {
                "type": "resource",
                "actions": [
                    {"action": "IN", "time": 10.0, "values": {"input_count": 1}},
                    {"action": "OUT", "time": 15.0, "values": {"input_count": 1}},
                    {"action": "QUEUED", "time": 8.0, "values": {"queue_length": 2}},
                    {"action": "ENTER", "time": 9.0},
                    {"action": "Exit", "time": 16.0},
                ],
                "container_interactions": {"container1", "container2", "container3"}
            },
            "resource2": {
                "type": "resource",
                "actions": [
                    {"action": "IN", "time": 16.0, "values": {"input_count": 1}},
                    {"action": "OUT", "time": 20.0, "values": {"input_count": 1}},
                    {"action": "QUEUED", "time": 15.0, "values": {"queue_length": 1}},
                    {"action": "ENTER", "time": 16.0},
                    {"action": "Exit", "time": 21.0},
                ],
                "container_interactions": {"container1", "container3"}
            }
        }

        # Mock the calculate_component_efficiency method
        self.csv_scraper.calculate_component_efficiency.return_value = {
            "generator1": 0.9,
            "resource1": 0.8,
            "resource2": 0.7
        }

        # Mock the calculate_processing_time method
        self.csv_scraper.calculate_processing_time.return_value = {
            "generator1": {
                "mean": 2.0,
                "median": 2.0,
                "min": 2.0,
                "max": 2.0,
                "count": 2,
                "times": [2.0, 2.0]
            },
            "resource1": {
                "mean": 5.0,
                "median": 5.0,
                "min": 5.0,
                "max": 5.0,
                "count": 1,
                "times": [5.0]
            },
            "resource2": {
                "mean": 4.0,
                "median": 4.0,
                "min": 4.0,
                "max": 4.0,
                "count": 1,
                "times": [4.0]
            }
        }

        # Mock the get_component_utilization method
        self.csv_scraper.get_component_utilization.return_value = {
            "generator1": 80.0,
            "resource1": 75.0,
            "resource2": 70.0
        }

        # Create a SimulationBuilder instance with mocked methods
        self.builder = MagicMock(spec=SimulationBuilder)

        # Mock the generate_component_comparison method to use the real implementation
        # Use lambda to properly bind the methods
        self.builder.generate_component_comparison = lambda csv_scraper, component_insights: SimulationBuilder.generate_component_comparison(self.builder, csv_scraper, component_insights)
        self.builder._create_optimization_comparison_chart = lambda component_insights: SimulationBuilder._create_optimization_comparison_chart(self.builder, component_insights)
        self.builder._create_component_comparison_table = lambda csv_scraper, component_insights: SimulationBuilder._create_component_comparison_table(self.builder, csv_scraper, component_insights)

        # Create component insights
        self.component_insights = [
            self._create_mock_component_output("generator1", "Generator 1", "generator"),
            self._create_mock_component_output("resource1", "Resource 1", "resource"),
            self._create_mock_component_output("resource2", "Resource 2", "resource")
        ]

    def _create_mock_component_output(self, comp_id, comp_name, comp_type):
        """Create a mock ComponentOutput object."""
        output = ComponentOutput(
            id=comp_id,
            name=comp_name,
            type=comp_type
        )

        # Add optimization score card
        optimization_score = 85 if comp_type == "generator" else 75
        output.add_card(CardConfig(
            header="Optimization Score",
            description=f"Overall {comp_type} optimization level",
            value=optimization_score,
            valueSuffix="/100",
            valueFormatting="number",
            trend={
                "value": optimization_score,
                "direction": "up",
                "label": "Well Optimized"
            }
        ))

        # Add optimization metrics chart
        metrics_data = [
            DataPoint(x="Processing Speed", y=90.0 if comp_type == "generator" else 75.0),
            DataPoint(x="Resource Utilization", y=85.0 if comp_type == "generator" else 70.0),
            DataPoint(x="Throughput Rate", y=80.0 if comp_type == "generator" else 65.0),
            DataPoint(x="Flow Efficiency", y=75.0 if comp_type == "generator" else 60.0),
            DataPoint(x="Workflow Impact", y=95.0 if comp_type == "generator" else 80.0)
        ]

        output.add_chart(ChartConfig(
            type="chart",
            subtype="bar",
            header="Optimization Metrics",
            description=f"Factors contributing to {comp_type} optimization score",
            series=[Series(name="Score", data=metrics_data)]
        ))

        return output

    def test_generate_component_comparison(self):
        """Test that the component comparison visualization is generated correctly."""
        # Generate the component comparison
        comparison_output = self.builder.generate_component_comparison(
            self.csv_scraper, self.component_insights
        )

        # Check that the comparison output has the expected structure
        self.assertIn("optimization_chart", comparison_output)
        self.assertIn("comparison_table", comparison_output)

        # Check the optimization chart
        optimization_chart = comparison_output["optimization_chart"]
        self.assertEqual(optimization_chart.header, "Component Optimization Comparison")
        self.assertEqual(optimization_chart.subtype, "radar")
        self.assertEqual(len(optimization_chart.series), 3)  # One series per component

        # Check the comparison table
        comparison_table = comparison_output["comparison_table"]
        self.assertEqual(comparison_table["title"], "Component Performance Comparison")
        self.assertEqual(len(comparison_table["data"]), 3)  # One row per component

        # Check that the table has the expected columns
        expected_columns = [
            "id", "name", "type", "efficiency", "optimization_score",
            "avg_processing_time", "in_out_processing_time", "processing_count", "utilization"
        ]
        for column in expected_columns:
            self.assertIn(column, comparison_table["columnOrder"])

        # Check that the table data has the expected values
        for row in comparison_table["data"]:
            self.assertIn(row["id"], ["generator1", "resource1", "resource2"])
            self.assertIn(row["type"], ["generator", "resource"])
            self.assertGreaterEqual(row["optimization_score"], 0)
            self.assertLessEqual(row["optimization_score"], 100)


if __name__ == "__main__":
    unittest.main()
