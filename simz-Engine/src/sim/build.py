import json
import simpy
from src.sim.chart import (
    CardConfig,
    ChartBuilder,
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
from pathlib import Path
from typing import Callable, Dict, Type

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
            json.dump(data.dict(), f, indent=4)
        self.Logger(f"[OUTPUT] Simulation output saved to {file_path}")

    def output(self, csvScaraper: CSVScraper) -> SimOutput:
        output = SimOutput(id=self.runName)
        simTime = csvScaraper.get_time_range()
        # s_time_card = CardConfig(
        #     header="Simulation Time (start)",
        #     description="start time of the simulation",
        #     value=simTime["min_time"],
        #     valueFormatting=ValueFormatting.NUMBER,
        #     size=ChartSize(cols=1, rows=1),
        #     valuePrefix=None,
        #     valueSuffix=None,
        # )
        e_time_card = CardConfig(
            header="Simulation Time (last record)",
            description="ending time of the simulation",
            value=simTime["max_time"],
            valueFormatting=ValueFormatting.NUMBER,
            size=ChartSize(cols=1, rows=1),
            valuePrefix=None,
            valueSuffix=None,
        )

        total_comp = CardConfig(
            header="Total Components",
            description="Total number of components in the simulation",
            value=len(Component.registry),
            valueFormatting=ValueFormatting.NUMBER,
            size=ChartSize(cols=1, rows=1),
            valuePrefix=None,
            valueSuffix=None,
        )
        containerData = csvScaraper.count_containers_duckdb()
        total_container = CardConfig(
            header="Total Containers",
            description="Total number of Containers in the simulation",
            value=containerData.get("total_containers", 0),
            valueFormatting=ValueFormatting.NUMBER,
            size=ChartSize(cols=1, rows=1),
            valuePrefix=None,
            valueSuffix=None,
        )

        total_genType = CardConfig(
            header="Total GenTypes",
            description="Total number of GenTypes in the simulation",
            value=self.genState.total_count(),
            valueFormatting=ValueFormatting.NUMBER,
            size=ChartSize(cols=1, rows=1),
            valuePrefix=None,
            valueSuffix=None,
        )
        # Pie chart for component categories
        comp_Cat_data = csvScaraper.get_component_types().to_dict()
        comp_Cat_data_sum = sum(comp_Cat_data["unique_components"].values())
        comp_cat_series = Series(
            name="Categories",
            data=[
                DataPoint(
                    x=comp_Cat_data["component_type"][i],
                    y=(comp_Cat_data["unique_components"][i] / comp_Cat_data_sum) * 100,
                )
                for i in comp_Cat_data["component_type"]
            ],
        )
        component_cat = ChartBuilder.create_pie_chart(
            header="Component Categories",
            description="Distribution of component categories",
            series=[comp_cat_series],
            cols=2,
            rows=1,
        )

        # bar chat of action count
        act_count = csvScaraper.get_action_counts().to_dict()
        act_series = [
            DataPoint(x=act_count["action"][i], y=float(act_count["count"][i]))
            for i in act_count["action"]
        ]
        act_chart = ChartBuilder.create_bar_chart(
            header="Action Counts",
            description="Counts of actions performed by components",
            series=[Series(name="Actions", data=act_series)],
            cols=2,
            rows=1,
        )

        # efficey chart
        eff_pro_count = csvScaraper.get_ep_chart_data()
        eff_count = eff_pro_count["component_efficiency"]
        pro_count = eff_pro_count["processing_times"]
        eff_data_points = [
            DataPoint(x=self.get_component_with_name(key) or "Unkown", y=value)
            for key, value in eff_count.items()
        ]
        pro_data_points = [
            DataPoint(x=self.get_component_with_name(key) or "Unkown", y=float(value))
            for key, value in pro_count.items()
        ]
        line_eff_chart = ChartBuilder.create_line_chart(
            header="Avarage Efficiency Times (components)",
            description="Efficiency of components over time",
            series=[Series(name="components", data=eff_data_points)],
            cols=2,
            rows=1,
        )
        pro_eff_chart = ChartBuilder.create_line_chart(
            header="Avarage Processing Time (components)",
            description="Processing times of components over time",
            series=[Series(name="components", data=pro_data_points)],
            cols=2,
            rows=1,
        )

        # output.add_card(s_time_card)
        output.add_card(e_time_card)
        output.add_card(total_comp)
        output.add_card(total_genType)
        output.add_card(total_container)
        output.add_chart(component_cat)
        output.add_chart(act_chart)
        output.add_chart(line_eff_chart)
        output.add_chart(pro_eff_chart)

        # Component processing time chart (line chart)
        proc_time_chart_data = csvScaraper.get_component_processing_time_chart_data()
        proc_time_series = []

        # Check if we have the line_chart_data in the result
        if "line_chart_data" in proc_time_chart_data:
            line_data = proc_time_chart_data["line_chart_data"]
            timeline = line_data["timeline"]

            # Create a series for each component
            for comp_group in line_data["components"]:
                # Process each component in the group
                for component in comp_group["components"]:
                    # Create data points for this component
                    data_points = []
                    for i, time in enumerate(timeline):
                        if i < len(component["processing_times"]):
                            data_points.append(
                                DataPoint(
                                    x=str(time),
                                    y=float(component["processing_times"][i]),
                                )
                            )

                    # Add series for this component
                    if data_points:
                        proc_time_series.append(
                            Series(name=component["name"], data=data_points)
                        )

        # Create the chart if we have data
        if proc_time_series:
            component_proc_time_chart = ChartBuilder.create_line_chart(
                header="Component  Processing Times Over Time",
                description="Processing times of each component at different time points",
                series=proc_time_series,
                y_axis_label="Processing Time",
                x_axis_label="Simulation Time",
                cols=4,
                rows=1,
            )
            # Add the chart to output
            output.add_chart(component_proc_time_chart)

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

        # Reset the environment
        del self.env

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
