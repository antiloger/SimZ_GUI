"""
Component-specific analytics system for SimZ Engine.

This module provides classes for analyzing simulation data and generating
component-specific insights and visualizations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
from collections import Counter, defaultdict
import math

from src.sim.csvpaser import CSVScraper
from src.sim.chart import (
    ChartBuilder,
    Series,
    DataPoint,
    CardConfig,
    ChartConfig,
    ValueFormatting,
    ChartSize,
    TrendDirection,
    BarLayout,
    BarType,
    LineType
)
from src.sim.sim_types import ComponentOutput


class ComponentAnalytics(ABC):
    """
    Base class for component-specific analytics.

    This class provides common functionality for analyzing simulation data
    and generating component-specific insights and visualizations.
    """

    def __init__(self, component_id: str, component_type: str, csv_scraper: CSVScraper):
        """
        Initialize the analytics system for a specific component.

        Args:
            component_id: The ID of the component to analyze
            component_type: The type of the component (generator, resource, etc.)
            csv_scraper: The CSVScraper instance for accessing simulation data
        """
        self.component_id = component_id
        self.component_type = component_type
        self.csv_scraper = csv_scraper
        self.metrics = {}

    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """
        Calculate performance metrics for the component.

        This method calculates common performance metrics that apply to all component types,
        including processing time, efficiency, and utilization.

        Returns:
            Dictionary of performance metrics
        """
        metrics = {}

        # Get processing time metrics
        try:
            proc_times = self.csv_scraper.calculate_processing_time(self.component_id)
            if proc_times:
                metrics["processing_time"] = proc_times
        except Exception as e:
            print(f"Error calculating processing time metrics: {e}")
            metrics["processing_time"] = {
                "mean": 0, "median": 0, "min": 0, "max": 0, "count": 0
            }

        # Get efficiency metrics
        try:
            efficiency = self.csv_scraper.calculate_component_efficiency(self.component_id)
            metrics["efficiency"] = efficiency
        except Exception as e:
            print(f"Error calculating efficiency metrics: {e}")
            metrics["efficiency"] = 0.0

        # Get utilization metrics
        try:
            utilization = self.csv_scraper.get_component_utilization(self.component_id)
            metrics["utilization"] = utilization
        except Exception as e:
            print(f"Error calculating utilization metrics: {e}")
            metrics["utilization"] = 0.0

        # Get action counts
        try:
            component_data = self.csv_scraper.components_data.get(self.component_id, {})
            actions = component_data.get("actions", [])
            action_counts = Counter(action["action"] for action in actions)
            metrics["action_counts"] = dict(action_counts)
        except Exception as e:
            print(f"Error calculating action counts: {e}")
            metrics["action_counts"] = {}

        # Calculate IN/OUT processing time specifically
        try:
            in_out_times = self._calculate_in_out_processing_times()
            metrics["in_out_processing"] = in_out_times
        except Exception as e:
            print(f"Error calculating IN/OUT processing times: {e}")
            metrics["in_out_processing"] = {
                "times": [], "mean": 0, "median": 0, "min": 0, "max": 0, "count": 0
            }

        # Calculate optimization score
        try:
            optimization_score = self.calculate_optimization_score()
            metrics["optimization_score"] = optimization_score
        except Exception as e:
            print(f"Error calculating optimization score: {e}")
            metrics["optimization_score"] = {
                "score": 0, "metrics": {}, "normalized_metrics": {}
            }

        # Store the metrics for later use
        self.metrics = metrics
        return metrics

    def _calculate_in_out_processing_times(self) -> Dict[str, Any]:
        """
        Calculate processing times between IN and OUT action pairs.

        This method uses multiple strategies to match IN and OUT actions:
        1. Match by container ID and input_count
        2. Match by container ID only
        3. Match by input_count only
        4. Match by sequence (if all else fails)

        Returns:
            Dictionary with processing time statistics
        """
        result = {
            "times": [],
            "mean": 0,
            "median": 0,
            "min": 0,
            "max": 0,
            "count": 0,
            "by_container": {}
        }

        try:
            # Get component actions
            component_data = self.csv_scraper.components_data.get(self.component_id, {})
            if not component_data:
                print(f"No data found for component {self.component_id}")
                return result

            actions = component_data.get("actions", [])
            if not actions:
                print(f"No actions found for component {self.component_id}")
                return result

            # Filter for IN and OUT actions only
            in_actions = [a for a in actions if a["action"] == "IN"]
            out_actions = [a for a in actions if a["action"] == "OUT"]

            print(f"Processing time calculation for component {self.component_id}: {len(in_actions)} IN actions, {len(out_actions)} OUT actions")

            if not in_actions or not out_actions:
                print(f"Missing IN or OUT actions for component {self.component_id}")
                return result

            # Sort actions by time
            in_actions = sorted(in_actions, key=lambda x: x["time"])
            out_actions = sorted(out_actions, key=lambda x: x["time"])

            # STRATEGY 1: Match by container ID and input_count
            matched_pairs = []
            remaining_in = []
            remaining_out = []

            for in_action in in_actions:
                in_container_id = self._extract_container_id(in_action)
                in_input_count = self._extract_input_count(in_action)
                in_time = in_action["time"]

                matched = False

                for out_action in out_actions:
                    if out_action.get("_matched", False):
                        continue

                    out_container_id = self._extract_container_id(out_action)
                    out_input_count = self._extract_input_count(out_action)
                    out_time = out_action["time"]

                    # Match by both container ID and input_count if both are available
                    if (in_container_id and out_container_id and in_container_id == out_container_id and
                        in_input_count is not None and out_input_count is not None and in_input_count == out_input_count and
                        out_time > in_time):

                        processing_time = out_time - in_time
                        matched_pairs.append((in_action, out_action, processing_time))
                        out_action["_matched"] = True
                        matched = True
                        break

                if not matched:
                    remaining_in.append(in_action)

            for out_action in out_actions:
                if not out_action.get("_matched", False):
                    remaining_out.append(out_action)

            # STRATEGY 2: Match remaining by container ID only
            still_remaining_in = []
            for in_action in remaining_in:
                in_container_id = self._extract_container_id(in_action)
                in_time = in_action["time"]

                if not in_container_id:
                    still_remaining_in.append(in_action)
                    continue

                matched = False
                for out_action in remaining_out:
                    if out_action.get("_matched", False):
                        continue

                    out_container_id = self._extract_container_id(out_action)
                    out_time = out_action["time"]

                    if in_container_id == out_container_id and out_time > in_time:
                        processing_time = out_time - in_time
                        matched_pairs.append((in_action, out_action, processing_time))
                        out_action["_matched"] = True
                        matched = True
                        break

                if not matched:
                    still_remaining_in.append(in_action)

            remaining_in = still_remaining_in
            remaining_out = [o for o in remaining_out if not o.get("_matched", False)]

            # STRATEGY 3: Match remaining by input_count only
            still_remaining_in = []
            for in_action in remaining_in:
                in_input_count = self._extract_input_count(in_action)
                in_time = in_action["time"]

                if in_input_count is None:
                    still_remaining_in.append(in_action)
                    continue

                matched = False
                for out_action in remaining_out:
                    if out_action.get("_matched", False):
                        continue

                    out_input_count = self._extract_input_count(out_action)
                    out_time = out_action["time"]

                    if in_input_count == out_input_count and out_time > in_time:
                        processing_time = out_time - in_time
                        matched_pairs.append((in_action, out_action, processing_time))
                        out_action["_matched"] = True
                        matched = True
                        break

                if not matched:
                    still_remaining_in.append(in_action)

            remaining_in = still_remaining_in
            remaining_out = [o for o in remaining_out if not o.get("_matched", False)]

            # STRATEGY 4: Match remaining by sequence (if all else fails)
            # Only do this if we have equal numbers of remaining IN and OUT actions
            if len(remaining_in) > 0 and len(remaining_out) > 0:
                remaining_in = sorted(remaining_in, key=lambda x: x["time"])
                remaining_out = sorted(remaining_out, key=lambda x: x["time"])

                # Only match if we have the same number of IN and OUT actions
                # or if this is a Resource component (which should have matching pairs)
                if len(remaining_in) == len(remaining_out) or self.component_type.lower() == "resource":
                    for i in range(min(len(remaining_in), len(remaining_out))):
                        in_action = remaining_in[i]
                        out_action = remaining_out[i]
                        in_time = in_action["time"]
                        out_time = out_action["time"]

                        if out_time > in_time:
                            processing_time = out_time - in_time
                            matched_pairs.append((in_action, out_action, processing_time))

            # Process all matched pairs
            for in_action, out_action, processing_time in matched_pairs:
                container_id = self._extract_container_id(in_action) or self._extract_container_id(out_action)
                input_count = self._extract_input_count(in_action) or self._extract_input_count(out_action)

                # Use a unique identifier for the pair
                pair_id = container_id if container_id else f"input_{input_count}" if input_count is not None else f"seq_{len(result['times'])}"

                result["times"].append(processing_time)
                result["by_container"][pair_id] = processing_time

            # Calculate statistics if we have times
            if result["times"]:
                result["mean"] = np.mean(result["times"])
                result["median"] = np.median(result["times"])
                result["min"] = min(result["times"])
                result["max"] = max(result["times"])
                result["count"] = len(result["times"])
                print(f"Found {result['count']} processing time pairs for component {self.component_id}")
                print(f"Processing time statistics: mean={result['mean']}, median={result['median']}, min={result['min']}, max={result['max']}")
            else:
                print(f"No valid processing time pairs found for component {self.component_id}")

                # If this is a Resource component and we have no processing times,
                # try to estimate based on the time difference between consecutive actions
                if self.component_type.lower() == "resource" and len(actions) >= 2:
                    actions = sorted(actions, key=lambda x: x["time"])
                    time_diffs = []

                    for i in range(1, len(actions)):
                        time_diff = actions[i]["time"] - actions[i-1]["time"]
                        if time_diff > 0:
                            time_diffs.append(time_diff)

                    if time_diffs:
                        # Use the median time difference as an estimate
                        estimated_time = np.median(time_diffs)
                        result["times"] = [estimated_time]
                        result["mean"] = estimated_time
                        result["median"] = estimated_time
                        result["min"] = estimated_time
                        result["max"] = estimated_time
                        result["count"] = 1
                        result["by_container"]["estimated"] = estimated_time
                        result["is_estimated"] = True
                        print(f"Using estimated processing time of {estimated_time} for component {self.component_id}")

        except Exception as e:
            print(f"Error calculating processing times for component {self.component_id}: {str(e)}")
            # Don't re-raise the exception, just return the empty result

        return result

    def _extract_container_id(self, action: Dict[str, Any]) -> Optional[str]:
        """
        Extract container ID from an action using multiple strategies.

        This method tries several approaches to extract the container ID:
        1. Direct access from PDV dictionary
        2. Parse PDV if it's a string
        3. Look for containerId in values
        4. Extract from PDV string using regex

        Args:
            action: The action dictionary from which to extract the container ID

        Returns:
            The container ID if found, None otherwise
        """
        try:
            # Method 1: Direct access from PDV dictionary
            pdv = action.get("PDV", {})
            if isinstance(pdv, dict) and "containerId" in pdv:
                container_id = pdv["containerId"]
                if container_id:
                    print(f"Extracted container ID {container_id} from PDV dictionary")
                    return container_id

            # Method 2: Parse PDV if it's a string
            if isinstance(pdv, str):
                try:
                    import json
                    parsed_pdv = json.loads(pdv.replace("'", '"'))
                    if isinstance(parsed_pdv, dict) and "containerId" in parsed_pdv:
                        container_id = parsed_pdv["containerId"]
                        if container_id:
                            print(f"Extracted container ID {container_id} from PDV string")
                            return container_id
                except:
                    pass

            # Method 3: Look for containerId in values
            values = action.get("values", {})
            if isinstance(values, dict) and "containerId" in values:
                container_id = values["containerId"]
                if container_id:
                    print(f"Extracted container ID {container_id} from values dictionary")
                    return container_id

            # Method 4: Extract from PDV string using regex
            if isinstance(pdv, str):
                import re
                # Try to match containerId in various formats
                patterns = [
                    r'"containerId":\s*"([^"]+)"',
                    r"'containerId':\s*'([^']+)'",
                    r'"containerId":\s*"([^"]+)"',
                    r"containerId=([a-zA-Z0-9-_]+)",
                ]

                for pattern in patterns:
                    match = re.search(pattern, pdv)
                    if match:
                        container_id = match.group(1)
                        if container_id:
                            print(f"Extracted container ID {container_id} using regex pattern {pattern}")
                            return container_id

            # Method 5: Try to extract from input_count if available
            input_count = self._extract_input_count(action)
            if input_count is not None:
                # Use input_count as a fallback identifier
                container_id = f"input_{input_count}"
                print(f"Using input_count {input_count} as fallback container ID")
                return container_id

        except Exception as e:
            print(f"Error extracting container ID: {str(e)}")

        print(f"Failed to extract container ID from action: {action.get('action')} at time {action.get('time')}")
        return None

    def _extract_input_count(self, action: Dict[str, Any]) -> Optional[int]:
        """Extract input_count from an action."""
        try:
            values = action.get("values", {})
            if isinstance(values, dict) and "input_count" in values:
                return values["input_count"]
        except:
            pass
        return None

    @abstractmethod
    def generate_component_insights(self) -> ComponentOutput:
        """
        Generate component-specific insights and visualizations.

        This method should be implemented by each component type to provide
        specialized analytics and visualizations.

        Returns:
            ComponentOutput object with charts and cards
        """
        pass

    def _create_processing_time_chart(self) -> ChartConfig:
        """
        Create a chart showing processing time statistics.

        Returns:
            ChartConfig object for a bar chart
        """
        try:
            # Get processing time data
            proc_time = self.metrics.get("in_out_processing", {})

            # Check if we have any processing time data
            if not proc_time or proc_time.get("count", 0) == 0:
                # Create a chart with a clear message that there's no data
                return ChartBuilder.create_bar_chart(
                    header="Processing Time Statistics",
                    description="No processing time data available",
                    series=[Series(name="Processing Time", data=[DataPoint(x="No Data", y=0)])],
                    y_axis_label="Time",
                    x_axis_label="Statistic",
                    cols=2,
                    rows=1
                )

            # Check if the data is estimated
            is_estimated = proc_time.get("is_estimated", False)

            # Create data points
            data_points = [
                DataPoint(x="Mean", y=proc_time.get("mean", 0)),
                DataPoint(x="Median", y=proc_time.get("median", 0)),
                DataPoint(x="Min", y=proc_time.get("min", 0)),
                DataPoint(x="Max", y=proc_time.get("max", 0))
            ]

            # Create series
            series = Series(name="Processing Time", data=data_points)

            # Create description based on data source
            if is_estimated:
                description = "Estimated processing time (based on time differences)"
            else:
                description = f"Time between IN and OUT actions (based on {proc_time.get('count', 0)} pairs)"

            # Create chart
            return ChartBuilder.create_bar_chart(
                header="Processing Time Statistics",
                description=description,
                series=[series],
                y_axis_label="Time",
                x_axis_label="Statistic",
                cols=2,
                rows=1
            )
        except Exception as e:
            # If anything goes wrong, return a fallback chart
            print(f"Error creating processing time chart: {str(e)}")
            return ChartBuilder.create_bar_chart(
                header="Processing Time Statistics",
                description="Error generating chart",
                series=[Series(name="Processing Time", data=[DataPoint(x="Error", y=0)])],
                y_axis_label="Time",
                x_axis_label="Statistic",
                cols=2,
                rows=1
            )

    def _create_efficiency_card(self) -> CardConfig:
        """
        Create a card showing efficiency metrics.

        Returns:
            CardConfig object
        """
        efficiency = self.metrics.get("efficiency", 0.0)

        # Determine trend direction
        trend_direction = TrendDirection.UP if efficiency >= 0.7 else TrendDirection.DOWN

        return ChartBuilder.create_metric_card(
            header="Component Efficiency",
            description="Ratio of productive actions to total actions",
            value=efficiency * 100,  # Convert to percentage
            value_suffix="%",
            value_formatting=ValueFormatting.NUMBER,
            trend_value=efficiency * 100,
            trend_direction=trend_direction,
            trend_label="Efficiency Score",
            cols=1,
            rows=1
        )

    def _create_utilization_card(self) -> CardConfig:
        """
        Create a card showing utilization metrics.

        Returns:
            CardConfig object
        """
        utilization = self.metrics.get("utilization", 0.0)

        # Determine trend direction
        trend_direction = TrendDirection.UP if utilization >= 70 else TrendDirection.DOWN

        return ChartBuilder.create_metric_card(
            header="Component Utilization",
            description="Percentage of time the component is active",
            value=utilization,
            value_suffix="%",
            value_formatting=ValueFormatting.NUMBER,
            trend_value=utilization,
            trend_direction=trend_direction,
            trend_label="Utilization Rate",
            cols=1,
            rows=1
        )

    def calculate_optimization_score(self) -> Dict[str, Any]:
        """
        Calculate an optimization score for the component based on multiple metrics.

        The optimization score considers:
        1. Processing time efficiency (actual vs. expected processing time)
        2. Resource utilization (idle time vs. active time)
        3. Throughput rate (containers processed per time unit)
        4. Bottleneck potential (how often this component delays the overall process)
        5. Component's position in the workflow (upstream/downstream impact)

        Each metric is normalized to a 0-1 scale where higher values indicate better performance.
        The final score is a weighted average of these metrics, scaled to 0-100.

        Returns:
            Dictionary with optimization score and contributing metrics:
            {
                "score": float,                  # Overall optimization score (0-100)
                "metrics": Dict[str, float],     # Raw metric values (0-1 scale)
                "normalized_metrics": Dict[str, float],  # Metrics on 0-100 scale
                "weights": Dict[str, float],     # Weight for each metric
                "weighted_scores": Dict[str, float]  # Contribution of each metric to final score
            }
        """
        # Initialize result structure
        result = {
            "score": 0,
            "metrics": {},
            "normalized_metrics": {},
            "weights": {},
            "weighted_scores": {}
        }

        # Get overall simulation metrics for comparison
        overall_avg_processing_time = 0
        try:
            all_processing_times = self.csv_scraper.calculate_all_processing_times()
            # Only use mean if we have actual data
            if all_processing_times.get("count", 0) > 0:
                overall_avg_processing_time = all_processing_times.get("mean", 0)
        except Exception as e:
            # Log error but continue with default value
            print(f"Error getting overall processing times: {e}")

        # =====================================================================
        # 1. Processing Time Efficiency
        # =====================================================================
        # Lower processing time is better - how does this component's processing time
        # compare to the average across all components?
        processing_time_metric = self._calculate_processing_time_efficiency(overall_avg_processing_time)

        # =====================================================================
        # 2. Resource Utilization
        # =====================================================================
        # Higher utilization is better - how effectively is the component being used?
        utilization_metric = self._calculate_utilization_metric()

        # =====================================================================
        # 3. Throughput Rate
        # =====================================================================
        # Higher throughput is better - how many containers does this component process?
        throughput_metric = self._calculate_throughput_metric()

        # =====================================================================
        # 4. Bottleneck Potential
        # =====================================================================
        # Lower bottleneck potential is better - how often does this component cause delays?
        bottleneck_metric = self._calculate_bottleneck_metric()

        # =====================================================================
        # 5. Workflow Position Impact
        # =====================================================================
        # This measures the component's importance in the overall workflow
        position_metric = self._calculate_position_metric()

        # Store raw metrics (all normalized to 0-1 scale where higher is better)
        result["metrics"] = {
            "processing_time_efficiency": processing_time_metric,
            "utilization": utilization_metric,
            "throughput": throughput_metric,
            "bottleneck_potential": bottleneck_metric,
            "workflow_position": position_metric
        }

        # Normalize metrics to 0-100 scale for display
        result["normalized_metrics"] = {
            "processing_time_efficiency": round(processing_time_metric * 100, 1),
            "utilization": round(utilization_metric * 100, 1),
            "throughput": round(throughput_metric * 100, 1),
            "bottleneck_potential": round(bottleneck_metric * 100, 1),
            "workflow_position": round(position_metric * 100, 1)
        }

        # Define weights for each metric - these should sum to 1.0
        weights = {
            "processing_time_efficiency": 0.25,  # 25% weight - critical for performance
            "utilization": 0.20,                # 20% weight - important for resource efficiency
            "throughput": 0.20,                 # 20% weight - important for productivity
            "bottleneck_potential": 0.25,       # 25% weight - critical for workflow efficiency
            "workflow_position": 0.10           # 10% weight - contextual importance
        }
        result["weights"] = weights

        # Calculate weighted scores
        weighted_scores = {}
        for metric, value in result["metrics"].items():
            weight = weights.get(metric, 0)
            weighted_scores[metric] = value * weight
        result["weighted_scores"] = weighted_scores

        # Calculate final score (0-100 scale)
        final_score = sum(weighted_scores.values()) * 100
        result["score"] = round(final_score, 1)

        return result

    def _calculate_processing_time_efficiency(self, overall_avg_processing_time: float) -> float:
        """
        Calculate processing time efficiency metric.

        This metric compares the component's processing time to the overall average.
        Lower processing time relative to average is better.

        Args:
            overall_avg_processing_time: Average processing time across all components

        Returns:
            Normalized efficiency metric (0-1 scale, higher is better)
        """
        # Default to average efficiency (0.5) if we can't calculate
        processing_time_metric = 0.5

        try:
            # Get component's average processing time
            component_proc_time = self.metrics.get("in_out_processing", {}).get("mean", 0)

            # If we have valid data for both component and overall processing times
            if overall_avg_processing_time > 0 and component_proc_time > 0:
                # Calculate ratio of component processing time to overall average
                # Lower ratio is better (faster than average)
                processing_time_ratio = component_proc_time / overall_avg_processing_time

                # Invert and normalize so higher is better
                # 1.0 means average, >1.0 means better than average, <1.0 means worse than average
                if processing_time_ratio > 0:
                    # Use sigmoid function to normalize: 1 / (1 + e^(k*(x-1)))
                    # This gives a smooth curve where:
                    # - processing_time_ratio = 1 (average) gives 0.5
                    # - processing_time_ratio < 1 (better than average) gives >0.5
                    # - processing_time_ratio > 1 (worse than average) gives <0.5
                    k = 2.0  # Controls steepness of the curve
                    processing_time_metric = 1.0 / (1.0 + math.exp(k * (processing_time_ratio - 1.0)))

                    # Ensure the result is in the range [0, 1]
                    processing_time_metric = max(0.0, min(1.0, processing_time_metric))
            elif self.component_type == "generator":
                # For generators without processing time data, use a default good score
                # since they typically don't have traditional processing times
                processing_time_metric = 0.8
        except Exception as e:
            # Log error but continue with default value
            print(f"Error calculating processing time efficiency: {e}")

        return processing_time_metric

    def _calculate_utilization_metric(self) -> float:
        """
        Calculate resource utilization metric.

        This metric measures how effectively the component is being used.
        Higher utilization is generally better, but extremely high utilization
        might indicate a bottleneck.

        Returns:
            Normalized utilization metric (0-1 scale, higher is better)
        """
        try:
            # Get utilization percentage and convert to 0-1 scale
            utilization_pct = self.metrics.get("utilization", 0)

            # Apply a non-linear transformation to favor moderate-to-high utilization
            # but penalize extremely high utilization (which might indicate a bottleneck)
            # Use a modified bell curve that peaks at 85% utilization
            if utilization_pct <= 85:
                # Linear increase up to 85%
                utilization_metric = utilization_pct / 85.0
            else:
                # Slight decrease after 85% to penalize potential bottlenecks
                # Formula: 1 - (utilization_pct - 85) / 150
                # This gives a gentle slope down from 1.0 at 85% to 0.9 at 100%
                utilization_metric = 1.0 - (utilization_pct - 85.0) / 150.0

            # Ensure the result is in the range [0, 1]
            utilization_metric = max(0.0, min(1.0, utilization_metric))

            # Special case for generators which might have naturally low utilization
            if self.component_type == "generator" and utilization_pct > 0:
                # For generators, even low utilization can be good if they're producing
                utilization_metric = max(utilization_metric, 0.5)

            return utilization_metric
        except Exception as e:
            # Log error and return default value
            print(f"Error calculating utilization metric: {e}")
            return 0.5  # Default to middle value

    def _calculate_throughput_metric(self) -> float:
        """
        Calculate throughput rate metric.

        This metric measures how many containers the component processes per time unit.
        Higher throughput is generally better.

        Returns:
            Normalized throughput metric (0-1 scale, higher is better)
        """
        # Default to zero throughput
        throughput_metric = 0.0

        try:
            # Get count of IN/OUT pairs or relevant actions based on component type
            if self.component_type == "generator":
                # For generators, use GENERATE action count
                action_counts = self.metrics.get("action_counts", {})
                action_count = action_counts.get("GENERATE", 0)
            else:
                # For other components, use IN/OUT pair count
                action_count = self.metrics.get("in_out_processing", {}).get("count", 0)

            # Get time range for this component
            component_data = self.csv_scraper.components_data.get(self.component_id, {})
            actions = component_data.get("actions", [])

            # Calculate throughput rate (actions per time unit)
            throughput_rate = 0.0
            if actions and len(actions) > 1:
                times = [action["time"] for action in actions]
                time_range = max(times) - min(times)

                if time_range > 0 and action_count > 0:
                    throughput_rate = action_count / time_range

            # Normalize throughput based on component type and expected rates
            if self.component_type == "generator":
                # For generators, normalize based on expected generation rate
                # Assume 0.1 is a good rate (1 entity every 10 time units)
                expected_rate = 0.1
                # Use a logarithmic scale to handle wide range of possible rates
                # log(rate/expected_rate + 0.1) / log(10.1) gives a value between 0 and 1
                # where expected_rate maps to ~0.5
                if throughput_rate > 0:
                    throughput_metric = min(math.log10(throughput_rate/expected_rate + 0.1) / math.log10(10.1), 1.0)
                else:
                    throughput_metric = 0.0

            elif self.component_type == "resource":
                # For resources, normalize based on capacity if available
                capacity = 1.0  # Default capacity

                # Try to get capacity from component data
                for action in actions:
                    if isinstance(action.get("values"), dict) and "capacity" in action["values"]:
                        try:
                            cap_value = action["values"]["capacity"]
                            if isinstance(cap_value, (int, float)) and cap_value > 0:
                                capacity = cap_value
                                break
                        except (ValueError, TypeError):
                            pass

                # Calculate normalized throughput
                # Use sigmoid function to normalize: 1 / (1 + e^(-k*(x-c)))
                # where k controls steepness and c is the midpoint
                if capacity > 0:
                    k = 5.0  # Steepness
                    c = 0.5  # Midpoint (0.5 * capacity is considered average)
                    x = throughput_rate / capacity  # Normalize by capacity
                    throughput_metric = 1.0 / (1.0 + math.exp(-k * (x - c)))

            else:
                # For other component types, use a default normalization
                # Assume 0.05 is a good rate (1 entity every 20 time units)
                expected_rate = 0.05
                if throughput_rate > 0:
                    throughput_metric = min(throughput_rate / expected_rate, 1.0)
                    # Apply diminishing returns for very high throughput
                    if throughput_metric > 0.8:
                        throughput_metric = 0.8 + (throughput_metric - 0.8) * 0.5

            # Ensure the result is in the range [0, 1]
            throughput_metric = max(0.0, min(1.0, throughput_metric))

        except Exception as e:
            # Log error but continue with default value
            print(f"Error calculating throughput metric: {e}")

        return throughput_metric

    def _calculate_bottleneck_metric(self) -> float:
        """
        Calculate bottleneck potential metric.

        This metric measures how often the component causes delays in the workflow.
        Lower bottleneck potential is better.

        Returns:
            Normalized bottleneck metric (0-1 scale, higher is better)
        """
        # Default to best score (no bottleneck)
        bottleneck_metric = 1.0

        try:
            # Skip for generators as they typically don't have queues
            if self.component_type == "generator":
                return bottleneck_metric

            # Get component data
            component_data = self.csv_scraper.components_data.get(self.component_id, {})
            actions = component_data.get("actions", [])

            # Calculate queue metrics
            queue_lengths = []
            for action in actions:
                if action["action"] == "QUEUED" and isinstance(action.get("values"), dict):
                    queue_length = action["values"].get("queue_length")
                    if queue_length is not None and isinstance(queue_length, (int, float)):
                        queue_lengths.append(queue_length)

            # Calculate average queue length
            avg_queue_length = np.mean(queue_lengths) if queue_lengths else 0

            # Calculate wait times
            wait_times = self.csv_scraper.calculate_wait_times(self.component_id)
            avg_wait_time = wait_times.get("mean", 0) if isinstance(wait_times, dict) else 0

            # Get processing time for comparison
            proc_time = self.metrics.get("in_out_processing", {}).get("mean", 0)

            # Calculate bottleneck score based on multiple factors
            bottleneck_factors = []

            # Factor 1: Queue length relative to throughput
            # Higher queue length indicates potential bottleneck
            if avg_queue_length > 0:
                throughput = self.metrics.get("in_out_processing", {}).get("count", 0)
                if throughput > 0:
                    queue_factor = 1.0 / (1.0 + avg_queue_length / throughput)
                    bottleneck_factors.append(queue_factor)

            # Factor 2: Wait time relative to processing time
            # Higher wait-to-processing ratio indicates bottleneck
            if proc_time > 0 and avg_wait_time > 0:
                wait_ratio = avg_wait_time / proc_time
                wait_factor = 1.0 / (1.0 + wait_ratio)
                bottleneck_factors.append(wait_factor)

            # Factor 3: Utilization as bottleneck indicator
            # Very high utilization can indicate bottleneck
            utilization = self.metrics.get("utilization", 0) / 100.0
            if utilization > 0.9:  # Only consider high utilization
                util_factor = 1.0 - (utilization - 0.9) * 5.0  # Linear penalty
                util_factor = max(0.5, util_factor)  # Don't penalize too much
                bottleneck_factors.append(util_factor)

            # Combine factors if we have any
            if bottleneck_factors:
                # Use geometric mean to combine factors
                # This ensures that if any factor is very low, the overall score is affected
                bottleneck_metric = np.exp(np.mean(np.log([max(0.01, f) for f in bottleneck_factors])))

            # Ensure the result is in the range [0, 1]
            bottleneck_metric = max(0.0, min(1.0, bottleneck_metric))

        except Exception as e:
            # Log error but continue with default value (no bottleneck)
            print(f"Error calculating bottleneck metric: {e}")

        return bottleneck_metric

    def _calculate_position_metric(self) -> float:
        """
        Calculate workflow position impact metric.

        This metric measures the component's importance in the overall workflow
        based on its position and connectivity.

        Returns:
            Normalized position metric (0-1 scale, higher is better)
        """
        # Default to neutral impact
        position_metric = 0.5

        try:
            component_data = self.csv_scraper.components_data.get(self.component_id, {})

            if self.component_type == "generator":
                # Generators are at the start of the workflow
                # Their optimization is important as they affect everything downstream
                position_metric = 0.8

                # Adjust based on how many entities they generate
                action_counts = self.metrics.get("action_counts", {})
                generate_count = action_counts.get("GENERATE", 0)

                # More generations = more important
                if generate_count > 0:
                    # Bonus for high generation count (up to +0.1)
                    position_metric += min(0.1, generate_count / 100.0)

                # Cap at 0.95 (not quite perfect)
                position_metric = min(0.95, position_metric)

            elif self.component_type == "resource":
                # Resources could be anywhere in the workflow
                # Use container interactions as a proxy for centrality
                container_interactions = set()

                # Count unique container IDs that interact with this component
                for action in component_data.get("actions", []):
                    if isinstance(action.get("PDV"), dict) and "containerId" in action["PDV"]:
                        container_interactions.add(action["PDV"]["containerId"])

                # More interactions = more central = more important
                interaction_count = len(container_interactions)

                # Normalize with diminishing returns
                # 0 interactions -> 0.3
                # 10 interactions -> 0.7
                # 20+ interactions -> 0.9
                if interaction_count == 0:
                    position_metric = 0.3
                elif interaction_count < 10:
                    position_metric = 0.3 + (interaction_count / 10.0) * 0.4
                else:
                    position_metric = 0.7 + min(0.2, (interaction_count - 10) / 50.0)

            else:
                # For other component types, use action count as a proxy for importance
                action_count = len(component_data.get("actions", []))

                # More actions = more important
                if action_count == 0:
                    position_metric = 0.3  # Low importance if no actions
                elif action_count < 50:
                    position_metric = 0.3 + (action_count / 50.0) * 0.4
                else:
                    position_metric = 0.7 + min(0.2, (action_count - 50) / 200.0)

            # Ensure the result is in the range [0, 1]
            position_metric = max(0.0, min(1.0, position_metric))

        except Exception as e:
            # Log error but continue with default value
            print(f"Error calculating position metric: {e}")

        return position_metric

    def _create_optimization_score_card(self) -> CardConfig:
        """
        Create a card showing the component's optimization score.

        The card displays the overall optimization score (0-100) with a trend
        indicator and label that reflects the optimization level.

        Returns:
            CardConfig object for a metric card
        """
        optimization_data = self.metrics.get("optimization_score", {})
        score = optimization_data.get("score", 0)

        # Determine trend direction and label based on score
        if score >= 60:
            trend_direction = TrendDirection.UP
            if score >= 85:
                trend_label = "Excellent Optimization"
            elif score >= 70:
                trend_label = "Well Optimized"
            else:  # 60-70
                trend_label = "Good Optimization"
        else:  # < 60
            trend_direction = TrendDirection.DOWN
            if score >= 40:
                trend_label = "Average Optimization"
            elif score >= 25:
                trend_label = "Needs Improvement"
            else:
                trend_label = "Requires Optimization"

        # Create description based on component type
        if self.component_type == "generator":
            description = "Overall generator optimization level"
        elif self.component_type == "resource":
            description = "Overall resource optimization level"
        else:
            description = "Overall component optimization level"

        return ChartBuilder.create_metric_card(
            header="Optimization Score",
            description=description,
            value=score,
            value_suffix="/100",
            value_formatting=ValueFormatting.NUMBER,
            trend_value=score,
            trend_direction=trend_direction,
            trend_label=trend_label,
            cols=1,
            rows=1
        )

    def _create_optimization_metrics_chart(self) -> ChartConfig:
        """
        Create a chart showing the breakdown of optimization metrics.

        This chart displays each optimization metric's contribution to the overall score,
        sorted by value in descending order. It also includes the weight of each metric
        to show its relative importance in the calculation.

        Returns:
            ChartConfig object for a bar chart
        """
        optimization_data = self.metrics.get("optimization_score", {})
        normalized_metrics = optimization_data.get("normalized_metrics", {})
        weights = optimization_data.get("weights", {})

        # Create data points for each metric
        score_points = []
        weight_points = []

        # Define friendly names for metrics
        metric_friendly_names = {
            "processing_time_efficiency": "Processing Speed",
            "utilization": "Resource Utilization",
            "throughput": "Throughput Rate",
            "bottleneck_potential": "Flow Efficiency",
            "workflow_position": "Workflow Impact"
        }

        # Create data points with friendly names and sort by score
        metric_data = []
        for metric, value in normalized_metrics.items():
            friendly_name = metric_friendly_names.get(metric, metric.replace("_", " ").title())
            weight = weights.get(metric, 0) * 100  # Convert to percentage
            metric_data.append((friendly_name, value, weight))

        # Sort by score in descending order
        metric_data.sort(key=lambda x: x[1], reverse=True)

        # Create data points from sorted data
        for friendly_name, value, weight in metric_data:
            score_points.append(DataPoint(x=friendly_name, y=value))
            weight_points.append(DataPoint(x=friendly_name, y=weight))

        # Create series
        series = [
            Series(name="Score", data=score_points),
            Series(name="Weight (%)", data=weight_points)
        ]

        # Create description based on component type
        if self.component_type == "generator":
            description = "Factors contributing to generator optimization score"
        elif self.component_type == "resource":
            description = "Factors contributing to resource optimization score"
        else:
            description = "Factors contributing to component optimization score"

        # Create chart
        return ChartBuilder.create_bar_chart(
            header="Optimization Metrics",
            description=description,
            series=series,
            y_axis_label="Value",
            x_axis_label="Metric",
            cols=2,
            rows=1
        )


class GeneratorAnalytics(ComponentAnalytics):
    """
    Analytics for Generator components.

    This class provides specialized analytics for Generator components,
    focusing on generation rate, total entities created, and timing patterns.
    """

    def __init__(self, component_id: str, csv_scraper: CSVScraper):
        """Initialize Generator analytics."""
        super().__init__(component_id, "generator", csv_scraper)

    def generate_component_insights(self) -> ComponentOutput:
        """
        Generate Generator-specific insights and visualizations.

        Returns:
            ComponentOutput object with charts and cards
        """
        # Calculate performance metrics
        self.calculate_performance_metrics()

        # Create output container
        output = ComponentOutput(
            id=self.component_id,
            name=f"Generator {self.component_id}",
            type=self.component_type
        )

        # Add generation rate card
        generation_rate_card = self._create_generation_rate_card()
        output.add_card(generation_rate_card)

        # Add total entities card
        total_entities_card = self._create_total_entities_card()
        output.add_card(total_entities_card)

        # Add generation pattern chart
        generation_pattern_chart = self._create_generation_pattern_chart()
        output.add_chart(generation_pattern_chart)

        # Add efficiency card
        efficiency_card = self._create_efficiency_card()
        output.add_card(efficiency_card)

        # Add optimization score card
        optimization_score_card = self._create_optimization_score_card()
        output.add_card(optimization_score_card)

        # Add optimization metrics chart
        optimization_metrics_chart = self._create_optimization_metrics_chart()
        output.add_chart(optimization_metrics_chart)

        return output

    def _create_generation_rate_card(self) -> CardConfig:
        """
        Create a card showing generation rate metrics.

        Returns:
            CardConfig object
        """
        # Calculate generation rate (entities per time unit)
        component_data = self.csv_scraper.components_data.get(self.component_id, {})
        actions = component_data.get("actions", [])

        # Filter for GENERATE actions
        generate_actions = [a for a in actions if a["action"] == "GENERATE"]

        # Calculate rate
        if generate_actions:
            times = [a["time"] for a in generate_actions]
            time_range = max(times) - min(times) if len(times) > 1 else 1
            generation_rate = len(generate_actions) / time_range if time_range > 0 else 0
        else:
            generation_rate = 0

        return ChartBuilder.create_metric_card(
            header="Generation Rate",
            description="Entities generated per time unit",
            value=round(generation_rate, 2),
            value_formatting=ValueFormatting.NUMBER,
            cols=1,
            rows=1
        )

    def _create_total_entities_card(self) -> CardConfig:
        """
        Create a card showing total entities created.

        Returns:
            CardConfig object
        """
        # Count GENERATE actions
        action_counts = self.metrics.get("action_counts", {})
        total_entities = action_counts.get("GENERATE", 0)

        return ChartBuilder.create_metric_card(
            header="Total Entities",
            description="Total number of entities generated",
            value=total_entities,
            value_formatting=ValueFormatting.NUMBER,
            cols=1,
            rows=1
        )

    def _create_generation_pattern_chart(self) -> ChartConfig:
        """
        Create a chart showing generation timing patterns.

        Returns:
            ChartConfig object for a line chart
        """
        # Get component actions
        component_data = self.csv_scraper.components_data.get(self.component_id, {})
        actions = component_data.get("actions", [])

        # Filter for GENERATE actions and sort by time
        generate_actions = sorted(
            [a for a in actions if a["action"] == "GENERATE"],
            key=lambda x: x["time"]
        )

        # Create data points for generation times
        data_points = []
        for i, action in enumerate(generate_actions):
            data_points.append(DataPoint(x=str(i+1), y=action["time"]))

        # Create series
        series = Series(name="Generation Time", data=data_points)

        # Create chart
        return ChartBuilder.create_line_chart(
            header="Entity Generation Pattern",
            description="Timing of entity generation events",
            series=[series],
            y_axis_label="Simulation Time",
            x_axis_label="Entity Number",
            cols=2,
            rows=1
        )


class ResourceAnalytics(ComponentAnalytics):
    """
    Analytics for Resource components.

    This class provides specialized analytics for Resource components,
    focusing on utilization rate, queue statistics, and processing time distribution.
    """

    def __init__(self, component_id: str, csv_scraper: CSVScraper):
        """Initialize Resource analytics."""
        super().__init__(component_id, "resource", csv_scraper)

    def generate_component_insights(self) -> ComponentOutput:
        """
        Generate Resource-specific insights and visualizations.

        Returns:
            ComponentOutput object with charts and cards
        """
        # Calculate performance metrics
        self.calculate_performance_metrics()

        # Create output container
        output = ComponentOutput(
            id=self.component_id,
            name=f"Resource {self.component_id}",
            type=self.component_type
        )

        # Add utilization card
        utilization_card = self._create_utilization_card()
        output.add_card(utilization_card)

        # Add efficiency card
        efficiency_card = self._create_efficiency_card()
        output.add_card(efficiency_card)

        # Add processing time chart
        processing_time_chart = self._create_processing_time_chart()
        output.add_chart(processing_time_chart)

        # Add queue statistics chart
        queue_stats_chart = self._create_queue_statistics_chart()
        output.add_chart(queue_stats_chart)

        # Add queue length timeline chart
        queue_length_timeline_chart = self._create_queue_length_timeline_chart()
        output.add_chart(queue_length_timeline_chart)

        # Add container processing time chart
        container_processing_time_chart = self._create_container_processing_time_chart()
        output.add_chart(container_processing_time_chart)

        # Add processing time distribution chart
        processing_time_dist_chart = self._create_processing_time_distribution_chart()
        output.add_chart(processing_time_dist_chart)

        # Add optimization score card
        optimization_score_card = self._create_optimization_score_card()
        output.add_card(optimization_score_card)

        # Add optimization metrics chart
        optimization_metrics_chart = self._create_optimization_metrics_chart()
        output.add_chart(optimization_metrics_chart)

        return output

    def _create_queue_statistics_chart(self) -> ChartConfig:
        """
        Create a chart showing queue statistics.

        Returns:
            ChartConfig object for a bar chart
        """
        # Get component actions
        component_data = self.csv_scraper.components_data.get(self.component_id, {})
        actions = component_data.get("actions", [])

        # Filter for QUEUED actions
        queued_actions = [a for a in actions if a["action"] == "QUEUED"]

        # Extract queue lengths
        queue_lengths = []
        for action in queued_actions:
            if "values" in action and isinstance(action["values"], dict):
                queue_length = action["values"].get("queue_length")
                if queue_length is not None:
                    queue_lengths.append(queue_length)

        # Calculate statistics
        if queue_lengths:
            avg_queue = np.mean(queue_lengths)
            max_queue = max(queue_lengths)
            min_queue = min(queue_lengths)
            median_queue = np.median(queue_lengths)
        else:
            avg_queue = max_queue = min_queue = median_queue = 0

        # Create data points
        data_points = [
            DataPoint(x="Average", y=avg_queue),
            DataPoint(x="Maximum", y=max_queue),
            DataPoint(x="Minimum", y=min_queue),
            DataPoint(x="Median", y=median_queue)
        ]

        # Create series
        series = Series(name="Queue Length", data=data_points)

        # Create chart
        return ChartBuilder.create_bar_chart(
            header="Queue Statistics",
            description="Statistics about queue length",
            series=[series],
            y_axis_label="Queue Length",
            x_axis_label="Statistic",
            cols=2,
            rows=1
        )

    def _create_queue_length_timeline_chart(self) -> ChartConfig:
        """
        Create a chart showing queue length over time.

        This chart tracks the queue length at each time point when QUEUED, IN, or OUT actions occur,
        providing insights into how the queue length changes throughout the simulation.

        Returns:
            ChartConfig object for a line chart
        """
        try:
            # Get component actions
            component_data = self.csv_scraper.components_data.get(self.component_id, {})
            actions = component_data.get("actions", [])

            # Filter for QUEUED, IN, and OUT actions and sort by time
            relevant_actions = sorted(
                [a for a in actions if a["action"] in ["QUEUED", "IN", "OUT"]],
                key=lambda x: x["time"]
            )

            # Extract queue lengths and times
            data_points = []
            for action in relevant_actions:
                if "values" in action and isinstance(action["values"], dict):
                    queue_length = action["values"].get("queue_length")
                    time = action.get("time")
                    if queue_length is not None and time is not None:
                        data_points.append(DataPoint(x=str(time), y=float(queue_length)))

            # If no data points, create a placeholder chart
            if not data_points:
                return ChartBuilder.create_line_chart(
                    header="Queue Length Timeline",
                    description="No queue length data available",
                    series=[Series(name="Queue Length", data=[DataPoint(x="0", y=0)])],
                    y_axis_label="Queue Length",
                    x_axis_label="Simulation Time",
                    cols=2,
                    rows=1
                )

            # Create series
            series = Series(name="Queue Length", data=data_points)

            # Create chart
            return ChartBuilder.create_line_chart(
                header="Queue Length Timeline",
                description="Queue length over time during QUEUED, IN, and OUT actions",
                series=[series],
                y_axis_label="Queue Length",
                x_axis_label="Simulation Time",
                show_grid=True,
                show_legend=True,
                show_tooltip=True,
                cols=2,
                rows=1
            )
        except Exception as e:
            # If anything goes wrong, return a fallback chart
            print(f"Error creating queue length timeline chart: {str(e)}")
            return ChartBuilder.create_line_chart(
                header="Queue Length Timeline",
                description="Error generating chart",
                series=[Series(name="Queue Length", data=[DataPoint(x="0", y=0)])],
                y_axis_label="Queue Length",
                x_axis_label="Simulation Time",
                cols=2,
                rows=1
            )

    def _create_container_processing_time_chart(self) -> ChartConfig:
        """
        Create a chart showing processing time per container.

        This chart displays the total processing time for each container from QUEUED to OUT,
        with containers shown in sequence rather than using actual container IDs.

        Returns:
            ChartConfig object for a line chart
        """
        try:
            # Get component actions
            component_data = self.csv_scraper.components_data.get(self.component_id, {})
            actions = component_data.get("actions", [])

            # Sort actions by time
            sorted_actions = sorted(actions, key=lambda x: x["time"])

            # Track containers and their processing times
            processing_times = []

            # Track QUEUED actions
            queued_actions = []
            for action in sorted_actions:
                if action["action"] == "QUEUED":
                    queued_actions.append(action)

            # Track OUT actions
            out_actions = []
            for action in sorted_actions:
                if action["action"] == "OUT":
                    out_actions.append(action)

            print(f"Found {len(queued_actions)} QUEUED actions and {len(out_actions)} OUT actions for component {self.component_id}")

            # Method 1: Try to match by container ID
            matched_by_id = 0
            for queued_action in queued_actions:
                queued_time = queued_action["time"]
                queued_container_id = self._extract_container_id(queued_action)

                if not queued_container_id:
                    continue

                # Find matching OUT action with same container ID
                for out_action in out_actions:
                    out_time = out_action["time"]
                    out_container_id = self._extract_container_id(out_action)

                    if not out_container_id:
                        continue

                    # If container IDs match and OUT time is after QUEUED time
                    if queued_container_id == out_container_id and out_time > queued_time:
                        processing_time = out_time - queued_time
                        processing_times.append(processing_time)
                        matched_by_id += 1
                        # Mark as processed to avoid duplicate matches
                        out_action["_matched"] = True
                        break

            print(f"Matched {matched_by_id} container pairs by ID")

            # Method 2: If few matches by ID, try sequential matching
            if matched_by_id < min(len(queued_actions), len(out_actions)) / 2:
                print("Few matches by ID, trying sequential matching...")

                # Reset processing times if we're switching to sequential matching
                if matched_by_id > 0:
                    processing_times = []

                # Sort by time
                queued_actions = sorted(queued_actions, key=lambda x: x["time"])
                out_actions = sorted(out_actions, key=lambda x: x["time"])

                # Match sequentially (assuming FIFO processing)
                for i in range(min(len(queued_actions), len(out_actions))):
                    queued_time = queued_actions[i]["time"]
                    out_time = out_actions[i]["time"]

                    # Ensure OUT time is after QUEUED time
                    if out_time > queued_time:
                        processing_time = out_time - queued_time
                        processing_times.append(processing_time)

                print(f"Matched {len(processing_times)} container pairs sequentially")

            # Method 3: If still no matches, try to use IN/OUT pairs from metrics
            if not processing_times:
                print("No matches found, trying to use IN/OUT processing times from metrics...")
                proc_time_data = self.metrics.get("in_out_processing", {})
                times = proc_time_data.get("times", [])

                if times:
                    processing_times = times
                    print(f"Using {len(processing_times)} processing times from metrics")

            # Create data points for the chart
            data_points = []
            for i, processing_time in enumerate(processing_times, 1):
                # Use sequential container numbers
                data_points.append(DataPoint(x=f"Container {i}", y=float(processing_time)))

            # If no data points, create a placeholder chart
            if not data_points:
                print(f"No container processing time data available for component {self.component_id}")
                return ChartBuilder.create_line_chart(
                    header="Container Processing Times",
                    description="No container processing time data available",
                    series=[Series(name="Processing Time", data=[DataPoint(x="No Data", y=0)])],
                    y_axis_label="Processing Time",
                    x_axis_label="Container",
                    cols=2,
                    rows=1
                )

            # Create series
            series = Series(name="Processing Time", data=data_points)

            # Create chart
            return ChartBuilder.create_line_chart(
                header="Container Processing Times",
                description=f"Processing time for each container ({len(data_points)} containers)",
                series=[series],
                y_axis_label="Processing Time (time units)",
                x_axis_label="Container",
                show_grid=True,
                show_legend=True,
                show_tooltip=True,
                cols=2,
                rows=1
            )
        except Exception as e:
            # If anything goes wrong, return a fallback chart with detailed error
            error_msg = f"Error creating container processing time chart: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return ChartBuilder.create_line_chart(
                header="Container Processing Times",
                description=f"Error: {error_msg}",
                series=[Series(name="Processing Time", data=[DataPoint(x="Error", y=0)])],
                y_axis_label="Processing Time",
                x_axis_label="Container",
                cols=2,
                rows=1
            )

    def _create_processing_time_distribution_chart(self) -> ChartConfig:
        """
        Create a chart showing the distribution of processing times.

        Returns:
            ChartConfig object for a bar chart
        """
        try:
            # Get processing time data
            proc_time_data = self.metrics.get("in_out_processing", {})
            times = proc_time_data.get("times", [])
            is_estimated = proc_time_data.get("is_estimated", False)

            if not times:
                # Create empty chart if no data
                return ChartBuilder.create_bar_chart(
                    header="Processing Time Distribution",
                    description="No processing time data available",
                    series=[Series(name="Count", data=[DataPoint(x="No Data", y=0)])],
                    cols=2,
                    rows=1
                )

            # If we only have estimated data, create a simple chart
            if is_estimated:
                return ChartBuilder.create_bar_chart(
                    header="Processing Time Distribution",
                    description="Using estimated processing time",
                    series=[Series(name="Count", data=[DataPoint(x=f"Estimated: {round(times[0], 1)}", y=1)])],
                    cols=2,
                    rows=1
                )

            # If we have only one data point, create a simple chart
            if len(times) == 1:
                return ChartBuilder.create_bar_chart(
                    header="Processing Time Distribution",
                    description="Only one processing time data point available",
                    series=[Series(name="Count", data=[DataPoint(x=f"Time: {round(times[0], 1)}", y=1)])],
                    cols=2,
                    rows=1
                )

            # Create bins for histogram
            # Adjust number of bins based on data size
            bins = min(5, len(times))  # Use fewer bins for small datasets

            min_time = min(times)
            max_time = max(times)

            # Ensure we have a valid range
            if max_time > min_time:
                # Create histogram with evenly spaced bins
                hist, bin_edges = np.histogram(times, bins=bins)

                # Create data points
                data_points = []
                for i in range(len(hist)):
                    bin_label = f"{round(bin_edges[i], 1)}-{round(bin_edges[i+1], 1)}"
                    data_points.append(DataPoint(x=bin_label, y=float(hist[i])))

                # Create series
                series = Series(name="Count", data=data_points)

                # Create chart
                return ChartBuilder.create_bar_chart(
                    header="Processing Time Distribution",
                    description=f"Distribution of processing times ({len(times)} data points)",
                    series=[series],
                    y_axis_label="Count",
                    x_axis_label="Processing Time Range",
                    cols=2,
                    rows=1
                )
            else:
                # Handle the case where all times are the same
                return ChartBuilder.create_bar_chart(
                    header="Processing Time Distribution",
                    description="All processing times are identical",
                    series=[Series(name="Count", data=[DataPoint(x=f"Time: {round(min_time, 1)}", y=len(times))])],
                    cols=2,
                    rows=1
                )
        except Exception as e:
            # If anything goes wrong, return a fallback chart
            print(f"Error creating processing time distribution chart: {str(e)}")
            return ChartBuilder.create_bar_chart(
                header="Processing Time Distribution",
                description="Error generating chart",
                series=[Series(name="Count", data=[DataPoint(x="Error", y=0)])],
                y_axis_label="Count",
                x_axis_label="Processing Time Range",
                cols=2,
                rows=1
            )


class AnalyticsFactory:
    """
    Factory class for creating component-specific analytics instances.

    This class provides methods for creating the appropriate analytics class
    based on component type.
    """

    @staticmethod
    def create_analytics(component_id: str, component_type: str, csv_scraper: CSVScraper) -> ComponentAnalytics:
        """
        Create an appropriate analytics instance based on component type.

        Args:
            component_id: The ID of the component to analyze
            component_type: The type of the component (generator, resource, etc.)
            csv_scraper: The CSVScraper instance for accessing simulation data

        Returns:
            ComponentAnalytics instance appropriate for the component type
        """
        if component_type.lower() == "generator":
            return GeneratorAnalytics(component_id, csv_scraper)
        elif component_type.lower() == "resource":
            return ResourceAnalytics(component_id, csv_scraper)
        else:
            # For unknown component types, use a base implementation
            # that provides common analytics
            return BaseComponentAnalytics(component_id, component_type, csv_scraper)


class BaseComponentAnalytics(ComponentAnalytics):
    """
    Default implementation of ComponentAnalytics for unknown component types.

    This class provides basic analytics for component types that don't have
    specialized analytics classes.
    """

    def generate_component_insights(self) -> ComponentOutput:
        """
        Generate basic insights and visualizations for unknown component types.

        Returns:
            ComponentOutput object with charts and cards
        """
        # Calculate performance metrics
        self.calculate_performance_metrics()

        # Create output container
        output = ComponentOutput(
            id=self.component_id,
            name=f"{self.component_type.capitalize()} {self.component_id}",
            type=self.component_type
        )

        # Add basic cards and charts

        # Add efficiency card if we have data
        if "efficiency" in self.metrics:
            efficiency_card = self._create_efficiency_card()
            output.add_card(efficiency_card)

        # Add utilization card if we have data
        if "utilization" in self.metrics:
            utilization_card = self._create_utilization_card()
            output.add_card(utilization_card)

        # Add processing time chart if we have data
        if "in_out_processing" in self.metrics and self.metrics["in_out_processing"]["count"] > 0:
            processing_time_chart = self._create_processing_time_chart()
            output.add_chart(processing_time_chart)

        # Add action counts chart
        action_counts_chart = self._create_action_counts_chart()
        output.add_chart(action_counts_chart)

        # Add optimization score card
        optimization_score_card = self._create_optimization_score_card()
        output.add_card(optimization_score_card)

        # Add optimization metrics chart
        optimization_metrics_chart = self._create_optimization_metrics_chart()
        output.add_chart(optimization_metrics_chart)

        return output

    def _create_action_counts_chart(self) -> ChartConfig:
        """
        Create a chart showing counts of different action types.

        Returns:
            ChartConfig object for a bar chart
        """
        # Get action counts
        action_counts = self.metrics.get("action_counts", {})

        # Create data points
        data_points = []
        for action, count in action_counts.items():
            data_points.append(DataPoint(x=action, y=count))

        # If no data points, add a placeholder
        if not data_points:
            data_points = [DataPoint(x="No Actions", y=0)]

        # Create series
        series = Series(name="Count", data=data_points)

        # Create chart
        return ChartBuilder.create_bar_chart(
            header="Action Counts",
            description="Number of occurrences of each action type",
            series=[series],
            y_axis_label="Count",
            x_axis_label="Action",
            cols=2,
            rows=1
        )
