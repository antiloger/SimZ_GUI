import json
import simpy
import numpy as np
from src.sim.chart import (
    CardConfig,
    ChartBuilder,
    ChartConfig,
    ChartSize,
    DataPoint,
    Series,
    ValueFormatting,
)
from src.sim.comp import Component, Generator, Resource
from src.sim.csvpaser import CSVScraper
from src.sim.sim_types import ComponentOutput, ComponentStore, GenTypeState, SimOutput
from src.sim.graph import WorkflowGraph
from src.sim.db import CsvLogger
from src.sim.analytics import AnalyticsFactory
from src.sim.table import Table
from pathlib import Path
from typing import Callable, Dict, Type, List, Any

compReg = {
    "generator": Generator,
    "resource": Resource,
}


class SimulationBuilder:
    compStore: ComponentStore
    genState: GenTypeState
    workflow: WorkflowGraph
    logger: CsvLogger
    env = simpy.Environment()

    def __init__(
        self,
        runName: str,
        ProjectPath: Path,
        runPath: Path,
        run_time: int | None = None,
        socketLog: Callable | None = None,
    ):
        self.runName = runName
        self.filePath = ProjectPath
        self.runPath = self.load_run_Path(runPath, runName)
        self.run_time = run_time
        self.compRegistry: Dict[str, Type[Component]] = compReg
        self.components: Dict[
            str, Component
        ] = {}  # Store component instances by their IDs
        self.socketLog = socketLog
        self.component_data_for_table: List[
            Dict[str, Any]
        ] = []  # Store component data for table visualization
        self.load()

    def Logger(self, message: str):
        if self.socketLog:
            self.socketLog(message)

    def load_run_Path(self, runPath: Path, runName: str):
        """
        Check if the runPath exists, if not create it with runName folder and return that path as runpath.
        """
        if not runPath.exists():
            runPath.mkdir(parents=True, exist_ok=True)
        temprunPath = runPath / runName
        if not temprunPath.exists():
            temprunPath.mkdir(parents=True, exist_ok=True)
        return temprunPath

    def load_compStore(self):
        file_path = self.filePath / "dataState.json"
        raw = json.loads(file_path.read_text())
        self.compStore = ComponentStore.model_validate(raw)
        self.Logger("[BUILD] component data loaded")

    def load_genState(self):
        file_path = self.filePath / "genState.json"
        raw = json.loads(file_path.read_text())
        self.genState = GenTypeState.model_validate(raw)
        self.Logger("[BUILD] generator state loaded")

    def load_workflow(self):
        file_path = self.filePath / "edge.json"
        raw = json.loads(file_path.read_text())
        if isinstance(raw, list) and all(isinstance(item, dict) for item in raw):
            self.workflow = WorkflowGraph(edges_data=raw)
        else:
            self.Logger("[ERROR] Invalid JSON format for workflow data")
            raise ValueError("Invalid JSON format: Expected a list of dictionaries")
        self.Logger("[BUILD] workflow data loaded")

    def get_component_with_name(self, id):
        for comp_id, comp in self.components.items():
            if comp_id == id:
                return comp.comp_name

    def create_logger(self):
        self.logger = CsvLogger(
            filename=str(self.runPath / f"{self.runName}.csv"),
            fieldnames=[
                "time",
                "component_id",
                "component_type",
                "action",
                "values",
                "PDV",
                "addition",
            ],
            buffer_size=1_048_576,
        )
        self.Logger("[BUILD] logger created")

    def load(self):
        self.load_compStore()
        self.load_genState()
        self.load_workflow()
        self.create_logger()

        # Set class-level references for all component types immediately after loading
        # This ensures the class variables are set before any instances are created
        for comp_class in self.compRegistry.values():
            comp_class.set_Gen_ref(self.genState)
            comp_class.set_workflow(self.workflow)
            comp_class.set_logger(self.logger)

    def build(self):
        # First, ensure the Component class has the necessary references
        # This is critical to ensure that all components created will have access to these
        Component.set_Gen_ref(self.genState)
        Component.set_workflow(self.workflow)
        Component.set_logger(self.logger)

        # Now build all components
        for comp_id, comp_data in self.compStore.root.items():
            if comp_data.category not in self.compRegistry:
                self.Logger(
                    f"[ERROR] Component type '{comp_data.category}' not registered."
                )
                raise ValueError(
                    f"Component type '{comp_data.typeName}' not registered."
                )

            comp_class = self.compRegistry[comp_data.category]

            # Create the component instance
            component = comp_class.create(
                env=self.env,
                compData=comp_data,
            )

            # Store the component in our local dictionary for easier access
            self.components[comp_id] = component

            # Debug output to confirm creation
            print(f"Created component {comp_id} of type {comp_data.category}")
            self.Logger(
                f"[BUILD] Created component {comp_id} of type {comp_data.category}"
            )

        # Verify that components are properly registered
        print(f"Registry size after build: {Component.get_registry_size()}")
        print(f"Registry keys: {Component.get_registry_keys()}")
        self.Logger(
            f"[LOAD] Registry size after build: {Component.get_registry_size()}"
        )

    def pprint_compStore(self):
        for name, comp in self.compStore.root.items():
            print(f"Component Name: {name}")
            print(f"Component Data: {comp}")
            print("-" * 20)

    def get_compStore(self):
        return self.compStore

    def find_root_comps(self) -> list[Component]:
        root_comps = []
        roots = self.workflow.get_roots()
        print(f"Found root components: {roots}")

        for root in roots:
            comp = Component.comp_from_registery(root)
            if comp is None:
                # Try to find it in our local components dictionary as a fallback
                comp = self.components.get(root)
                if comp is None:
                    raise ValueError(
                        f"Component '{root}' not found in component registry or local components."
                    )
                # Re-register it just to be safe
                Component.registry[root] = comp
                print(f"Re-registered component {root} in registry")

            root_comps.append(comp)
        return root_comps

    def save_simulation_output(self, runFolder: Path, data: SimOutput):
        """
        Save the simulation output to a CSV file.
        """
        if not runFolder.exists():
            runFolder.mkdir(parents=True, exist_ok=True)
        file_path = f"{runFolder}/simData.json"
        with open(file_path, "w") as f:
            # Use model_dump instead of dict (which is deprecated)
            try:
                json.dump(data.model_dump(), f, indent=4)
            except AttributeError:
                # Fallback for older versions that might not have model_dump
                json.dump(data.dict(), f, indent=4)
        self.Logger(f"[OUTPUT] Simulation output saved to {file_path}")

    def save_component_analytics(
        self, runFolder: Path, component_insights: List[ComponentOutput]
    ):
        """
        Save component-specific analytics data to separate JSON files.

        Args:
            runFolder: Path to the run folder
            component_insights: List of ComponentOutput objects with component-specific analytics
        """
        if not runFolder.exists():
            runFolder.mkdir(parents=True, exist_ok=True)

        # Create a components directory if it doesn't exist
        components_dir = runFolder / "components"
        if not components_dir.exists():
            components_dir.mkdir(parents=True, exist_ok=True)

        # Save each component's analytics to a separate file
        for insight in component_insights:
            try:
                # Add component-specific table data if available
                if (
                    hasattr(self, "component_data_for_table")
                    and self.component_data_for_table
                ):
                    # Find the data for this component
                    component_data = [
                        entry
                        for entry in self.component_data_for_table
                        if entry.get("id") == insight.id
                    ]
                    if component_data:
                        # Create a table with the component data
                        component_table = Table.create_component_table(
                            components_data=component_data,
                            title=f"{insight.name} Details",
                            description=f"Detailed metrics for {insight.name}",
                        )
                        # Add the table to the component output
                        insight.add_table(component_table)

                file_path = components_dir / f"component_analytics_{insight.id}.json"
                with open(file_path, "w") as f:
                    # Use model_dump instead of dict (which is deprecated)
                    try:
                        json.dump(insight.model_dump(), f, indent=4)
                    except AttributeError:
                        # Fallback for older versions that might not have model_dump
                        json.dump(insight.dict(), f, indent=4)
                self.Logger(
                    f"[OUTPUT] Component analytics for {insight.id} saved to {file_path}"
                )
            except Exception as e:
                self.Logger(
                    f"[ERROR] Failed to save component analytics for {insight.id}: {e}"
                )

    def save_component_names(self, runFolder: Path):
        """
        Save component ID-name mappings to a JSON file.

        This method collects all component IDs and their corresponding names
        and saves them to a JSON file in the run folder.

        Args:
            runFolder: Path to the run folder
        """
        if not runFolder.exists():
            runFolder.mkdir(parents=True, exist_ok=True)

        # Create a dictionary of component IDs and names
        component_names = {}

        # Get component names from the components dictionary
        for comp_id, comp in self.components.items():
            component_names[comp_id] = comp.comp_name

        # Also check the Component registry for any components not in self.components
        for comp_id in Component.get_registry_keys():
            if comp_id not in component_names:
                component = Component.comp_from_registery(comp_id)
                if component:
                    component_names[comp_id] = component.comp_name

        # Save the component names to a JSON file
        file_path = runFolder / "component_names.json"
        try:
            with open(file_path, "w") as f:
                json.dump(component_names, f, indent=4)
            self.Logger(f"[OUTPUT] Component names saved to {file_path}")
        except Exception as e:
            self.Logger(f"[ERROR] Failed to save component names: {e}")

    def generate_component_insights(
        self, csv_scraper: CSVScraper
    ) -> List[ComponentOutput]:
        """
        Generate insights for all components in the simulation.

        This method uses the analytics system to generate insights for each component
        based on its type and behavior.

        Args:
            csv_scraper: CSVScraper instance for accessing simulation data

        Returns:
            List of ComponentOutput objects with charts and cards
        """
        insights = []

        # Get all components from the registry
        for comp_id in Component.get_registry_keys():
            try:
                # Get the component from the registry
                component = Component.comp_from_registery(comp_id)
                if component:
                    # Generate insights for this component
                    component_insights = component.generate_component_insights(
                        csv_scraper
                    )
                    insights.append(component_insights)
            except Exception as e:
                print(
                    f"Warning: Could not generate insights for component {comp_id}: {e}"
                )

        return insights

    def output(self, csvScaraper: CSVScraper) -> SimOutput:
        """
        Generate visualization output from simulation data.
        Enhanced to handle dynamic data structures and missing fields.
        """
        output = SimOutput(id=self.runName)

        # Get time range with error handling
        try:
            simTime = csvScaraper.get_time_range()
            max_time = simTime.get("max_time", 0)

            e_time_card = CardConfig(
                header="Simulation Time (last record)",
                description="ending time of the simulation",
                value=max_time,
                valueFormatting=ValueFormatting.NUMBER,
                size=ChartSize(cols=1, rows=1),
                valuePrefix=None,
                valueSuffix=None,
            )
            output.add_card(e_time_card)
        except Exception as e:
            print(f"Warning: Could not create time range card: {e}")

        # Total components card
        try:
            total_comp = CardConfig(
                header="Total Components",
                description="Total number of components in the simulation",
                value=len(Component.registry),
                valueFormatting=ValueFormatting.NUMBER,
                size=ChartSize(cols=1, rows=1),
                valuePrefix=None,
                valueSuffix=None,
            )
            output.add_card(total_comp)
        except Exception as e:
            print(f"Warning: Could not create total components card: {e}")

        # Total containers card
        try:
            # Get container count data
            containerData = csvScaraper.count_containers_duckdb()
            container_count = containerData.get("total_containers", 0)

            # Print debug information
            print(f"Container count from count_containers_duckdb: {container_count}")

            # Double-check with a direct count from the CSV data
            direct_count = len(csvScaraper.get_unique_container_ids())
            print(f"Direct container count from CSV: {direct_count}")

            # Use the direct count if available, otherwise fall back to the original count
            final_count = direct_count if direct_count > 0 else container_count

            # Create the card with the verified count
            total_container = CardConfig(
                header="Total Containers",
                description="Total number of Containers in the simulation",
                value=final_count,
                valueFormatting=ValueFormatting.NUMBER,
                size=ChartSize(cols=1, rows=1),
                valuePrefix=None,
                valueSuffix=None,
            )
            output.add_card(total_container)
        except Exception as e:
            print(f"Warning: Could not create total containers card: {e}")

        # Total GenTypes card
        try:
            total_genType = CardConfig(
                header="Total GenTypes",
                description="Total number of GenTypes in the simulation",
                value=self.genState.total_count(),
                valueFormatting=ValueFormatting.NUMBER,
                size=ChartSize(cols=1, rows=1),
                valuePrefix=None,
                valueSuffix=None,
            )
            output.add_card(total_genType)
        except Exception as e:
            print(f"Warning: Could not create total GenTypes card: {e}")

        # Container Count Timeline Chart - Created here but will be added to output later
        container_count_chart = None
        try:
            # Get container count timeline data
            container_count_data = csvScaraper.get_container_count_timeline()

            # Check if we have the expected data structure
            if (
                "data_points" in container_count_data
                and container_count_data["data_points"]
            ):
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
                    description="Number of containers being processed at each time point. X-axis: Simulation time. Y-axis: Number of containers in the system.",
                    series=[container_count_series],
                    show_legend=True,
                    show_grid=True,
                    show_tooltip=True,
                    cols=4,
                    rows=1,
                )

                print(
                    f"Created container count timeline chart with {len(container_count_series.data)} data points"
                )
                # Note: We'll add this chart to the output later to maintain the requested order
        except Exception as e:
            print(f"Warning: Could not create container count timeline chart: {e}")

        # GenType Distribution Pie Chart
        try:
            # Get GenType distribution data
            gentype_data = csvScaraper.get_gentype_distribution()

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
                    description="Percentage breakdown of different GenTypes in the simulation. Pie segments represent the percentage of each GenType in the system.",
                    series=[gentype_series],
                    show_legend=True,
                    show_tooltip=True,
                    show_labels=True,
                    cols=2,
                    rows=1,
                )

                # Add the chart to output
                output.add_chart(gentype_chart)
                print(
                    f"Created GenType distribution pie chart with {len(gentype_series.data)} data points"
                )
        except Exception as e:
            print(f"Warning: Could not create GenType distribution pie chart: {e}")

        # Pie chart for component categories
        try:
            comp_Cat_data = csvScaraper.get_component_types().to_dict()

            # Check if we have the expected data structure
            if (
                "unique_components" in comp_Cat_data
                and "component_type" in comp_Cat_data
            ):
                comp_Cat_data_sum = sum(comp_Cat_data["unique_components"].values())

                if comp_Cat_data_sum > 0:  # Avoid division by zero
                    comp_cat_series = Series(
                        name="Categories",
                        data=[
                            DataPoint(
                                x=comp_Cat_data["component_type"][i],
                                y=(
                                    comp_Cat_data["unique_components"][i]
                                    / comp_Cat_data_sum
                                )
                                * 100,
                            )
                            for i in comp_Cat_data["component_type"]
                        ],
                    )

                    component_cat = ChartBuilder.create_pie_chart(
                        header="Component Categories",
                        description="Distribution of component categories. Pie segments represent the percentage of each component type in the simulation.",
                        series=[comp_cat_series],
                        cols=2,
                        rows=1,
                    )

                    output.add_chart(component_cat)
        except Exception as e:
            print(f"Warning: Could not create component categories chart: {e}")

        # Bar chart of action counts
        try:
            act_count = csvScaraper.get_action_counts().to_dict()

            # Check if we have the expected data structure
            if "action" in act_count and "count" in act_count:
                act_series = []

                for i in act_count["action"]:
                    try:
                        act_series.append(
                            DataPoint(
                                x=act_count["action"][i], y=float(act_count["count"][i])
                            )
                        )
                    except (ValueError, TypeError, IndexError) as e:
                        print(
                            f"Warning: Could not process action count data point: {e}"
                        )

                if act_series:  # Only create chart if we have data points
                    act_chart = ChartBuilder.create_bar_chart(
                        header="Action Counts",
                        description="Counts of actions performed by components. X-axis: Action types (IN, OUT, QUEUED, etc.). Y-axis: Number of occurrences.",
                        series=[Series(name="Actions", data=act_series)],
                        cols=2,
                        rows=1,
                    )

                    output.add_chart(act_chart)
        except Exception as e:
            print(f"Warning: Could not create action counts chart: {e}")

        # Efficiency and processing time charts
        try:
            eff_pro_count = csvScaraper.get_ep_chart_data()

            # Check if we have the expected data structure
            if (
                "component_efficiency" in eff_pro_count
                and "processing_times" in eff_pro_count
            ):
                eff_count = eff_pro_count["component_efficiency"]
                pro_count = eff_pro_count["processing_times"]

                # Create efficiency data points with error handling
                eff_data_points = []
                for key, value in eff_count.items():
                    try:
                        comp_name = self.get_component_with_name(key) or "Unknown"
                        eff_data_points.append(DataPoint(x=comp_name, y=value))
                    except Exception as e:
                        print(f"Warning: Could not process efficiency data point: {e}")

                # Create processing time data points with error handling
                pro_data_points = []
                for key, value in pro_count.items():
                    try:
                        comp_name = self.get_component_with_name(key) or "Unknown"
                        pro_data_points.append(DataPoint(x=comp_name, y=float(value)))
                    except (ValueError, TypeError) as e:
                        print(
                            f"Warning: Could not process processing time data point: {e}"
                        )

                # Create efficiency chart if we have data points
                if eff_data_points:
                    line_eff_chart = ChartBuilder.create_line_chart(
                        header="Average Efficiency Times (components)",
                        description="Efficiency of components over time. X-axis: Component names. Y-axis: Efficiency values (0-1 scale).",
                        series=[Series(name="components", data=eff_data_points)],
                        cols=2,
                        rows=1,
                    )
                    output.add_chart(line_eff_chart)

                # Create processing time chart if we have data points
                if pro_data_points:
                    pro_eff_chart = ChartBuilder.create_line_chart(
                        header="Average Processing Time (components)",
                        description="Processing times of components over time. X-axis: Component names. Y-axis: Average processing time (time units).",
                        series=[Series(name="components", data=pro_data_points)],
                        cols=2,
                        rows=1,
                    )
                    output.add_chart(pro_eff_chart)

                    # Generate component comparison visualization right after the processing time chart
                    try:
                        # Generate insights for all components
                        component_insights = self.generate_component_insights(csvScaraper)

                        # Generate component comparison visualization
                        comparison_output = self.generate_component_comparison(
                            csvScaraper, component_insights
                        )

                        # Add the optimization comparison chart to the output if available
                        if (
                            "optimization_chart" in comparison_output
                            and comparison_output["optimization_chart"]
                        ):
                            output.add_chart(comparison_output["optimization_chart"])
                            print("Added component optimization comparison chart to output")
                    except Exception as e:
                        print(f"Warning: Could not create component optimization chart: {e}")
        except Exception as e:
            print(f"Warning: Could not create efficiency/processing time charts: {e}")

        # Component processing time chart (line chart)
        try:
            proc_time_chart_data = (
                csvScaraper.get_component_processing_time_chart_data()
            )
            proc_time_series = []

            # Check if we have the line_chart_data in the result
            if "line_chart_data" in proc_time_chart_data:
                line_data = proc_time_chart_data["line_chart_data"]

                # Check if we have the expected data structure
                if "timeline" in line_data and "components" in line_data:
                    timeline = line_data["timeline"]

                    # Create a series for each component
                    for comp_group in line_data["components"]:
                        # Process each component in the group
                        if "components" in comp_group:
                            for component in comp_group["components"]:
                                # Check if we have the expected component data
                                if (
                                    "name" in component
                                    and "processing_times" in component
                                ):
                                    # Create data points for this component
                                    data_points = []
                                    for i, time in enumerate(timeline):
                                        try:
                                            if i < len(component["processing_times"]):
                                                data_points.append(
                                                    DataPoint(
                                                        x=str(time),
                                                        y=float(
                                                            component[
                                                                "processing_times"
                                                            ][i]
                                                        ),
                                                    )
                                                )
                                        except (ValueError, TypeError, IndexError) as e:
                                            print(
                                                f"Warning: Could not process time series data point: {e}"
                                            )

                                    # Add series for this component
                                    if data_points:
                                        proc_time_series.append(
                                            Series(
                                                name=component["name"], data=data_points
                                            )
                                        )

            # Debug information to help diagnose the issue
            print(
                f"Found {len(proc_time_series)} component series for processing time chart"
            )
            for series in proc_time_series:
                print(f"  - Series: {series.name} with {len(series.data)} data points")

            # Create a new chart showing component processing state over time (active/inactive)
            continuous_series = []

            # Get continuous data from the chart data
            continuous_data = proc_time_chart_data.get("continuous_data", {})
            timeline = proc_time_chart_data.get("continuous_chart_data", {}).get(
                "timeline", []
            )

            if continuous_data and timeline:
                print(
                    f"Creating continuous processing state chart with {len(continuous_data)} components"
                )

                # Create a series for each component showing its processing state over time
                for comp_id, state_data in continuous_data.items():
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
                        continuous_series.append(
                            Series(name=state_data["name"], data=data_points)
                        )

                # Create the continuous processing state chart
                if continuous_series:
                    continuous_state_chart = ChartBuilder.create_area_chart(
                        header="Component Processing State Over Time",
                        description="Shows when each component is actively processing (1) or idle (0). X-axis: Simulation time. Y-axis: Processing state where 1 means active and 0 means idle.",
                        series=continuous_series,
                        show_legend=True,
                        show_grid=True,
                        show_tooltip=True,
                        cols=4,
                        rows=1,
                    )
                    # Add the chart to output
                    output.add_chart(continuous_state_chart)

                    # Add the Container Count Timeline chart after the Component Processing State Over Time chart
                    if container_count_chart:
                        output.add_chart(container_count_chart)
                        print("Added container count timeline chart after component processing state chart")

            # Create the original processing time chart if we have data
            if proc_time_series:
                # Ensure we're showing all components by setting show_legend to True
                component_proc_time_chart = ChartBuilder.create_line_chart(
                    header="Component Processing Times (IN to OUT)",
                    description="Processing time duration between IN and OUT actions for each component. X-axis: Simulation time. Y-axis: Processing time in time units.",
                    series=proc_time_series,
                    show_legend=True,  # Ensure legend is shown to distinguish components
                    show_grid=True,
                    show_tooltip=True,
                    cols=4,
                    rows=1,
                )
                # Add the chart to output
                output.add_chart(component_proc_time_chart)

                # Create an additional chart for average processing time by component type
                try:
                    # Group components by type and calculate average processing times
                    type_avg_times = {}

                    for comp_group in proc_time_chart_data.get(
                        "line_chart_data", {}
                    ).get("components", []):
                        comp_type = comp_group.get("type", "unknown")

                        # Calculate average processing time for this component type
                        total_time = 0
                        count = 0

                        for component in comp_group.get("components", []):
                            avg_time = component.get("avg_processing_time", 0)
                            if avg_time > 0:
                                total_time += avg_time
                                count += 1

                        if count > 0:
                            type_avg_times[comp_type] = total_time / count

                    # Create data points for the chart
                    avg_data_points = []
                    for comp_type, avg_time in type_avg_times.items():
                        avg_data_points.append(DataPoint(x=comp_type, y=avg_time))

                    # Create the chart if we have data
                    if avg_data_points:
                        avg_proc_time_chart = ChartBuilder.create_bar_chart(
                            header="Average Processing Time by Component Type",
                            description="Average time between IN and OUT actions for each component type. X-axis: Component types. Y-axis: Average processing time in time units.",
                            series=[
                                Series(name="Avg Processing Time", data=avg_data_points)
                            ],
                            cols=2,
                            rows=1,
                        )
                        output.add_chart(avg_proc_time_chart)

                        # Create a chart showing total cumulative processing time for each component
                        cumulative_data_points = []

                        for comp_id, comp_data in proc_time_chart_data.get(
                            "components", {}
                        ).items():
                            # Calculate total processing time for this component
                            total_time = sum(
                                entry.get("processing_time", 0)
                                for entry in comp_data.get("processing_data", [])
                            )

                            if total_time > 0:
                                cumulative_data_points.append(
                                    DataPoint(
                                        x=comp_data.get("name", comp_id), y=total_time
                                    )
                                )

                        # Sort by total processing time (descending)
                        cumulative_data_points.sort(key=lambda p: p.y, reverse=True)

                        # Create the chart if we have data
                        if cumulative_data_points:
                            cumulative_chart = ChartBuilder.create_bar_chart(
                                header="Total Processing Time by Component",
                                description="Cumulative time spent processing containers for each component. X-axis: Component names. Y-axis: Total processing time in time units.",
                                series=[
                                    Series(
                                        name="Total Processing Time",
                                        data=cumulative_data_points,
                                    )
                                ],
                                cols=2,
                                rows=1,
                            )
                            output.add_chart(cumulative_chart)
                except Exception as e:
                    print(
                        f"Warning: Could not create average processing time chart: {e}"
                    )
        except Exception as e:
            print(f"Warning: Could not create component processing time chart: {e}")

        # Generate simulation-wide metrics table
        try:
            # Create a metrics table with overall simulation statistics
            metrics_data = []

            # Add time metrics
            time_range = csvScaraper.get_time_range()
            metrics_data.append(
                {
                    "metric": "Simulation Duration",
                    "value": time_range.get("max_time", 0),
                    "unit": "time units",
                    "category": "Time",
                }
            )

            # Add component metrics
            metrics_data.append(
                {
                    "metric": "Total Components",
                    "value": len(Component.registry),
                    "unit": "count",
                    "category": "Components",
                }
            )

            # Add container metrics
            container_count = len(csvScaraper.get_unique_container_ids())
            metrics_data.append(
                {
                    "metric": "Total Containers",
                    "value": container_count,
                    "unit": "count",
                    "category": "Containers",
                }
            )

            # Add processing metrics
            try:
                # Get average processing time across all components
                proc_times = csvScaraper.calculate_all_processing_times()
                if proc_times:
                    metrics_data.append(
                        {
                            "metric": "Average Processing Time",
                            "value": proc_times.get("mean", 0),
                            "unit": "time units",
                            "category": "Processing",
                        }
                    )
                    metrics_data.append(
                        {
                            "metric": "Maximum Processing Time",
                            "value": proc_times.get("max", 0),
                            "unit": "time units",
                            "category": "Processing",
                        }
                    )
            except Exception as e:
                print(f"Warning: Could not calculate processing metrics: {e}")

            # Create and add the metrics table directly to the output
            output.add_table(
                Table.create_metrics_table(
                    metrics_data=metrics_data,
                    title="Simulation Metrics",
                    description="Key metrics from the simulation run",
                    group_by="category",
                )
            )

        except Exception as e:
            print(f"Warning: Could not create simulation metrics table: {e}")

        # Generate component-specific insights
        try:
            # Generate insights for all components but don't add them to the main output
            # They are now stored in separate files by the save_component_analytics method
            # Note: We already generated component_insights earlier for the optimization chart
            # So we'll only generate them here if they don't exist yet
            if not 'component_insights' in locals() or component_insights is None:
                component_insights = self.generate_component_insights(csvScaraper)

            # Generate component comparison visualization if not already done
            if not 'comparison_output' in locals() or comparison_output is None:
                comparison_output = self.generate_component_comparison(
                    csvScaraper, component_insights
                )

            # Add the component comparison table to the output if available
            if (
                "comparison_table" in comparison_output
                and comparison_output["comparison_table"]
            ):
                output.add_table(comparison_output["comparison_table"])
                print("Added component comparison table to output")

            # Add a note about component analytics being available separately

            # Add a summary table with component information
            try:
                # Create a table with basic component information
                component_table_data = []

                for insight in component_insights:
                    # Get component properties if available
                    component_properties = {}

                    # For each component, try to get its properties from the CSV data
                    component_data = csvScaraper.components_data.get(insight.id, {})

                    # Extract component type
                    component_type = insight.type

                    # Extract metrics based on component type
                    if component_type == "generator":
                        # For generators, include generation count
                        action_counts = component_data.get("action_counts", {})
                        generation_count = action_counts.get("GENERATE", 0)
                        component_properties["generation_count"] = generation_count

                    elif component_type == "resource":
                        # For resources, include capacity and utilization
                        capacity = component_data.get("capacity", 1)
                        utilization = component_data.get("utilization", 0)
                        component_properties["capacity"] = capacity
                        component_properties["utilization"] = utilization

                    # Create a data point for this component
                    component_table_data.append(
                        DataPoint(
                            x=insight.id,
                            y=1,  # Placeholder value, not used for tables
                        )
                    )

                    # Create a component data entry for component-specific analytics
                    component_entry = {
                        "id": insight.id,
                        "name": insight.name,
                        "type": insight.type,
                    }

                    # Add component-specific properties
                    if component_type == "generator":
                        component_entry["generation_count"] = component_properties.get(
                            "generation_count", 0
                        )
                    elif component_type == "resource":
                        component_entry["capacity"] = component_properties.get(
                            "capacity", 1
                        )
                        component_entry["utilization"] = component_properties.get(
                            "utilization", 0
                        )

                    # Add processing time metrics if available
                    processing_metrics = component_data.get("processing_metrics", {})
                    if processing_metrics:
                        component_entry["avg_processing_time"] = processing_metrics.get(
                            "mean", 0
                        )
                        component_entry["max_processing_time"] = processing_metrics.get(
                            "max", 0
                        )
                        component_entry["total_processed"] = processing_metrics.get(
                            "count", 0
                        )

                    # Add to the component data list for component-specific analytics
                    self.component_data_for_table.append(component_entry)

                # Note: We don't add component-specific table data to the main output
                # This data will be saved in separate component files
                # The Component Summary chart has been removed as it doesn't display properly
                # and doesn't correctly categorize component types
            except Exception as e:
                print(f"Warning: Could not create component summary table: {e}")

        except Exception as e:
            print(f"Warning: Could not generate component insights: {e}")

        return output

    def start(self):
        # Before starting, verify registry state
        print(f"Registry before start: {list(Component.registry.keys())}")

        root_comps = self.find_root_comps()
        for comp in root_comps:
            if comp is None:
                raise ValueError("Component is None, cannot start simulation.")
            self.env.process(comp.run(input=None))

        self.env.run(until=self.run_time)

    def run_all(self):
        # Before starting, verify registry state
        try:
            self.build()
            self.start()
        finally:
            if hasattr(self, "logger") and self.logger is not None:
                print("Closing logger...")
                self.logger.close()

    def generate_component_comparison(
        self, csv_scraper: CSVScraper, component_insights: List[ComponentOutput]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive component comparison visualization.

        This method creates:
        1. A radar chart comparing optimization metrics across all components
        2. A data table with key performance indicators for each component

        Args:
            csv_scraper: CSVScraper instance for accessing simulation data
            component_insights: List of ComponentOutput objects with component analytics

        Returns:
            Dictionary with comparison charts and tables
        """
        comparison_output = {}

        try:
            # 1. Create optimization metrics comparison chart
            optimization_chart = self._create_optimization_comparison_chart(
                component_insights
            )
            if optimization_chart:
                comparison_output["optimization_chart"] = optimization_chart

            # 2. Create component comparison table
            comparison_table = self._create_component_comparison_table(
                csv_scraper, component_insights
            )
            if comparison_table:
                comparison_output["comparison_table"] = comparison_table

        except Exception as e:
            print(f"Warning: Could not generate component comparison: {e}")

        return comparison_output

    def _create_optimization_comparison_chart(
        self, component_insights: List[ComponentOutput]
    ) -> ChartConfig:
        """
        Create a radar chart comparing optimization metrics across all components.

        Args:
            component_insights: List of ComponentOutput objects with component analytics

        Returns:
            ChartConfig object for a radar chart
        """
        try:
            # Check if we have any component insights
            if not component_insights:
                print(
                    "No component insights available for optimization comparison chart"
                )
                return self._create_fallback_optimization_chart()

            # Collect optimization metrics for each component
            component_metrics = []

            for insight in component_insights:
                # Find the optimization score data in the component's metrics
                optimization_data = None
                for chart in insight.dashboradData:
                    if (
                        hasattr(chart, "header")
                        and chart.header == "Optimization Metrics"
                        and hasattr(chart, "series")
                        and chart.series
                    ):
                        # Found the optimization metrics chart
                        optimization_data = (
                            chart.series[0].data if chart.series[0].data else []
                        )
                        break

                if optimization_data:
                    # Create a data point for this component with all its metrics
                    metrics = {}
                    for data_point in optimization_data:
                        metric_name = data_point.x
                        metric_value = data_point.y
                        metrics[metric_name] = metric_value

                    component_metrics.append(
                        {
                            "id": insight.id,
                            "name": insight.name,
                            "type": insight.type,
                            "metrics": metrics,
                        }
                    )

            if not component_metrics:
                print("No component metrics found for comparison chart")
                return self._create_fallback_optimization_chart()

            # Create series for each metric
            series = []

            # Define the metrics we want to include
            metric_names = [
                "Processing Speed",
                "Resource Utilization",
                "Throughput Rate",
                "Flow Efficiency",
                "Workflow Impact",
            ]

            # Create a series for each component
            for component in component_metrics:
                data_points = []

                # Create data points for each metric
                for metric_name in metric_names:
                    # Find the metric value for this component
                    metric_value = 0
                    for name, value in component["metrics"].items():
                        if name == metric_name:
                            metric_value = value
                            break

                    # Add the data point
                    data_points.append(DataPoint(x=metric_name, y=metric_value))

                # Create the series for this component
                series.append(
                    Series(
                        name=f"{component['name']} ({component['type']})",
                        data=data_points,
                    )
                )

            # Create the radar chart
            return ChartBuilder.create_radar_chart(
                header="Component Optimization Comparison",
                description="Comparison of optimization metrics across all components. Each axis represents a different optimization metric (0-100 scale). Higher values indicate better performance.",
                series=series,
                show_legend=True,
                show_tooltip=True,
                max_value=100,  # Set maximum value for better scaling
                cols=2,
                rows=1,
            )

        except Exception as e:
            print(f"Warning: Could not create optimization comparison chart: {e}")
            return self._create_fallback_optimization_chart()

    def _create_fallback_optimization_chart(self) -> ChartConfig:
        """
        Create a fallback optimization comparison chart when component insights are not available.

        This method creates a simple radar chart showing basic component metrics
        based on CSV data.

        Returns:
            ChartConfig object for a radar chart
        """
        try:
            # Try to get the CSV scraper from the current run
            csv_scraper = None
            try:
                csv_path = self.runPath / self.runName / f"{self.runName}.csv"
                if csv_path.exists():
                    from src.sim.csvpaser import CSVScraper

                    csv_scraper = CSVScraper(csv_path)
            except Exception as e:
                print(f"Warning: Could not create CSV scraper for fallback chart: {e}")

            if not csv_scraper:
                # Create a message chart indicating that optimization metrics are not available
                message_series = Series(name="Note", data=[DataPoint(x="No Data", y=0)])

                return ChartBuilder.create_bar_chart(
                    header="Component Optimization Comparison",
                    description="Optimization metrics are not available for this simulation. Run a simulation with component analytics enabled to see detailed optimization metrics. X-axis: Metrics. Y-axis: Values.",
                    series=[message_series],
                    cols=4,
                    rows=1,
                )

            # Get component names from CSV data
            component_names = {}
            try:
                # Try to load component names from component_names.json
                component_names_path = (
                    self.runPath / self.runName / "component_names.json"
                )
                if component_names_path.exists():
                    with open(component_names_path, "r") as f:
                        component_names = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load component names: {e}")

            # Get all component IDs from CSV data
            component_ids = list(csv_scraper.components_data.keys())

            # If no component IDs are found, try to extract them from the component_names.json file
            if not component_ids and component_names:
                component_ids = list(component_names.keys())

            # If we still don't have any component IDs, return the message chart
            if not component_ids:
                message_series = Series(name="Note", data=[DataPoint(x="No Data", y=0)])

                return ChartBuilder.create_bar_chart(
                    header="Component Optimization Comparison",
                    description="No component data found in this simulation. Run a simulation with components to see optimization metrics. X-axis: Metrics. Y-axis: Values.",
                    series=[message_series],
                    cols=4,
                    rows=1,
                )

            # Create series for each component
            series = []

            # Define the metrics we want to include
            metric_names = [
                "Processing Speed",
                "Resource Utilization",
                "Throughput Rate",
                "Flow Efficiency",
                "Workflow Impact",
            ]

            # Process each component to create data points
            for comp_id in component_ids:
                # Get component data
                component_data = csv_scraper.components_data.get(comp_id, {})

                # Get component type
                component_type = component_data.get("type", "unknown")

                # Get component name
                component_name = component_names.get(comp_id, comp_id)

                # Calculate basic metrics
                metrics = {}

                # 1. Processing Speed (based on processing time)
                processing_speed = 0
                try:
                    proc_times = csv_scraper.calculate_processing_time(comp_id)
                    if isinstance(proc_times, dict) and proc_times.get("mean", 0) > 0:
                        # Invert processing time to get speed (faster = higher score)
                        processing_speed = 100 / (1 + proc_times.get("mean", 0))
                        # Normalize to 0-100 scale
                        processing_speed = min(100, processing_speed * 10)
                except Exception:
                    pass
                metrics["Processing Speed"] = processing_speed

                # 2. Resource Utilization
                utilization = 0
                try:
                    util = csv_scraper.get_component_utilization(comp_id)
                    if isinstance(util, dict):
                        utilization = util.get(comp_id, 0)
                    else:
                        utilization = util

                    # Normalize to 0-100 scale with penalty for over-utilization
                    if utilization > 95:
                        utilization = 95 - (utilization - 95) * 2
                except Exception:
                    pass
                metrics["Resource Utilization"] = utilization

                # 3. Throughput Rate (based on processing count)
                throughput = 0
                try:
                    proc_times = csv_scraper.calculate_processing_time(comp_id)
                    if isinstance(proc_times, dict):
                        count = proc_times.get("count", 0)
                        # Normalize to 0-100 scale
                        throughput = min(100, count * 10)
                except Exception:
                    pass
                metrics["Throughput Rate"] = throughput

                # 4. Flow Efficiency (based on queue length for resources, generation rate for generators)
                flow_efficiency = 0
                try:
                    if component_type == "resource":
                        # For resources, calculate flow efficiency based on queue length
                        queue_lengths = []
                        for action in component_data.get("actions", []):
                            if action.get("action") == "QUEUED":
                                values = action.get("values", {})
                                if (
                                    isinstance(values, dict)
                                    and "queue_length" in values
                                ):
                                    queue_lengths.append(values["queue_length"])

                        if queue_lengths:
                            avg_queue_length = np.mean(queue_lengths)
                            # Invert queue length to get efficiency (shorter queue = higher score)
                            flow_efficiency = 100 / (1 + avg_queue_length)
                            # Normalize to 0-100 scale
                            flow_efficiency = min(100, flow_efficiency * 20)
                    elif component_type == "generator":
                        # For generators, use a high flow efficiency by default
                        flow_efficiency = 80
                except Exception:
                    pass
                metrics["Flow Efficiency"] = flow_efficiency

                # 5. Workflow Impact (based on component position in the workflow)
                # This is a placeholder metric since we don't have workflow position data
                workflow_impact = 0
                try:
                    # Use a default value based on component type
                    if component_type == "generator":
                        workflow_impact = (
                            90  # Generators are typically at the start of the workflow
                        )
                    elif component_type == "resource":
                        workflow_impact = (
                            70  # Resources are typically in the middle of the workflow
                        )
                    else:
                        workflow_impact = 50  # Unknown components get a middle value
                except Exception:
                    pass
                metrics["Workflow Impact"] = workflow_impact

                # Create data points for this component
                data_points = []
                for metric_name in metric_names:
                    data_points.append(
                        DataPoint(x=metric_name, y=metrics.get(metric_name, 0))
                    )

                # Create the series for this component
                series.append(
                    Series(
                        name=f"{component_name} ({component_type})", data=data_points
                    )
                )

            # Create the radar chart
            return ChartBuilder.create_radar_chart(
                header="Component Optimization Comparison",
                description="Basic comparison of component metrics based on available data. Each axis represents a different optimization metric (0-100 scale). Higher values indicate better performance.",
                series=series,
                show_legend=True,
                show_tooltip=True,
                max_value=100,  # Set maximum value for better scaling
                cols=4,
                rows=2,
            )

        except Exception as e:
            print(f"Warning: Could not create fallback optimization chart: {e}")

            # Return a simple message chart as a last resort
            message_series = Series(name="Note", data=[DataPoint(x="No Data", y=0)])

            return ChartBuilder.create_bar_chart(
                header="Component Optimization Comparison",
                description="Could not generate optimization metrics chart. Error: "
                + str(e) + " X-axis: Metrics. Y-axis: Values.",
                series=[message_series],
                cols=4,
                rows=1,
            )

    def _create_component_comparison_table(
        self, csv_scraper: CSVScraper, component_insights: List[ComponentOutput]
    ) -> Dict[str, Any]:
        """
        Create a table comparing key performance indicators across all components.

        Args:
            csv_scraper: CSVScraper instance for accessing simulation data
            component_insights: List of ComponentOutput objects with component analytics

        Returns:
            Dictionary with table data
        """
        try:
            # Check if we have any component insights
            if not component_insights:
                print("No component insights available for comparison table")

                # If no component insights are available, try to create a table from CSV data directly
                return self._create_fallback_component_table(csv_scraper)

            # Collect data for each component
            table_data = []

            for insight in component_insights:
                # Get component data from CSV scraper
                component_data = csv_scraper.components_data.get(insight.id, {})

                # Find optimization score in the component's metrics
                optimization_score = 0
                for card in insight.dashboradData:
                    if (
                        hasattr(card, "header")
                        and card.header == "Optimization Score"
                        and hasattr(card, "value")
                    ):
                        optimization_score = card.value
                        break

                # Get efficiency from component data
                efficiency = csv_scraper.calculate_component_efficiency(insight.id)
                if isinstance(efficiency, dict):
                    efficiency = efficiency.get(insight.id, 0)

                # Get processing time metrics
                processing_time = 0
                processing_count = 0
                in_out_processing = {}

                # Try to get processing time from component metrics
                for chart in insight.dashboradData:
                    if (
                        hasattr(chart, "header")
                        and "Processing Time" in chart.header
                        and hasattr(chart, "series")
                        and chart.series
                    ):
                        # Found a processing time chart, extract the average
                        for series in chart.series:
                            if series.name == "Average":
                                for data_point in series.data:
                                    if data_point.x == "Average":
                                        processing_time = data_point.y
                                        break

                # If we couldn't find processing time in charts, try to get it from CSV data
                if processing_time == 0:
                    proc_times = csv_scraper.calculate_processing_time(insight.id)
                    if isinstance(proc_times, dict):
                        processing_time = proc_times.get("mean", 0)
                        processing_count = proc_times.get("count", 0)

                # Get in/out processing time specifically
                try:
                    in_out_processing = csv_scraper._calculate_in_out_processing_times(
                        insight.id
                    )
                except:
                    # Use the component's analytics method if available
                    for comp_id in Component.get_registry_keys():
                        component = Component.comp_from_registery(comp_id)
                        if component and component.compId == insight.id:
                            analytics = AnalyticsFactory.create_analytics(
                                component_id=insight.id,
                                component_type=insight.type,
                                csv_scraper=csv_scraper,
                            )
                            analytics.calculate_performance_metrics()
                            in_out_processing = analytics.metrics.get(
                                "in_out_processing", {}
                            )
                            break

                # Get utilization
                utilization = csv_scraper.get_component_utilization(insight.id)
                if isinstance(utilization, dict):
                    utilization = utilization.get(insight.id, 0)

                # Create table entry
                entry = {
                    "id": insight.id,
                    "name": insight.name,
                    "type": insight.type,
                    "efficiency": round(float(efficiency) * 100, 1),
                    "avg_processing_time": round(float(processing_time), 2),
                    "in_out_processing_time": round(
                        float(in_out_processing.get("mean", 0)), 2
                    ),
                    "processing_count": int(processing_count),
                    "utilization": round(float(utilization), 1),
                    "optimization_score": round(float(optimization_score), 1),
                }

                # Add component-specific KPIs based on type
                if insight.type == "generator":
                    # For generators, add generation count
                    action_counts = component_data.get("action_counts", {})
                    generation_count = action_counts.get("GENERATE", 0)
                    entry["generation_count"] = generation_count
                elif insight.type == "resource":
                    # For resources, add queue metrics
                    queue_metrics = {}
                    for action in component_data.get("actions", []):
                        if action["action"] == "QUEUED" and isinstance(
                            action.get("values"), dict
                        ):
                            queue_length = action["values"].get("queue_length")
                            if queue_length is not None:
                                queue_metrics.setdefault("lengths", []).append(
                                    queue_length
                                )

                    if "lengths" in queue_metrics and queue_metrics["lengths"]:
                        entry["avg_queue_length"] = round(
                            float(np.mean(queue_metrics["lengths"])), 2
                        )
                        entry["max_queue_length"] = round(
                            float(max(queue_metrics["lengths"])), 2
                        )

                table_data.append(entry)

            # If we still don't have any table data, try the fallback method
            if not table_data:
                return self._create_fallback_component_table(csv_scraper)

            # Define column order and labels
            column_order = [
                "id",
                "name",
                "type",
                "efficiency",
                "optimization_score",
                "avg_processing_time",
                "in_out_processing_time",
                "processing_count",
                "utilization",
            ]

            column_labels = {
                "id": "ID",
                "name": "Name",
                "type": "Type",
                "efficiency": "Efficiency (%)",
                "optimization_score": "Optimization Score",
                "avg_processing_time": "Avg. Processing Time",
                "in_out_processing_time": "IN/OUT Processing Time",
                "processing_count": "Processed Count",
                "utilization": "Utilization (%)",
                "generation_count": "Generation Count",
                "avg_queue_length": "Avg. Queue Length",
                "max_queue_length": "Max Queue Length",
            }

            # Add type-specific columns to the order
            for entry in table_data:
                if (
                    entry["type"] == "generator"
                    and "generation_count" in entry
                    and "generation_count" not in column_order
                ):
                    column_order.append("generation_count")
                elif entry["type"] == "resource":
                    if (
                        "avg_queue_length" in entry
                        and "avg_queue_length" not in column_order
                    ):
                        column_order.append("avg_queue_length")
                    if (
                        "max_queue_length" in entry
                        and "max_queue_length" not in column_order
                    ):
                        column_order.append("max_queue_length")

            # Create the table
            return Table.create_table(
                data=table_data,
                title="Component Performance Comparison",
                description="Comparison of key performance indicators across all components",
                column_order=column_order,
                column_labels=column_labels,
                table_id="component_comparison_table",
            )

        except Exception as e:
            print(f"Warning: Could not create component comparison table: {e}")
            return self._create_fallback_component_table(csv_scraper)

    def _create_fallback_component_table(
        self, csv_scraper: CSVScraper
    ) -> Dict[str, Any]:
        """
        Create a fallback component comparison table directly from CSV data.

        This method is used when component insights are not available.

        Args:
            csv_scraper: CSVScraper instance for accessing simulation data

        Returns:
            Dictionary with table data
        """
        try:
            # Get component names from CSV data
            component_names = {}
            try:
                # Try to load component names from component_names.json
                component_names_path = (
                    self.runPath / self.runName / "component_names.json"
                )
                if component_names_path.exists():
                    with open(component_names_path, "r") as f:
                        component_names = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load component names: {e}")

            # Collect data for each component
            table_data = []

            # Get all component IDs from CSV data
            component_ids = list(csv_scraper.components_data.keys())

            # If no component IDs are found, try to extract them from the CSV data directly
            if not component_ids:
                print(
                    "No component data found in CSV scraper, attempting to extract from raw CSV data"
                )
                try:
                    # Try to extract component IDs from the component_names.json file
                    if component_names:
                        component_ids = list(component_names.keys())

                        # Initialize components_data in the CSV scraper if it doesn't exist
                        if (
                            not hasattr(csv_scraper, "components_data")
                            or not csv_scraper.components_data
                        ):
                            csv_scraper.components_data = {}

                        # For each component ID, create a basic entry in the components_data dictionary
                        for comp_id in component_ids:
                            if comp_id not in csv_scraper.components_data:
                                # Try to determine the component type from the CSV data
                                comp_type = "unknown"
                                try:
                                    # Extract component type from CSV data
                                    df = csv_scraper.df
                                    if not df.empty:
                                        comp_rows = df[df["component_id"] == comp_id]
                                        if not comp_rows.empty:
                                            comp_type = comp_rows[
                                                "component_type"
                                            ].iloc[0]
                                except Exception as e:
                                    print(
                                        f"Warning: Could not determine component type for {comp_id}: {e}"
                                    )

                                # Create a basic component data entry
                                csv_scraper.components_data[comp_id] = {
                                    "type": comp_type,
                                    "actions": [],
                                }

                                # Try to extract actions for this component from the CSV data
                                try:
                                    comp_rows = df[df["component_id"] == comp_id]
                                    for _, row in comp_rows.iterrows():
                                        action = {
                                            "action": row["action"],
                                            "time": row["time"],
                                        }

                                        # Try to parse values if available
                                        try:
                                            if "values" in row and row["values"]:
                                                values = json.loads(
                                                    row["values"].replace("'", '"')
                                                )
                                                action["values"] = values
                                        except Exception:
                                            pass

                                        csv_scraper.components_data[comp_id][
                                            "actions"
                                        ].append(action)
                                except Exception as e:
                                    print(
                                        f"Warning: Could not extract actions for {comp_id}: {e}"
                                    )
                except Exception as e:
                    print(
                        f"Warning: Could not extract component IDs from component_names.json: {e}"
                    )

            # Update component_ids list after potential extraction
            component_ids = list(csv_scraper.components_data.keys())

            # If we still don't have any component IDs, try to extract them from the CSV data
            if not component_ids:
                print(
                    "No component IDs found in component_names.json, attempting to extract from CSV data"
                )
                try:
                    df = csv_scraper.df
                    if not df.empty and "component_id" in df.columns:
                        component_ids = df["component_id"].unique().tolist()

                        # Initialize components_data in the CSV scraper if it doesn't exist
                        if (
                            not hasattr(csv_scraper, "components_data")
                            or not csv_scraper.components_data
                        ):
                            csv_scraper.components_data = {}

                        # For each component ID, create a basic entry in the components_data dictionary
                        for comp_id in component_ids:
                            if comp_id not in csv_scraper.components_data:
                                # Try to determine the component type from the CSV data
                                comp_type = "unknown"
                                try:
                                    comp_rows = df[df["component_id"] == comp_id]
                                    if not comp_rows.empty:
                                        comp_type = comp_rows["component_type"].iloc[0]
                                except Exception:
                                    pass

                                # Create a basic component data entry
                                csv_scraper.components_data[comp_id] = {
                                    "type": comp_type,
                                    "actions": [],
                                }

                                # Try to extract actions for this component from the CSV data
                                try:
                                    comp_rows = df[df["component_id"] == comp_id]
                                    for _, row in comp_rows.iterrows():
                                        action = {
                                            "action": row["action"],
                                            "time": row["time"],
                                        }

                                        # Try to parse values if available
                                        try:
                                            if "values" in row and row["values"]:
                                                values = json.loads(
                                                    row["values"].replace("'", '"')
                                                )
                                                action["values"] = values
                                        except Exception:
                                            pass

                                        csv_scraper.components_data[comp_id][
                                            "actions"
                                        ].append(action)
                                except Exception as e:
                                    print(
                                        f"Warning: Could not extract actions for {comp_id}: {e}"
                                    )
                except Exception as e:
                    print(
                        f"Warning: Could not extract component IDs from CSV data: {e}"
                    )

            # Process each component to create table entries
            for comp_id in component_ids:
                # Get component data
                component_data = csv_scraper.components_data.get(comp_id, {})

                # Get component type
                component_type = component_data.get("type", "unknown")

                # Get component name
                component_name = component_names.get(comp_id, comp_id)

                # Get efficiency
                efficiency = 0
                try:
                    efficiency = csv_scraper.calculate_component_efficiency(comp_id)
                    if isinstance(efficiency, dict):
                        efficiency = efficiency.get(comp_id, 0)
                except Exception as e:
                    print(f"Warning: Could not calculate efficiency for {comp_id}: {e}")

                # Get processing time
                processing_time = 0
                processing_count = 0
                try:
                    proc_times = csv_scraper.calculate_processing_time(comp_id)
                    if isinstance(proc_times, dict):
                        processing_time = proc_times.get("mean", 0)
                        processing_count = proc_times.get("count", 0)
                except Exception as e:
                    print(
                        f"Warning: Could not calculate processing time for {comp_id}: {e}"
                    )

                # Get in/out processing time
                in_out_processing = {}
                try:
                    # Check if the method exists
                    if hasattr(csv_scraper, "_calculate_in_out_processing_times"):
                        in_out_processing = (
                            csv_scraper._calculate_in_out_processing_times(comp_id)
                        )
                    else:
                        # Fallback: calculate in/out processing times manually
                        in_out_processing = self._calculate_in_out_processing_times(
                            csv_scraper, comp_id
                        )
                except Exception as e:
                    print(
                        f"Warning: Could not calculate in/out processing times for {comp_id}: {e}"
                    )

                # Get utilization
                utilization = 0
                try:
                    utilization = csv_scraper.get_component_utilization(comp_id)
                    if isinstance(utilization, dict):
                        utilization = utilization.get(comp_id, 0)
                except Exception as e:
                    print(
                        f"Warning: Could not calculate utilization for {comp_id}: {e}"
                    )

                # Calculate a basic optimization score based on available metrics
                optimization_score = 0
                try:
                    # Use a simple formula to calculate a basic optimization score
                    # This is a simplified version of the full optimization score calculation
                    if processing_time > 0:
                        # Normalize efficiency to 0-1 scale
                        norm_efficiency = min(1.0, float(efficiency))

                        # Normalize utilization to 0-1 scale with penalty for over-utilization
                        norm_utilization = min(1.0, float(utilization) / 100.0)
                        if norm_utilization > 0.95:  # Penalize over-utilization
                            norm_utilization = 0.95 - (norm_utilization - 0.95) * 2

                        # Calculate a basic optimization score
                        optimization_score = (
                            norm_efficiency * 0.4 + norm_utilization * 0.6
                        ) * 100
                except Exception as e:
                    print(
                        f"Warning: Could not calculate optimization score for {comp_id}: {e}"
                    )

                # Create table entry
                entry = {
                    "id": comp_id,
                    "name": component_name,
                    "type": component_type,
                    "efficiency": round(float(efficiency) * 100, 1),
                    "avg_processing_time": round(float(processing_time), 2),
                    "in_out_processing_time": round(
                        float(in_out_processing.get("mean", 0)), 2
                    ),
                    "processing_count": int(processing_count),
                    "utilization": round(float(utilization), 1),
                    "optimization_score": round(float(optimization_score), 1),
                }

                # Add component-specific KPIs based on type
                if component_type == "generator":
                    # For generators, add generation count
                    generation_count = 0
                    try:
                        # Count GENERATE actions
                        for action in component_data.get("actions", []):
                            if action.get("action") == "GENERATE":
                                generation_count += 1
                    except Exception:
                        pass

                    entry["generation_count"] = generation_count

                elif component_type == "resource":
                    # For resources, add queue metrics
                    queue_lengths = []
                    try:
                        for action in component_data.get("actions", []):
                            if action.get("action") == "QUEUED":
                                values = action.get("values", {})
                                if (
                                    isinstance(values, dict)
                                    and "queue_length" in values
                                ):
                                    queue_lengths.append(values["queue_length"])
                    except Exception:
                        pass

                    if queue_lengths:
                        entry["avg_queue_length"] = round(
                            float(np.mean(queue_lengths)), 2
                        )
                        entry["max_queue_length"] = round(float(max(queue_lengths)), 2)

                table_data.append(entry)

            # If we still don't have any table data, return None
            if not table_data:
                print("No component data available for fallback table")
                return None

            # Define column order and labels
            column_order = [
                "id",
                "name",
                "type",
                "efficiency",
                "optimization_score",
                "avg_processing_time",
                "in_out_processing_time",
                "processing_count",
                "utilization",
            ]

            column_labels = {
                "id": "ID",
                "name": "Name",
                "type": "Type",
                "efficiency": "Efficiency (%)",
                "optimization_score": "Optimization Score",
                "avg_processing_time": "Avg. Processing Time",
                "in_out_processing_time": "IN/OUT Processing Time",
                "processing_count": "Processed Count",
                "utilization": "Utilization (%)",
                "generation_count": "Generation Count",
                "avg_queue_length": "Avg. Queue Length",
                "max_queue_length": "Max Queue Length",
            }

            # Add type-specific columns to the order
            for entry in table_data:
                if (
                    entry["type"] == "generator"
                    and "generation_count" in entry
                    and "generation_count" not in column_order
                ):
                    column_order.append("generation_count")
                elif entry["type"] == "resource":
                    if (
                        "avg_queue_length" in entry
                        and "avg_queue_length" not in column_order
                    ):
                        column_order.append("avg_queue_length")
                    if (
                        "max_queue_length" in entry
                        and "max_queue_length" not in column_order
                    ):
                        column_order.append("max_queue_length")

            # Create the table
            return Table.create_table(
                data=table_data,
                title="Component Performance Comparison",
                description="Comparison of key performance indicators across all components",
                column_order=column_order,
                column_labels=column_labels,
                table_id="component_comparison_table",
            )

        except Exception as e:
            print(f"Warning: Could not create fallback component comparison table: {e}")
            return None

    def _calculate_in_out_processing_times(self, csv_scraper, component_id):
        """
        Calculate processing times between IN and OUT actions for a component.

        This is a fallback method used when the CSV scraper doesn't have the method.

        Args:
            csv_scraper: CSVScraper instance
            component_id: ID of the component to calculate processing times for

        Returns:
            Dictionary with processing time statistics
        """
        try:
            # Get component data
            component_data = csv_scraper.components_data.get(component_id, {})
            actions = component_data.get("actions", [])

            # Find IN/OUT pairs
            in_times = {}
            out_times = {}
            processing_times = []

            for action in actions:
                if action.get("action") == "IN":
                    # Get the container ID if available
                    container_id = None
                    try:
                        values = action.get("values", {})
                        if isinstance(values, dict):
                            # Try to extract container ID from PDV if available
                            pdv = action.get("PDV", {})
                            if isinstance(pdv, dict) and "containerId" in pdv:
                                container_id = pdv["containerId"]
                    except Exception:
                        pass

                    # If we couldn't get a container ID, use a counter
                    if not container_id:
                        container_id = f"container_{len(in_times)}"

                    # Record the IN time
                    in_times[container_id] = action.get("time", 0)

                elif action.get("action") == "OUT":
                    # Get the container ID if available
                    container_id = None
                    try:
                        values = action.get("values", {})
                        if isinstance(values, dict):
                            # Try to extract container ID from PDV if available
                            pdv = action.get("PDV", {})
                            if isinstance(pdv, dict) and "containerId" in pdv:
                                container_id = pdv["containerId"]
                    except Exception:
                        pass

                    # If we couldn't get a container ID, use a counter
                    if not container_id:
                        container_id = f"container_{len(out_times)}"

                    # Record the OUT time
                    out_times[container_id] = action.get("time", 0)

            # Calculate processing times for each container
            for container_id, in_time in in_times.items():
                if container_id in out_times:
                    out_time = out_times[container_id]
                    if out_time > in_time:
                        processing_times.append(out_time - in_time)

            # Calculate statistics
            if processing_times:
                import numpy as np

                return {
                    "mean": float(np.mean(processing_times)),
                    "median": float(np.median(processing_times)),
                    "min": float(np.min(processing_times)),
                    "max": float(np.max(processing_times)),
                    "count": len(processing_times),
                    "times": processing_times,
                }
            else:
                return {
                    "mean": 0,
                    "median": 0,
                    "min": 0,
                    "max": 0,
                    "count": 0,
                    "times": [],
                }
        except Exception as e:
            print(f"Warning: Error calculating in/out processing times: {e}")
            return {"mean": 0, "median": 0, "min": 0, "max": 0, "count": 0, "times": []}

    def cleanup(self):
        """
        Clean up all resources used by this simulation.
        This method should be called before deleting the SimulationBuilder instance.
        """
        # Close the logger if it exists
        if hasattr(self, "logger") and self.logger is not None:
            print("Closing logger...")
            self.logger.close()

        # Clear the component registry
        if hasattr(Component, "registry"):
            print(
                f"Clearing component registry with {Component.get_registry_size()} components..."
            )
            Component.registry.clear()

        # Instead of deleting the environment, reset it
        # This preserves the attribute while clearing its state
        self.env = simpy.Environment()

        # Clear local component references
        if hasattr(self, "components"):
            print(f"Clearing {len(self.components)} local component references...")
            self.components.clear()

        # Reset class-level references
        Component._initialized = False

        print("Simulation resources cleaned up successfully.")


def run():
    builder = SimulationBuilder(
        runName="test_run",
        ProjectPath=Path("./projects/state"),
        runPath=Path("./projects/run"),
    )

    builder.pprint_compStore()
    builder.build()

    # Check registry after build
    print("Simulation build complete.")
    print(f"Registry contains {Component.get_registry_size()} components")
    print(f"Registry keys: {Component.get_registry_keys()}")

    # Print the actual registry dictionary to see what's in it
    print(Component.genState)

    # Optional - start the simulation
    builder.start()
