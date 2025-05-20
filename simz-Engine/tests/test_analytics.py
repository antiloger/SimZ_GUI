import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import math
from src.sim.analytics import ResourceAnalytics
from src.sim.csvpaser import CSVScraper


class TestComponentOptimizationScore(unittest.TestCase):
    """Test the component optimization score calculation."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock CSVScraper
        self.csv_scraper = MagicMock(spec=CSVScraper)

        # Set up mock data for the CSVScraper
        self.csv_scraper.components_data = {
            "test_component": {
                "type": "resource",
                "actions": [
                    {"action": "IN", "time": 10.0, "values": {"input_count": 1}},
                    {"action": "OUT", "time": 15.0, "values": {"input_count": 1}},
                    {"action": "QUEUED", "time": 8.0, "values": {"queue_length": 2}},
                    {"action": "ENTER", "time": 9.0},
                    {"action": "Exit", "time": 16.0},
                ],
                "container_interactions": {"container1", "container2", "container3"}
            }
        }

        # Mock the calculate_all_processing_times method
        self.csv_scraper.calculate_all_processing_times.return_value = {
            "mean": 5.0,
            "median": 5.0,
            "min": 3.0,
            "max": 7.0,
            "count": 10,
            "times": [3.0, 4.0, 5.0, 5.0, 5.0, 5.0, 6.0, 6.0, 7.0, 7.0]
        }

        # Mock the calculate_wait_times method
        self.csv_scraper.calculate_wait_times.return_value = {
            "mean": 1.0,
            "median": 1.0,
            "min": 1.0,
            "max": 1.0,
            "count": 1
        }

        # Create a concrete implementation of ComponentAnalytics
        self.analytics = ResourceAnalytics("test_component", self.csv_scraper)

        # Set up mock metrics
        self.analytics.metrics = {
            "in_out_processing": {
                "mean": 5.0,
                "median": 5.0,
                "min": 5.0,
                "max": 5.0,
                "count": 1,
                "times": [5.0]
            },
            "utilization": 75.0,
            "efficiency": 100.0,
            "action_counts": {
                "IN": 1,
                "OUT": 1,
                "QUEUED": 1,
                "ENTER": 1,
                "Exit": 1
            }
        }

    def test_calculate_optimization_score(self):
        """Test that the optimization score calculation works correctly."""
        # Calculate the optimization score
        result = self.analytics.calculate_optimization_score()

        # Check that the result has the expected structure
        self.assertIn("score", result)
        self.assertIn("metrics", result)
        self.assertIn("normalized_metrics", result)
        self.assertIn("weights", result)
        self.assertIn("weighted_scores", result)

        # Check that the metrics are calculated correctly
        metrics = result["metrics"]
        self.assertIn("processing_time_efficiency", metrics)
        self.assertIn("utilization", metrics)
        self.assertIn("throughput", metrics)
        self.assertIn("bottleneck_potential", metrics)
        self.assertIn("workflow_position", metrics)

        # Check that all metrics are in the range [0, 1]
        for metric, value in metrics.items():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

        # Check that normalized metrics are in the range [0, 100]
        normalized_metrics = result["normalized_metrics"]
        for metric, value in normalized_metrics.items():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 100.0)

        # Check that weights sum to 1.0
        weights = result["weights"]
        self.assertAlmostEqual(sum(weights.values()), 1.0)

        # Check that the final score is in the range [0, 100]
        self.assertGreaterEqual(result["score"], 0.0)
        self.assertLessEqual(result["score"], 100.0)

    def test_processing_time_efficiency(self):
        """Test the processing time efficiency calculation."""
        # Test with component processing time equal to overall average
        efficiency = self.analytics._calculate_processing_time_efficiency(5.0)
        self.assertAlmostEqual(efficiency, 0.5, places=1)

        # Test with component processing time better than average
        self.analytics.metrics["in_out_processing"]["mean"] = 2.5
        efficiency = self.analytics._calculate_processing_time_efficiency(5.0)
        self.assertGreater(efficiency, 0.5)

        # Test with component processing time worse than average
        self.analytics.metrics["in_out_processing"]["mean"] = 10.0
        efficiency = self.analytics._calculate_processing_time_efficiency(5.0)
        self.assertLess(efficiency, 0.5)

        # Test with zero overall average
        efficiency = self.analytics._calculate_processing_time_efficiency(0.0)
        self.assertEqual(efficiency, 0.5)  # Should default to 0.5

        # Test with zero component processing time
        self.analytics.metrics["in_out_processing"]["mean"] = 0.0
        efficiency = self.analytics._calculate_processing_time_efficiency(5.0)
        self.assertEqual(efficiency, 0.5)  # Should default to 0.5

    def test_utilization_metric(self):
        """Test the utilization metric calculation."""
        # Test with 75% utilization
        self.analytics.metrics["utilization"] = 75.0
        utilization = self.analytics._calculate_utilization_metric()
        self.assertAlmostEqual(utilization, 75.0 / 85.0, places=2)

        # Test with 100% utilization (should be slightly penalized)
        self.analytics.metrics["utilization"] = 100.0
        utilization = self.analytics._calculate_utilization_metric()
        self.assertLess(utilization, 1.0)

        # Test with 0% utilization
        self.analytics.metrics["utilization"] = 0.0
        utilization = self.analytics._calculate_utilization_metric()
        self.assertEqual(utilization, 0.0)

    def test_bottleneck_metric(self):
        """Test the bottleneck metric calculation."""
        # Test with normal values
        bottleneck = self.analytics._calculate_bottleneck_metric()
        self.assertGreaterEqual(bottleneck, 0.0)
        self.assertLessEqual(bottleneck, 1.0)

        # Test with generator component (should return 1.0)
        self.analytics.component_type = "generator"
        bottleneck = self.analytics._calculate_bottleneck_metric()
        self.assertEqual(bottleneck, 1.0)


if __name__ == "__main__":
    unittest.main()
