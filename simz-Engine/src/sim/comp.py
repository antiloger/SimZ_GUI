from typing import (
    Any,
    Dict,
    Optional,
    List,
    Generator as TypingGen,
    Tuple,
    Callable,
    Union,
    TypeVar,
)
import simpy
from src.sim.codeExec import CodeExec
from src.sim.db import CsvLogger
from src.sim.graph import WorkflowGraph
from src.sim.kvstorage import KVStorage
from src.sim.sim_types import (
    CompDataI,
    GenContainer,
    GenTypeState,
    GenTypes,
    ComponentOutput,
)
from src.sim.analytics import AnalyticsFactory
from abc import ABC, abstractmethod
import weakref
import random
import copy
import uuid
import math
import time
from datetime import datetime


class Component(ABC):
    # Define as class variables to be shared across all instances
    genState: GenTypeState
    workflow: WorkflowGraph
    logger: CsvLogger  # Using WeakValueDictionary to avoid memory leaks - when a component is deleted,
    # its entry in the registry will be automatically removed
    registry: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
    # Flag to track if class-level resources have been initialized
    _initialized = False

    def __init__(
        self,
        env: simpy.Environment,
        name: str,
        compData: CompDataI,
    ):
        # Check if class resources are initialized
        if not Component._initialized:
            print("WARNING: Component class resources are not initialized yet!")

        self.env = env
        self.name = name

        if compData.id is None:
            raise ValueError(
                "Component 'Resource' requires 'component_data' to be defined."
            )
        self.compId = compData.id
        self.comp_name = compData.compName
        self.type = compData.typeName
        self.category = compData.category
        self.genList = [] if compData.GenData is None else compData.GenData.types
        kv_data = compData.get_custom_input()
        self.var = KVStorage(storage=kv_data)
        self.Yieldable = False if compData.Yieldable is None else compData.Yieldable
        self.run_call_count = 0
        self.input_count = 0
        self.actionSet = []
        self.executor = CodeExec(compData.Runners, Component, GenContainer)
        # Register this component instance in the class registry
        self._register()
        print(">> %%", self.executor.run_funcs)
        print(">> %%", self.executor.generator_funcs)

        # Run startup method if it exists in the event code base
        self.run_startup()

    def _register(self):
        """Register this component in the class registry."""
        Component.registry[self.compId] = self
        print(
            f"Registered component {self.compId} of type {self.__class__.__name__} in registry"
        )

    @classmethod
    @abstractmethod
    def create(
        cls,
        env: simpy.Environment,
        compData: CompDataI,
    ) -> "Component":
        """Return a new instance of this component."""
        pass

    @classmethod
    def set_Gen_ref(cls, gen_ref: GenTypeState):
        cls.genState = gen_ref
        Component.genState = gen_ref  # Ensure base class has it too
        Component._initialized = True
        print(f"Set GenState reference for {cls.__name__}")

    @classmethod
    def set_workflow(cls, workflow: WorkflowGraph):
        cls.workflow = workflow
        Component.workflow = workflow  # Ensure base class has it too
        Component._initialized = True
        print(f"Set workflow reference for {cls.__name__}")

    @classmethod
    def set_logger(cls, logger: CsvLogger):
        cls.logger = logger
        Component.logger = logger  # Ensure base class has it too
        Component._initialized = True
        print(f"Set logger reference for {cls.__name__}")

    @classmethod
    def comp_from_registery(cls, compId: str) -> Optional["Component"]:
        """Retrieve a component by its ID from the registry."""
        comp = cls.registry.get(compId)
        if comp is None:
            print(
                f"Component with ID {compId} not found in registry. Registry has {len(cls.registry)} components."
            )
            print(f"Available components: {list(cls.registry.keys())}")
        return comp

    @classmethod
    def get_registry_size(cls) -> int:
        """Return the number of components in the registry."""
        return len(cls.registry)

    @classmethod
    def get_registry_keys(cls) -> List[str]:
        """Return a list of all component IDs in the registry."""
        return list(cls.registry.keys())

    @classmethod
    def check_registry(cls):
        """Check and print registry information for debugging."""
        print(f"Registry contains {len(cls.registry)} components.")
        print(f"Registry keys: {list(cls.registry.keys())}")
        print(
            f"Registry values types: {[type(v).__name__ for v in cls.registry.values()]}"
        )

    def targetHandlerFind(self, output: GenContainer) -> Optional[str]:
        types_gen = output.get_name_in_Data()
        if len(types_gen) == 1:
            return f"{types_gen[0]}-out"
        return None

    def getGenType(self, name: str) -> Optional[Dict[str, GenTypes]]:
        gen_data = self.genState.get_by_name(name)
        if gen_data is None:
            print(f"GenType {name} not found in GenState.")
            return None
        return gen_data

    def run_startup(self):
        """
        Check if there's a startup method in the event code base and run it.
        This allows users to initialize their own variables inside the component.
        The startup method should take a component parameter (self from component class)
        which lets users access existing methods in the component class and inherited classes.
        """
        # Check if there's a startup method in the event code base
        startup_func = self.executor.execute_event_function("startup")
        if startup_func:
            try:
                # Run the startup method and pass self as the component parameter
                result = startup_func(self)
                print(f"Startup method executed for component {self.compId}")
                return result
            except Exception as e:
                print(
                    f"Error executing startup method for component {self.compId}: {e}"
                )
        return None

    def create_default_container(self, genTypeName) -> GenContainer:
        gen_data = self.genState.get_by_name(genTypeName)
        if gen_data is None:
            print(f"GenType {genTypeName} not found in GenState.")
            raise ValueError("GenType not found in GenState.")

        return GenContainer(
            Data=gen_data,
            targetComp=None,
            targetHandler=None,
        )

    def send_genOutput_next(self, input: GenContainer, genType: str) -> GenContainer:
        """
        Sets the appropriate target handler on the input container based on the genType string.

        This method allows components to dynamically route GenContainers to specific functions.
        If a function name is provided, it will be used to determine which function
        should process this container in the next component.

        Args:
            input: The GenContainer to route
            genType: The name of the generator type
            func_name: Optional name of the function to execute in the target component
                       If None, will check if there's a source handler in the workflow graph
                       that matches the genType with "-out" suffix

        Returns:
            The input GenContainer with the target handler set
        """
        # Set the component ID if not already set
        if input.targetComp is None:
            input.targetComp = self.compId

        # If a specific function name is provided, use it to set the target handler
        # Check if there's a source handler in the workflow graph that matches the genType with "-out" suffix
        source_handle_id = f"{genType}-out"

        # Check if this component has this source handle in the workflow graph
        component_handles = self.workflow.get_component_handles(self.compId)
        if source_handle_id in component_handles:
            # Use the existing source handle
            input.targetHandler = source_handle_id
        else:
            # Default behavior: use the genType as the handler base name
            input.targetHandler = source_handle_id

        # Print debug info
        print(
            f"Using source handler: {input.targetHandler} for component {self.compId}"
        )

        return input

    def _next(self, output: Optional[GenContainer] = None):
        if output is None:
            print("Output is None, cannot proceed.")
            return
        if output.targetComp is None:
            output.targetComp = self.compId

        if output.targetHandler is None:
            str_hand = self.targetHandlerFind(output)
            if str_hand is None:
                return
            output.targetHandler = str_hand

        output_list = self.workflow.find_connection_target(
            source_component_id=output.targetComp,
            source_handle_id=output.targetHandler,
        )

        if output_list is None:
            print(
                f"Connection not found for source component {output.targetComp} and handler {output.targetHandler}."
            )
            return

        output.set_next_target(
            comp=output_list[0],
            handler=output_list[1],
        )

        # Check registry explicitly before proceeding
        print(
            f"Looking for component {output_list[0]} in registry with {self.get_registry_size()} components"
        )
        next_comp_ref = self.comp_from_registery(output_list[0])
        if next_comp_ref is None:
            print(f"Component with ID {output_list[0]} not found in registry.")
            return
        self.env.process(next_comp_ref.run(output))

    def random(self, from_val: int, to_val: int):
        """Generate a random integer between from_val and to_val."""
        return random.randint(from_val, to_val)

    def rand_ndist(self, mean: int, std_dev: int):
        """Generate a random number from a normal distribution with mean and standard deviation."""
        return random.normalvariate(mean, std_dev)

    def create_container(self, genType: str, data: Dict[str, Any]) -> GenContainer:
        """Create a new GenContainer with the specified genType and data."""
        print(f"Creating container for genType: {genType} with data: {data}")
        gen_data = self.genState.get_by_name(genType)
        if gen_data is None:
            print(f"GenType {genType} not found in GenState.")
            raise ValueError("GenType not found in GenState.")
        container = GenContainer(
            Data=gen_data,
            targetComp=self.compId,
            targetHandler=None,
        )
        genid = container.get_name_in_Data()[0]
        print(f"1 11 1 1Container created: {container}")
        print(f"1 11 1 1att created: {data}")
        container.set_targetHandler(f"{genid}-out")
        try:
            for key, value in data.items():
                print(f"Updating container with key: {key}, value: {value}")
                container.Data[genid].update_value(key, value)
        except Exception as e:
            print(f"Error updating container data: {e}")
        print(f"Container created: {container}")
        return container

    @abstractmethod
    def run(self, input: Optional[GenContainer]) -> TypingGen[Any, Any, Any]:
        pass

    def set_actionSet(self, actionSet: List[str]):
        self.actionSet = actionSet

    def get_actionSet(self) -> List[str]:
        return self.actionSet

    def insert_action(self, action: str):
        self.actionSet.append(action)

    def inc_run_call_count(self):
        self.run_call_count += 1

    def get_run_call_count(self) -> int:
        return self.run_call_count

    def input_processing(self, input: GenContainer) -> tuple[Optional[str], bool]:
        """
        this method is used to process the input data and determine the type of action to be taken.
        arg: input: GenContainer
        return: tuple of (func_name, is_generator)
        """
        t, d = input.split_at_last_dash()
        if t is None or d is None:
            raise ValueError("Invalid input format. Expected 'type-data'.")

        if t in self.executor.generator_funcs:
            return t, True
        if t in self.executor.run_funcs:
            return t, False

        return None, False

    def log_event(
        self,
        action: str,
        values: Dict[str, Any],
        PDV: Optional[Dict[str, Any]] = None,
        more: Optional[Dict[str, Any]] = None,
    ):
        self.logger.log_event(
            {
                "time": self.env.now,
                "component_id": self.compId,
                "component_type": self.category,
                "action": action,
                "values": values,
                "PDV": PDV,
                "addition": more,
            }
        )

    def set_next_components(self, next_components: List[str]):
        self.next_components = next_components

    def run_custom_code(self, code: str, context):
        try:
            code_obj = compile(code, "<string>", "exec")
            namespace = {}
            exec(code_obj, namespace)
            run_func = namespace["run"]
            result = run_func(context)
            return result
        except Exception as e:
            print(f"Error compiling code: {e}")
            return None

    def timeout(self, duration: int):
        yield self.env.timeout(duration)

    #
    # HELPER METHODS FOR COMPONENT CLASSES
    # These methods are designed to help users write custom component functions
    #

    # Visualization Helpers

    def get_csv_data(self, csv_scraper=None) -> Any:
        """
        Get the CSV scraper for accessing simulation data.

        This method provides access to the CSV data for creating visualizations.
        If a CSV scraper is provided, it will be used; otherwise, it will try to
        get the scraper from the analytics system.

        Args:
            csv_scraper: Optional CSVScraper instance

        Returns:
            CSVScraper instance or None if not available

        Example:
            # Get CSV data and extract processing times
            csv_data = component.get_csv_data()
            if csv_data:
                processing_times = csv_data.get_processing_times(component.compId)
        """
        if csv_scraper:
            return csv_scraper

        # Try to get the CSV scraper from the analytics system
        try:
            from src.sim.csvpaser import CSVScraper
            csv_file = f"output/{self.compId}_data.csv"
            return CSVScraper(csv_file)
        except Exception as e:
            print(f"Error getting CSV data: {e}")
            return None

    def get_processing_times(self, csv_scraper=None) -> List[Dict[str, Any]]:
        """
        Get processing times for this component.

        This method extracts processing times between IN and OUT actions
        for visualization purposes.

        Args:
            csv_scraper: Optional CSVScraper instance

        Returns:
            List of processing time data points {time, duration}

        Example:
            # Get processing times and create a chart
            processing_times = component.get_processing_times()
            chart = component.create_line_chart(
                header="Processing Times",
                description="Processing times over simulation time",
                series_data=[{
                    'name': 'Processing Time',
                    'data': [{'x': pt['time'], 'y': pt['duration']} for pt in processing_times]
                }],
                y_axis_label="Time",
                x_axis_label="Simulation Time"
            )
        """
        csv_data = self.get_csv_data(csv_scraper)
        if not csv_data:
            return []

        try:
            # Get processing times from the CSV data
            processing_data = csv_data.get_processing_times(self.compId)
            return [
                {'time': entry.get('time', 0), 'duration': entry.get('duration', 0)}
                for entry in processing_data
            ]
        except Exception as e:
            print(f"Error getting processing times: {e}")
            return []

    def get_action_counts(self, csv_scraper=None) -> Dict[str, int]:
        """
        Get counts of different actions for this component.

        This method counts occurrences of each action type (IN, OUT, QUEUED, etc.)
        for visualization purposes.

        Args:
            csv_scraper: Optional CSVScraper instance

        Returns:
            Dictionary mapping action names to counts

        Example:
            # Get action counts and create a pie chart
            action_counts = component.get_action_counts()
            chart = component.create_pie_chart(
                header="Action Distribution",
                description="Distribution of actions in the component",
                data=[{'name': action, 'value': count} for action, count in action_counts.items()]
            )
        """
        csv_data = self.get_csv_data(csv_scraper)
        if not csv_data:
            return {}

        try:
            # Get all events for this component
            events = csv_data.get_component_events(self.compId)

            # Count actions
            action_counts = {}
            for event in events:
                action = event.get('action')
                if action:
                    action_counts[action] = action_counts.get(action, 0) + 1

            return action_counts
        except Exception as e:
            print(f"Error getting action counts: {e}")
            return {}

    def get_queue_length_timeline(self, csv_scraper=None) -> List[Dict[str, Any]]:
        """
        Get queue length timeline for this component.

        This method extracts queue length data over time for visualization purposes.
        Only applicable for Resource components.

        Args:
            csv_scraper: Optional CSVScraper instance

        Returns:
            List of queue length data points {time, length}

        Example:
            # Get queue length timeline and create a chart
            queue_data = component.get_queue_length_timeline()
            chart = component.create_line_chart(
                header="Queue Length Over Time",
                description="Queue length throughout the simulation",
                series_data=[{
                    'name': 'Queue Length',
                    'data': [{'x': entry['time'], 'y': entry['length']} for entry in queue_data]
                }],
                y_axis_label="Queue Length",
                x_axis_label="Simulation Time"
            )
        """
        csv_data = self.get_csv_data(csv_scraper)
        if not csv_data:
            return []

        try:
            # Get all events for this component
            events = csv_data.get_component_events(self.compId)

            # Extract queue length data
            queue_data = []
            for event in events:
                if 'values' in event and 'queue_length' in event['values']:
                    queue_data.append({
                        'time': event.get('time', 0),
                        'length': event['values']['queue_length']
                    })

            return queue_data
        except Exception as e:
            print(f"Error getting queue length timeline: {e}")
            return []

    def get_container_metrics(self, csv_scraper=None) -> List[Dict[str, Any]]:
        """
        Get metrics for containers processed by this component.

        This method extracts container-specific metrics for visualization purposes.

        Args:
            csv_scraper: Optional CSVScraper instance

        Returns:
            List of container metric data

        Example:
            # Get container metrics and create a table
            container_metrics = component.get_container_metrics()
            table = component.create_table(
                data=container_metrics,
                title="Container Metrics",
                description="Metrics for containers processed by this component"
            )
        """
        csv_data = self.get_csv_data(csv_scraper)
        if not csv_data:
            return []

        try:
            # Get all events for this component
            events = csv_data.get_component_events(self.compId)

            # Extract container data
            container_data = {}
            for event in events:
                if 'PDV' in event and event['PDV'] and 'containerId' in event['PDV']:
                    container_id = event['PDV']['containerId']
                    action = event.get('action')
                    time = event.get('time', 0)

                    # Initialize container entry if not exists
                    if container_id not in container_data:
                        container_data[container_id] = {
                            'container_id': container_id,
                            'actions': []
                        }

                    # Add action data
                    container_data[container_id]['actions'].append({
                        'action': action,
                        'time': time
                    })

                    # Add container type information if available
                    if 'types' in event['PDV']:
                        container_data[container_id]['types'] = list(event['PDV']['types'].keys())

            # Calculate metrics for each container
            container_metrics = []
            for container_id, data in container_data.items():
                metrics = {
                    'container_id': container_id,
                    'types': ', '.join(data.get('types', [])),
                }

                # Calculate processing time if IN and OUT actions exist
                actions = sorted(data['actions'], key=lambda x: x['time'])
                in_time = next((a['time'] for a in actions if a['action'] == 'IN'), None)
                out_time = next((a['time'] for a in actions if a['action'] == 'OUT'), None)

                if in_time is not None and out_time is not None:
                    metrics['processing_time'] = out_time - in_time

                # Calculate queue time if QUEUED and IN actions exist
                queued_time = next((a['time'] for a in actions if a['action'] == 'QUEUED'), None)
                if queued_time is not None and in_time is not None:
                    metrics['queue_time'] = in_time - queued_time

                container_metrics.append(metrics)

            return container_metrics
        except Exception as e:
            print(f"Error getting container metrics: {e}")
            return []

    def create_line_chart(
        self,
        header: str,
        description: str,
        series_data: List[Dict[str, Any]],
        y_axis_label: Optional[str] = None,
        x_axis_label: Optional[str] = None,
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> Any:
        """
        Create a line chart for component visualization.

        Args:
            header: Chart title
            description: Chart description
            series_data: List of series data dictionaries, each with 'name' and 'data' keys
                         where 'data' is a list of {x, y} dictionaries
            y_axis_label: Label for the Y axis (optional)
            x_axis_label: Label for the X axis (optional)
            cols: Number of columns (1-4) the chart should span (optional)
            rows: Number of rows (1-4) the chart should span (optional)

        Returns:
            ChartConfig object for a line chart

        Example:
            # Create a line chart showing processing times
            chart = component.create_line_chart(
                header="Processing Times",
                description="Processing times over simulation time",
                series_data=[{
                    'name': 'Processing Time',
                    'data': [
                        {'x': 0, 'y': 5},
                        {'x': 10, 'y': 8},
                        {'x': 20, 'y': 12}
                    ]
                }],
                y_axis_label="Time",
                x_axis_label="Simulation Time"
            )
        """
        from src.sim.chart import ChartBuilder, Series, DataPoint

        # Convert series_data to Series objects
        series_list = []
        for series_item in series_data:
            data_points = []
            for point in series_item.get('data', []):
                data_points.append(DataPoint(x=point.get('x', 0), y=point.get('y', 0)))

            series_list.append(Series(
                name=series_item.get('name', 'Series'),
                data=data_points
            ))

        # Create and return the chart
        return ChartBuilder.create_line_chart(
            header=header,
            description=description,
            series=series_list,
            y_axis_label=y_axis_label,
            x_axis_label=x_axis_label,
            cols=cols,
            rows=rows
        )

    def create_bar_chart(
        self,
        header: str,
        description: str,
        series_data: List[Dict[str, Any]],
        y_axis_label: Optional[str] = None,
        x_axis_label: Optional[str] = None,
        vertical: bool = True,
        stacked: bool = False,
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> Any:
        """
        Create a bar chart for component visualization.

        Args:
            header: Chart title
            description: Chart description
            series_data: List of series data dictionaries, each with 'name' and 'data' keys
                         where 'data' is a list of {x, y} dictionaries
            y_axis_label: Label for the Y axis (optional)
            x_axis_label: Label for the X axis (optional)
            vertical: Whether bars should be vertical (True) or horizontal (False)
            stacked: Whether bars should be stacked
            cols: Number of columns (1-4) the chart should span (optional)
            rows: Number of rows (1-4) the chart should span (optional)

        Returns:
            ChartConfig object for a bar chart

        Example:
            # Create a bar chart showing container counts by type
            chart = component.create_bar_chart(
                header="Container Counts",
                description="Number of containers by type",
                series_data=[{
                    'name': 'Count',
                    'data': [
                        {'x': 'Water', 'y': 25},
                        {'x': 'Oil', 'y': 15},
                        {'x': 'Gas', 'y': 10}
                    ]
                }],
                y_axis_label="Count",
                x_axis_label="Container Type"
            )
        """
        from src.sim.chart import ChartBuilder, Series, DataPoint, BarLayout, BarType

        # Convert series_data to Series objects
        series_list = []
        for series_item in series_data:
            data_points = []
            for point in series_item.get('data', []):
                data_points.append(DataPoint(x=point.get('x', ''), y=point.get('y', 0)))

            series_list.append(Series(
                name=series_item.get('name', 'Series'),
                data=data_points
            ))

        # Set layout and bar type
        layout = BarLayout.VERTICAL if vertical else BarLayout.HORIZONTAL
        bar_type = BarType.STACKED if stacked else BarType.GROUPED

        # Create and return the chart
        return ChartBuilder.create_bar_chart(
            header=header,
            description=description,
            series=series_list,
            y_axis_label=y_axis_label,
            x_axis_label=x_axis_label,
            layout=layout,
            bar_type=bar_type,
            cols=cols,
            rows=rows
        )

    def create_pie_chart(
        self,
        header: str,
        description: str,
        data: List[Dict[str, Any]],
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> Any:
        """
        Create a pie chart for component visualization.

        Args:
            header: Chart title
            description: Chart description
            data: List of data dictionaries, each with 'name' and 'value' keys
            cols: Number of columns (1-4) the chart should span (optional)
            rows: Number of rows (1-4) the chart should span (optional)

        Returns:
            ChartConfig object for a pie chart

        Example:
            # Create a pie chart showing container type distribution
            chart = component.create_pie_chart(
                header="Container Distribution",
                description="Distribution of container types",
                data=[
                    {'name': 'Water', 'value': 25},
                    {'name': 'Oil', 'value': 15},
                    {'name': 'Gas', 'value': 10}
                ]
            )
        """
        from src.sim.chart import ChartBuilder, Series, DataPoint

        # Convert data to Series format
        data_points = []
        for item in data:
            data_points.append(DataPoint(x=item.get('name', ''), y=item.get('value', 0)))

        series = Series(name="Data", data=data_points)

        # Create and return the chart
        return ChartBuilder.create_pie_chart(
            header=header,
            description=description,
            series=[series],
            cols=cols,
            rows=rows
        )

    def create_card(
        self,
        header: str,
        description: str,
        value: Any,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        cols: Optional[int] = None,
        rows: Optional[int] = None,
    ) -> Any:
        """
        Create a card for component visualization.

        Args:
            header: Card title
            description: Card description
            value: The value to display on the card
            prefix: Text to display before the value (optional)
            suffix: Text to display after the value (optional)
            cols: Number of columns (1-4) the card should span (optional)
            rows: Number of rows (1-4) the card should span (optional)

        Returns:
            CardConfig object

        Example:
            # Create a card showing total processed containers
            card = component.create_card(
                header="Processed Containers",
                description="Total number of containers processed",
                value=150,
                suffix="containers"
            )
        """
        from src.sim.chart import CardConfig, ValueFormatting, ChartSize

        # Determine value formatting based on value type
        if isinstance(value, (int, float)):
            value_formatting = ValueFormatting.NUMBER
        else:
            value_formatting = ValueFormatting.TEXT

        # Create size if specified
        size = None
        if cols or rows:
            size = ChartSize(cols=cols or 1, rows=rows or 1)

        # Create and return the card
        return CardConfig(
            header=header,
            description=description,
            value=value,
            valueFormatting=value_formatting,
            valuePrefix=prefix,
            valueSuffix=suffix,
            size=size
        )

    def create_table(
        self,
        data: List[Dict[str, Any]],
        title: Optional[str] = None,
        description: Optional[str] = None,
        column_order: Optional[List[str]] = None,
        column_labels: Optional[Dict[str, str]] = None,
        exclude_columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a table for component visualization.

        Args:
            data: List of data rows, where each row is a dictionary of column values
            title: Table title (optional)
            description: Table description (optional)
            column_order: List specifying the order of columns (optional)
            column_labels: Dictionary mapping column keys to display labels (optional)
            exclude_columns: List of column keys to exclude from the table (optional)

        Returns:
            Dictionary containing the table definition

        Example:
            # Create a table showing container processing metrics
            table = component.create_table(
                data=[
                    {'id': 1, 'type': 'Water', 'processing_time': 5.2, 'queue_time': 2.1},
                    {'id': 2, 'type': 'Oil', 'processing_time': 8.7, 'queue_time': 3.5},
                    {'id': 3, 'type': 'Gas', 'processing_time': 3.1, 'queue_time': 1.2}
                ],
                title="Container Processing Metrics",
                description="Processing and queue times for each container",
                column_order=['id', 'type', 'processing_time', 'queue_time'],
                column_labels={'processing_time': 'Processing Time', 'queue_time': 'Queue Time'}
            )
        """
        from src.sim.table import Table

        # Create and return the table
        return Table.create_table(
            data=data,
            title=title,
            description=description,
            column_order=column_order,
            column_labels=column_labels,
            exclude_columns=exclude_columns
        )

    # Container Management Helpers

    def get_container_data(
        self, container: GenContainer, gen_type: str, attribute: str
    ) -> Any:
        """
        Get a specific attribute value from a container.

        Args:
            container: The GenContainer to get data from
            gen_type: The name of the generator type
            attribute: The attribute name to retrieve

        Returns:
            The attribute value or None if not found

        Example:
            # Get the 'temperature' attribute from a 'Water' type in the container
            temp = component.get_container_data(container, 'Water', 'temperature')
        """
        if container is None or not isinstance(container, GenContainer):
            print(f"Warning: Invalid container provided to get_container_data")
            return None

        if gen_type not in container.Data:
            print(f"Warning: GenType '{gen_type}' not found in container")
            return None

        try:
            return container.Data[gen_type].get_value(attribute)
        except KeyError:
            print(f"Warning: Attribute '{attribute}' not found in GenType '{gen_type}'")
            return None
        except Exception as e:
            print(f"Error getting container data: {e}")
            return None

    def set_container_data(
        self, container: GenContainer, gen_type: str, attribute: str, value: Any
    ) -> bool:
        """
        Set a specific attribute value in a container.

        Args:
            container: The GenContainer to modify
            gen_type: The name of the generator type
            attribute: The attribute name to set
            value: The value to set

        Returns:
            True if successful, False otherwise

        Example:
            # Set the 'temperature' attribute to 25 for a 'Water' type in the container
            component.set_container_data(container, 'Water', 'temperature', 25)
        """
        if container is None or not isinstance(container, GenContainer):
            print(f"Warning: Invalid container provided to set_container_data")
            return False

        if gen_type not in container.Data:
            print(f"Warning: GenType '{gen_type}' not found in container")
            return False

        try:
            container.Data[gen_type].update_value(attribute, value)
            return True
        except KeyError:
            print(f"Warning: Attribute '{attribute}' not found in GenType '{gen_type}'")
            return False
        except Exception as e:
            print(f"Error setting container data: {e}")
            return False

    def copy_container(self, container: GenContainer) -> Optional[GenContainer]:
        """
        Create a deep copy of a container.

        Args:
            container: The GenContainer to copy

        Returns:
            A new GenContainer with the same data

        Example:
            # Create a copy of a container
            new_container = component.copy_container(original_container)
        """
        if container is None or not isinstance(container, GenContainer):
            print(f"Warning: Invalid container provided to copy_container")
            return None

        try:
            return copy.deepcopy(container)
        except Exception as e:
            print(f"Error copying container: {e}")
            return None

    def merge_container_data(
        self, target: GenContainer, source: GenContainer, overwrite: bool = True
    ) -> bool:
        """
        Merge data from source container into target container.

        Args:
            target: The target GenContainer to merge data into
            source: The source GenContainer to get data from
            overwrite: Whether to overwrite existing values in target (default: True)

        Returns:
            True if successful, False otherwise

        Example:
            # Merge data from container2 into container1
            component.merge_container_data(container1, container2)
        """
        if not all(isinstance(c, GenContainer) for c in [target, source]):
            print(f"Warning: Invalid containers provided to merge_container_data")
            return False

        try:
            # Get all GenTypes from source
            source_types = source.get_name_in_Data()

            # For each GenType in source
            for gen_type in source_types:
                # If target doesn't have this GenType, add it
                if gen_type not in target.Data:
                    target.insert(copy.deepcopy(source.Data[gen_type]))
                else:
                    # If target has this GenType, merge attributes
                    source_attrs = source.Data[gen_type].attributes
                    for attr_name, attr in source_attrs.items():
                        if (
                            overwrite
                            or attr_name not in target.Data[gen_type].attributes
                        ):
                            target.Data[gen_type].update_value(attr_name, attr.value)

            return True
        except Exception as e:
            print(f"Error merging container data: {e}")
            return False

    # Simulation Flow Control Helpers

    def wait(self, duration: int) -> TypingGen[Any, Any, None]:
        """
        Wait for a specified duration in simulation time.
        This is a wrapper for SimPy's timeout.

        Args:
            duration: The duration to wait in simulation time units

        Returns:
            A generator that yields a timeout event

        Example:
            # Wait for 5 time units
            yield component.wait(5)
        """
        yield self.env.timeout(duration)

    def wait_until(self, time_point: int) -> TypingGen[Any, Any, None]:
        """
        Wait until a specific simulation time point.

        Args:
            time_point: The absolute simulation time to wait until

        Returns:
            A generator that yields a timeout event

        Example:
            # Wait until simulation time 100
            yield component.wait_until(100)
        """
        current_time = self.env.now
        if time_point <= current_time:
            # Already past the time point, return immediately
            return

        wait_duration = time_point - current_time
        yield self.env.timeout(wait_duration)

    def wait_random(
        self, min_duration: int, max_duration: int
    ) -> TypingGen[Any, Any, None]:
        """
        Wait for a random duration between min_duration and max_duration.

        Args:
            min_duration: The minimum duration to wait
            max_duration: The maximum duration to wait

        Returns:
            A generator that yields a timeout event

        Example:
            # Wait for a random duration between 5 and 10 time units
            yield component.wait_random(5, 10)
        """
        duration = random.randint(min_duration, max_duration)
        yield self.env.timeout(duration)

    # Component Communication Helpers

    def get_component_by_id(self, comp_id: str) -> Optional["Component"]:
        """
        Get a component reference by ID.

        Args:
            comp_id: The ID of the component to retrieve

        Returns:
            The component instance or None if not found

        Example:
            # Get a reference to a component with ID 'resource1'
            resource = component.get_component_by_id('resource1')
        """
        return self.comp_from_registery(comp_id)

    def get_components_by_type(self, comp_type: str) -> List["Component"]:
        """
        Get all components of a specific type.

        Args:
            comp_type: The type of components to retrieve

        Returns:
            A list of component instances of the specified type

        Example:
            # Get all Resource components
            resources = component.get_components_by_type('Resource')
        """
        components = []
        for comp_id in self.get_registry_keys():
            comp = self.get_component_by_id(comp_id)
            if comp and comp.type == comp_type:
                components.append(comp)
        return components

    def send_to_component(
        self, container: GenContainer, comp_id: str, handler: Optional[str] = None
    ) -> bool:
        """
        Send a container directly to a specific component.

        Args:
            container: The GenContainer to send
            comp_id: The ID of the target component
            handler: Optional handler name (if None, will use default handler)

        Returns:
            True if successful, False otherwise

        Example:
            # Send a container to component 'resource1' with handler 'Water-in'
            component.send_to_component(container, 'resource1', 'Water-in')
        """
        if container is None or not isinstance(container, GenContainer):
            print(f"Warning: Invalid container provided to send_to_component")
            return False

        # Get the target component
        target_comp = self.get_component_by_id(comp_id)
        if target_comp is None:
            print(f"Warning: Target component '{comp_id}' not found")
            return False

        # Set the target component and handler
        container.targetComp = comp_id
        if handler:
            container.targetHandler = handler
        else:
            # Try to determine a default handler
            gen_types = container.get_name_in_Data()
            if len(gen_types) == 1:
                container.targetHandler = f"{gen_types[0]}-in"
            else:
                print(
                    f"Warning: No handler specified and multiple GenTypes in container"
                )
                return False

        # Start the process in the target component
        try:
            self.env.process(target_comp.run(container))
            return True
        except Exception as e:
            print(f"Error sending container to component: {e}")
            return False

    # Data Storage and Retrieval Helpers

    def store_data(self, key: str, value: Any) -> bool:
        """
        Store data in component's KVStorage.

        Args:
            key: The key to store the value under
            value: The value to store

        Returns:
            True if successful, False otherwise

        Example:
            # Store a counter value
            component.store_data('processed_count', 42)
        """
        try:
            self.var.set(key, value)
            return True
        except Exception as e:
            print(f"Error storing data: {e}")
            return False

    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Get data from component's KVStorage.

        Args:
            key: The key to retrieve
            default: The default value to return if key not found

        Returns:
            The stored value or default if not found

        Example:
            # Get a counter value, defaulting to 0 if not found
            count = component.get_data('processed_count', 0)
        """
        value = self.var.get(key)
        return default if value is None else value

    def increment_counter(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in KVStorage.

        Args:
            key: The key of the counter to increment
            amount: The amount to increment by (default: 1)

        Returns:
            The new counter value

        Example:
            # Increment a counter
            new_count = component.increment_counter('processed_count')
        """
        current = self.get_data(key, 0)
        if not isinstance(current, (int, float)):
            current = 0
        new_value = current + amount
        self.store_data(key, new_value)
        return new_value

    def decrement_counter(self, key: str, amount: int = 1) -> int:
        """
        Decrement a counter in KVStorage.

        Args:
            key: The key of the counter to decrement
            amount: The amount to decrement by (default: 1)

        Returns:
            The new counter value

        Example:
            # Decrement a counter
            new_count = component.decrement_counter('remaining_items')
        """
        return self.increment_counter(key, -amount)

    # Logging and Monitoring Helpers

    def log_custom_event(
        self,
        action: str,
        values: Dict[str, Any],
        container: Optional[GenContainer] = None,
    ) -> None:
        """
        Log a custom event with optional container data.

        Args:
            action: The action name for the event
            values: Dictionary of values to log
            container: Optional GenContainer to include in the log

        Example:
            # Log a custom processing event
            component.log_custom_event('CUSTOM_PROCESS', {'duration': 5}, container)
        """
        pdv = container.Display() if container else None
        self.log_event(action, values, pdv)

    def get_current_time(self) -> int:
        """
        Get the current simulation time.

        Returns:
            The current simulation time

        Example:
            # Get the current simulation time
            current_time = component.get_current_time()
        """
        return self.env.now

    def track_metric(self, metric_name: str, value: Any) -> None:
        """
        Track a custom metric by storing it and logging it.

        Args:
            metric_name: The name of the metric to track
            value: The value of the metric

        Example:
            # Track a processing time metric
            component.track_metric('processing_time', 5.2)
        """
        # Store the metric in KVStorage
        metrics = self.get_data("metrics", {})
        if not isinstance(metrics, dict):
            metrics = {}

        # Add the new metric value
        if metric_name not in metrics:
            metrics[metric_name] = []
        metrics[metric_name].append((self.get_current_time(), value))

        # Store the updated metrics
        self.store_data("metrics", metrics)

        # Log the metric
        self.log_custom_event(
            "METRIC",
            {
                "metric_name": metric_name,
                "value": value,
                "time": self.get_current_time(),
            },
        )

    def run_ml_model(self, model_name: str, input_data: Any, model_dir: str = None) -> Any:
        """
        Load and run a machine learning model with the provided input data.

        This method allows components to use machine learning models in their processing logic.
        It supports various ML frameworks including scikit-learn, TensorFlow, PyTorch, and
        models saved with joblib or pickle.

        Args:
            model_name: Name of the model file (without extension)
            input_data: Input data to pass to the model for prediction
            model_dir: Directory containing the model files (default: 'models')
                       If None, will use the default models directory

        Returns:
            The model's prediction/output or None if the model couldn't be loaded or run

        Example:
            # Run a scikit-learn model to predict processing time
            features = [temperature, volume, pressure]
            predicted_time = component.run_ml_model('processing_time_predictor', features)

            # Use the prediction
            if predicted_time is not None:
                yield component.wait(predicted_time)
        """
        import os
        import importlib
        import sys
        from pathlib import Path

        # Set default models directory if not provided
        if model_dir is None:
            model_dir = os.path.join(os.getcwd(), "models")

        # Ensure the models directory exists
        os.makedirs(model_dir, exist_ok=True)

        # Log the model execution attempt
        self.log_custom_event(
            "ML_MODEL_RUN",
            {
                "model_name": model_name,
                "time": self.get_current_time(),
            },
        )

        # Try to load and run the model
        try:
            # Check for different model file formats
            model_path = None
            model = None

            # Look for .pkl or .joblib files (scikit-learn, general pickle)
            for ext in ['.pkl', '.joblib', '.pickle']:
                path = os.path.join(model_dir, f"{model_name}{ext}")
                if os.path.exists(path):
                    model_path = path
                    break

            # Look for saved model directories (TensorFlow)
            tf_path = os.path.join(model_dir, model_name)
            if os.path.isdir(tf_path) and os.path.exists(os.path.join(tf_path, 'saved_model.pb')):
                model_path = tf_path

            # Look for .pt or .pth files (PyTorch)
            for ext in ['.pt', '.pth']:
                path = os.path.join(model_dir, f"{model_name}{ext}")
                if os.path.exists(path):
                    model_path = path
                    break

            # Look for .py files (custom model implementations)
            py_path = os.path.join(model_dir, f"{model_name}.py")
            if os.path.exists(py_path):
                model_path = py_path

            if model_path is None:
                print(f"Error: Model '{model_name}' not found in directory '{model_dir}'")
                return None

            # Load the model based on file type
            if model_path.endswith('.pkl') or model_path.endswith('.pickle'):
                import pickle
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
            elif model_path.endswith('.joblib'):
                import joblib
                model = joblib.load(model_path)
            elif model_path.endswith('.pt') or model_path.endswith('.pth'):
                # Check if PyTorch is available
                if importlib.util.find_spec("torch") is not None:
                    import torch
                    model = torch.load(model_path)
                else:
                    print("Error: PyTorch is not installed but required for .pt/.pth models")
                    return None
            elif os.path.isdir(model_path) and os.path.exists(os.path.join(model_path, 'saved_model.pb')):
                # Check if TensorFlow is available
                if importlib.util.find_spec("tensorflow") is not None:
                    import tensorflow as tf
                    model = tf.saved_model.load(model_path)
                else:
                    print("Error: TensorFlow is not installed but required for saved_model.pb models")
                    return None
            elif model_path.endswith('.py'):
                # Add the models directory to the Python path temporarily
                sys.path.insert(0, os.path.dirname(model_path))

                # Import the module
                module_name = os.path.basename(model_path)[:-3]  # Remove .py extension
                module = importlib.import_module(module_name)

                # Look for predict function
                if hasattr(module, 'predict'):
                    # Call the predict function directly
                    result = module.predict(input_data)

                    # Remove the added path
                    sys.path.pop(0)

                    # Log successful prediction
                    self.log_custom_event(
                        "ML_MODEL_RESULT",
                        {
                            "model_name": model_name,
                            "success": True,
                            "time": self.get_current_time(),
                        },
                    )

                    return result
                else:
                    print(f"Error: Module '{module_name}' does not have a 'predict' function")

                    # Remove the added path
                    sys.path.pop(0)
                    return None
            else:
                print(f"Error: Unsupported model format for '{model_path}'")
                return None

            # Run the model
            if hasattr(model, 'predict'):
                result = model.predict(input_data)
            elif callable(model):
                result = model(input_data)
            else:
                print(f"Error: Model '{model_name}' does not have a predict method or is not callable")
                return None

            # Log successful prediction
            self.log_custom_event(
                "ML_MODEL_RESULT",
                {
                    "model_name": model_name,
                    "success": True,
                    "time": self.get_current_time(),
                },
            )

            return result

        except ImportError as e:
            print(f"Error: Required ML library not installed: {e}")

            # Log the error
            self.log_custom_event(
                "ML_MODEL_ERROR",
                {
                    "model_name": model_name,
                    "error": f"Required ML library not installed: {str(e)}",
                    "time": self.get_current_time(),
                },
            )

            return None

        except Exception as e:
            print(f"Error running ML model '{model_name}': {e}")

            # Log the error
            self.log_custom_event(
                "ML_MODEL_ERROR",
                {
                    "model_name": model_name,
                    "error": str(e),
                    "time": self.get_current_time(),
                },
            )

            return None

    # Error Handling Helpers

    def handle_error(
        self, error: Exception, container: Optional[GenContainer] = None
    ) -> None:
        """
        Handle and log an error.

        Args:
            error: The exception that occurred
            container: Optional GenContainer related to the error

        Example:
            # Handle an error that occurred during processing
            try:
                # Some processing code
                pass
            except Exception as e:
                component.handle_error(e, container)
        """
        error_msg = str(error)
        error_type = type(error).__name__

        # Log the error
        values = {
            "error_type": error_type,
            "error_message": error_msg,
            "time": self.get_current_time(),
        }

        pdv = container.Display() if container else None
        self.log_event("ERROR", values, pdv)

        # Print the error for debugging
        print(f"Error in component {self.compId}: {error_type} - {error_msg}")

    def validate_container(
        self, container: GenContainer, required_attributes: Dict[str, List[str]] = None
    ) -> bool:
        """
        Validate a container has required attributes.

        Args:
            container: The GenContainer to validate
            required_attributes: Dictionary mapping GenTypes to lists of required attributes

        Returns:
            True if valid, False otherwise

        Example:
            # Validate a container has required attributes
            is_valid = component.validate_container(
                container,
                {'Water': ['temperature', 'volume']}
            )
        """
        if container is None or not isinstance(container, GenContainer):
            print(f"Warning: Invalid container provided to validate_container")
            return False

        if not required_attributes:
            # No validation required
            return True

        # Check each GenType and its required attributes
        for gen_type, attributes in required_attributes.items():
            # Check if the GenType exists
            if gen_type not in container.Data:
                print(f"Validation failed: GenType '{gen_type}' not found in container")
                return False

            # Check each required attribute
            for attr in attributes:
                if container.Data[gen_type].get_value(attr) is None:
                    print(
                        f"Validation failed: Attribute '{attr}' not found in GenType '{gen_type}'"
                    )
                    return False

        return True

    # Utility Functions

    def format_time(self, time_value: int) -> str:
        """
        Format a time value for display.

        Args:
            time_value: The time value to format

        Returns:
            A formatted time string

        Example:
            # Format the current time
            formatted_time = component.format_time(component.get_current_time())
        """
        return f"T+{time_value}"

    def calculate_duration(self, start_time: int, end_time: int) -> int:
        """
        Calculate duration between two time points.

        Args:
            start_time: The start time
            end_time: The end time

        Returns:
            The duration between the two times

        Example:
            # Calculate processing duration
            duration = component.calculate_duration(start_time, component.get_current_time())
        """
        return max(0, end_time - start_time)

    def generate_id(self, prefix: str = "") -> str:
        """
        Generate a unique ID.

        Args:
            prefix: Optional prefix for the ID

        Returns:
            A unique ID string

        Example:
            # Generate a unique ID for a batch
            batch_id = component.generate_id('batch-')
        """
        unique_id = str(uuid.uuid4())
        return f"{prefix}{unique_id}" if prefix else unique_id

    def generate_component_insights(self, csv_scraper) -> ComponentOutput:
        """
        Generate component-specific insights and visualizations.

        This method uses the analytics system to generate insights specific to this
        component's type and behavior. It also checks for user-defined visualization
        methods (outputCharts and outputTable) in the component's event code.

        Args:
            csv_scraper: CSVScraper instance for accessing simulation data

        Returns:
            ComponentOutput object with charts and cards
        """
        # Create output container
        output = ComponentOutput(
            id=self.compId,
            name=f"{self.category.capitalize()} {self.compId}",
            type=self.category
        )

        # First, check if the user has defined custom visualization methods

        # Check for outputCharts method in the event code
        output_charts_func = self.executor.execute_event_function("outputCharts")
        if output_charts_func:
            try:
                # Run the outputCharts method and pass self as the component parameter
                charts = output_charts_func(self)
                if charts and isinstance(charts, list):
                    for chart in charts:
                        if hasattr(chart, 'type') and chart.type in ['chart', 'card']:
                            output.add_chart(chart)
                print(f"Custom charts generated for component {self.compId}")
            except Exception as e:
                print(f"Error executing outputCharts method for component {self.compId}: {e}")

        # Check for outputTable method in the event code
        output_table_func = self.executor.execute_event_function("outputTable")
        if output_table_func:
            try:
                # Run the outputTable method and pass self as the component parameter
                tables = output_table_func(self)
                if tables and isinstance(tables, list):
                    for table in tables:
                        if isinstance(table, dict) and 'data' in table:
                            output.add_table(table)
                print(f"Custom tables generated for component {self.compId}")
            except Exception as e:
                print(f"Error executing outputTable method for component {self.compId}: {e}")

        # If no custom visualizations were defined or they didn't produce any output,
        # fall back to the analytics system
        if not output.dashboradData and not output.dashboardTable:
            # Create an appropriate analytics instance for this component
            analytics = AnalyticsFactory.create_analytics(
                component_id=self.compId,
                component_type=self.category,
                csv_scraper=csv_scraper,
            )

            # Generate insights
            return analytics.generate_component_insights()

        return output


class Generator(Component):
    def __init__(
        self,
        env: simpy.Environment,
        compData: CompDataI,
    ):
        super().__init__(
            env=env,
            name="Generator",
            compData=compData,
        )
        genlist = (
            []
            if compData.GenData is None or compData.GenData.types is None
            else compData.GenData.types
        )
        self.GenList = self.initGenType(genlist)

        self.generated_count = 0
        default_actions = ["GENERATE"]
        self.set_actionSet(default_actions)
        row_gencount = compData.get_input_data("gen_count")
        if isinstance(row_gencount, int):
            self.gen_count = row_gencount
        else:
            self.gen_count = None
        print(f"Generator {self.compId} initialized with gen_count: {self.gen_count}")

    @classmethod
    def create(cls, env: simpy.Environment, compData: CompDataI) -> "Generator":
        return Generator(env=env, compData=compData)

    def next_wrapper(self):
        # before calling next() method, user can decide which compoent to call
        pass

    def defult_output(self):
        pass

    def GenContainerBuild(self, input: GenContainer):
        pass

    def initGenType(self, data: List[str]) -> dict[str, int]:
        genTypes = {}
        for i in data:
            genTypes[i] = 0
        return genTypes

    def BrakeLoop(self) -> GenContainer:
        return GenContainer(
            Data={},
            targetComp=None,
            targetHandler=None,
            Flag="BREAK",
        )

    def inc_Gen_Count(self):
        self.generated_count += 1

    def genCountInc(self, input: GenContainer):
        keys = input.get_name_in_Data()
        for i in keys:
            self.GenList[i] = self.GenList.get(i, 0) + 1

    def exec_gen_fn(self):
        """
        Gets the generator function to be executed.
        Adds additional error checking around the executor.
        """
        try:
            func = self.executor.execute_gen_function()
            return func
        except AttributeError as e:
            print(
                f"Error in execute_gen_function: {e}. Check namespace naming in CodeExec class."
            )
            return None
        except Exception as e:
            print(f"Unexpected error when getting generator function: {e}")
            return None

    #
    # GENERATOR HELPER METHODS
    # These methods are designed to help users write custom generator functions
    #

    def create_entity(
        self, gen_type: str, attributes: Dict[str, Any] = None
    ) -> GenContainer:
        """
        Create a new entity with specified attributes.

        Args:
            gen_type: The name of the generator type
            attributes: Dictionary of attribute values to set (optional)

        Returns:
            A new GenContainer with the specified attributes

        Example:
            # Create a new Water entity with temperature 25
            container = component.create_entity('Water', {'temperature': 25, 'volume': 100})
        """
        # Create a default container for this gen_type
        container = self.create_default_container(gen_type)

        # Set attributes if provided
        if attributes:
            gen_id = container.get_name_in_Data()[0]
            for key, value in attributes.items():
                try:
                    container.Data[gen_id].update_value(key, value)
                except Exception as e:
                    print(f"Error setting attribute {key}: {e}")

        # Set the target handler
        container = self.send_genOutput_next(container, gen_type)

        return container

    def create_batch(
        self, gen_type: str, count: int, attributes: Dict[str, Any] = None
    ) -> List[GenContainer]:
        """
        Create multiple entities at once.

        Args:
            gen_type: The name of the generator type
            count: Number of entities to create
            attributes: Dictionary of attribute values to set (optional)

        Returns:
            List of new GenContainers

        Example:
            # Create 5 Water entities with the same attributes
            containers = component.create_batch('Water', 5, {'temperature': 25})
        """
        containers = []
        for _ in range(count):
            container = self.create_entity(gen_type, attributes)
            containers.append(container)
        return containers

    def create_entity_with_variations(
        self,
        gen_type: str,
        base_attributes: Dict[str, Any],
        variations: Dict[str, Tuple[float, float]] = None,
    ) -> GenContainer:
        """
        Create an entity with random variations of attributes.

        Args:
            gen_type: The name of the generator type
            base_attributes: Base attribute values
            variations: Dictionary mapping attribute names to (min_variation, max_variation) tuples

        Returns:
            A new GenContainer with varied attributes

        Example:
            # Create a Water entity with temperature varying between 20-30
            container = component.create_entity_with_variations(
                'Water',
                {'temperature': 25, 'volume': 100},
                {'temperature': (-5, 5)}
            )
        """
        # Start with base attributes
        attributes = base_attributes.copy() if base_attributes else {}

        # Apply variations if provided
        if variations:
            for attr, (min_var, max_var) in variations.items():
                if attr in attributes and isinstance(attributes[attr], (int, float)):
                    base_value = attributes[attr]
                    variation = random.uniform(min_var, max_var)
                    attributes[attr] = base_value + variation

        # Create the entity with the varied attributes
        return self.create_entity(gen_type, attributes)

    def set_generation_rate(self, rate: int) -> None:
        """
        Set the generation rate by storing it in the component's KVStorage.

        Args:
            rate: The new generation rate (entities per time unit)

        Example:
            # Set generation rate to 5 entities per time unit
            component.set_generation_rate(5)
        """
        self.store_data("generation_rate", rate)

    def get_generation_rate(self) -> int:
        """
        Get the current generation rate from the component's KVStorage.

        Returns:
            The current generation rate

        Example:
            # Get the current generation rate
            rate = component.get_generation_rate()
        """
        return self.get_data("generation_rate", 1)  # Default to 1 if not set

    def pause_generation(self) -> None:
        """
        Pause generation by setting a flag in the component's KVStorage.

        Example:
            # Pause generation
            component.pause_generation()
        """
        self.store_data("generation_paused", True)

    def resume_generation(self) -> None:
        """
        Resume generation by clearing the pause flag in the component's KVStorage.

        Example:
            # Resume generation
            component.resume_generation()
        """
        self.store_data("generation_paused", False)

    def is_generation_paused(self) -> bool:
        """
        Check if generation is currently paused.

        Returns:
            True if generation is paused, False otherwise

        Example:
            # Check if generation is paused
            if component.is_generation_paused():
                # Do something
        """
        return self.get_data("generation_paused", False)

    def stop_generation(self) -> None:
        """
        Stop generation completely by setting the gen_count to 0.

        Example:
            # Stop generation
            component.stop_generation()
        """
        self.gen_count = 0

    def generate_with_normal_distribution(
        self, gen_type: str, attribute: str, mean: float, std_dev: float
    ) -> GenContainer:
        """
        Generate an entity with an attribute following a normal distribution.

        Args:
            gen_type: The name of the generator type
            attribute: The attribute to set with a normally distributed value
            mean: The mean of the normal distribution
            std_dev: The standard deviation of the normal distribution

        Returns:
            A new GenContainer with the normally distributed attribute

        Example:
            # Create a Water entity with temperature following normal distribution
            container = component.generate_with_normal_distribution('Water', 'temperature', 25, 5)
        """
        # Generate a value from the normal distribution
        value = random.normalvariate(mean, std_dev)

        # Create an entity with this value
        return self.create_entity(gen_type, {attribute: value})

    def generate_with_exponential_distribution(
        self, gen_type: str, attribute: str, lambda_val: float
    ) -> GenContainer:
        """
        Generate an entity with an attribute following an exponential distribution.

        Args:
            gen_type: The name of the generator type
            attribute: The attribute to set with an exponentially distributed value
            lambda_val: The lambda parameter of the exponential distribution

        Returns:
            A new GenContainer with the exponentially distributed attribute

        Example:
            # Create a Customer entity with service_time following exponential distribution
            container = component.generate_with_exponential_distribution('Customer', 'service_time', 0.5)
        """
        # Generate a value from the exponential distribution
        value = random.expovariate(lambda_val)

        # Create an entity with this value
        return self.create_entity(gen_type, {attribute: value})

    def generate_with_uniform_distribution(
        self, gen_type: str, attribute: str, min_val: float, max_val: float
    ) -> GenContainer:
        """
        Generate an entity with an attribute following a uniform distribution.

        Args:
            gen_type: The name of the generator type
            attribute: The attribute to set with a uniformly distributed value
            min_val: The minimum value of the uniform distribution
            max_val: The maximum value of the uniform distribution

        Returns:
            A new GenContainer with the uniformly distributed attribute

        Example:
            # Create a Water entity with temperature uniformly distributed between 20 and 30
            container = component.generate_with_uniform_distribution('Water', 'temperature', 20, 30)
        """
        # Generate a value from the uniform distribution
        value = random.uniform(min_val, max_val)

        # Create an entity with this value
        return self.create_entity(gen_type, {attribute: value})

    def run(self, input: Optional[GenContainer]) -> TypingGen[Any, Any, Any]:
        # Check if required class resources are initialized
        if not Component._initialized:
            print(
                "WARNING: Component class resources are not initialized. Cannot run generator."
            )
            return None

        # infinite or bounded loop
        loop = self.gen_count
        if loop == 0:
            loop = None
        print(f"[loop] {loop}")
        while loop is None or loop > 0:
            self.inc_run_call_count()
            self.input_count = getattr(self, "input_count", 0) + 1

            # Get the generator function
            func = self.exec_gen_fn()
            if func is None:
                print("Warning: No generator function found. Breaking loop.")
                break

            # get a new GenContainer from the user's logic
            try:
                output: GenContainer = yield from func(self)
                self.log_event(
                    action="IN",
                    values={
                        "input_count": self.input_count,
                        "run_count": self.run_call_count,
                        "out_time": self.env.now,
                    },
                    PDV=output.Display(),
                )
                # Validate output is a GenContainer
                if not isinstance(output, GenContainer):
                    print(
                        f"Warning: Generator function returned {type(output)}, not GenContainer. Breaking loop."
                    )
                    break

            except Exception as e:
                print(f"Error in generator function: {e}")
                break

            if output.Flag == "BREAK":
                print("Generator received BREAK flag. Breaking loop.")
                break

            self.log_event(
                action="GENERATE",
                values={
                    "input_count": self.input_count,
                    "run_count": self.run_call_count,
                    "out_time": self.env.now,
                },
                PDV=output.Display(),
            )

            self.genCountInc(output)
            self.log_event(
                action="OUT",
                values={
                    "input_count": self.input_count,
                    "run_count": self.run_call_count,
                    "out_time": self.env.now,
                },
                PDV=output.Display(),
            )

            # Pass output to next component
            self._next(output)

            self.inc_Gen_Count()
            if loop is not None:
                loop -= 1


class Resource(Component):
    def __init__(
        self,
        env: simpy.Environment,
        compData: CompDataI,
    ):
        super().__init__(
            env=env,
            name="Resource",
            compData=compData,
        )
        default_actions = ["ENTER", "EXIT", "PROCESSING"]
        self.set_actionSet(default_actions)

        # Retrieve and validate the capacity value from component data
        capacity = compData.get_input_data("capacity")

        if capacity is None:
            raise ValueError("Component 'Resource' requires 'capacity' to be defined.")

        if not isinstance(capacity, int):
            raise TypeError(
                f"Capacity must be an integer, got {type(capacity).__name__} instead."
            )

        self.capacity: int = capacity
        self.resource = simpy.Resource(env, capacity=self.capacity)

    @classmethod
    def create(cls, env: simpy.Environment, compData: CompDataI) -> "Resource":
        return Resource(env=env, compData=compData)

    def next_wrapper(self):
        # before calling next() method, user can decide which compoent to call
        pass

    def defult_output(self):
        pass

    def test_func(self, input: Optional[GenContainer]) -> TypingGen[Any, Any, Any]:
        yield self.env.timeout(1)
        return input

    #
    # RESOURCE HELPER METHODS
    # These methods are designed to help users write custom resource functions
    #

    def get_capacity(self) -> int:
        """
        Get the current capacity of the resource.

        Returns:
            The current capacity

        Example:
            # Get the current capacity
            capacity = component.get_capacity()
        """
        return self.capacity

    def set_capacity(self, capacity: int) -> None:
        """
        Set a new capacity for the resource.
        Note: This only affects future requests, not current ones.

        Args:
            capacity: The new capacity value

        Example:
            # Set a new capacity
            component.set_capacity(5)
        """
        if not isinstance(capacity, int) or capacity <= 0:
            print(
                f"Warning: Invalid capacity value: {capacity}. Must be a positive integer."
            )
            return

        # Create a new resource with the new capacity
        old_resource = self.resource
        self.capacity = capacity
        self.resource = simpy.Resource(self.env, capacity=self.capacity)

        # Log the capacity change
        self.log_custom_event(
            "CAPACITY_CHANGE",
            {
                "old_capacity": old_resource.capacity,
                "new_capacity": self.capacity,
                "time": self.get_current_time(),
            },
        )

    def get_utilization(self) -> float:
        """
        Get the current utilization of the resource (0.0 to 1.0).

        Returns:
            The current utilization as a float between 0.0 and 1.0

        Example:
            # Get the current utilization
            util = component.get_utilization()
            if util > 0.8:
                print("Resource is heavily utilized")
        """
        if self.capacity == 0:
            return 0.0

        # Calculate utilization as users / capacity
        return len(self.resource.users) / self.capacity

    def get_queue_length(self) -> int:
        """
        Get the current queue length.

        Returns:
            The current queue length

        Example:
            # Get the current queue length
            queue_length = component.get_queue_length()
        """
        return len(self.resource.queue)

    def is_available(self) -> bool:
        """
        Check if the resource has available capacity.

        Returns:
            True if the resource has available capacity, False otherwise

        Example:
            # Check if the resource is available
            if component.is_available():
                # Process something
        """
        return len(self.resource.users) < self.capacity

    def get_queue_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the queue.

        Returns:
            Dictionary with queue statistics

        Example:
            # Get queue statistics
            stats = component.get_queue_statistics()
            print(f"Average queue length: {stats['avg_length']}")
        """
        # Get queue length history from KVStorage
        queue_history = self.get_data("queue_history", [])

        # Add current queue length to history
        current_length = self.get_queue_length()
        current_time = self.get_current_time()
        queue_history.append((current_time, current_length))

        # Store updated history
        self.store_data("queue_history", queue_history)

        # Calculate statistics
        if not queue_history:
            return {
                "current_length": 0,
                "max_length": 0,
                "avg_length": 0,
                "total_queued": 0,
            }

        lengths = [length for _, length in queue_history]
        return {
            "current_length": current_length,
            "max_length": max(lengths),
            "avg_length": sum(lengths) / len(lengths),
            "total_queued": len(queue_history),
        }

    def process_with_timeout(
        self, container: GenContainer, duration: int
    ) -> TypingGen[Any, Any, GenContainer]:
        """
        Process a container with a specified timeout.

        Args:
            container: The GenContainer to process
            duration: The processing duration

        Returns:
            The processed GenContainer

        Example:
            # Process a container for 5 time units
            processed_container = yield from component.process_with_timeout(container, 5)
        """
        # Log the start of processing
        self.log_custom_event(
            "PROCESSING_START",
            {"duration": duration, "start_time": self.get_current_time()},
            container,
        )

        # Wait for the specified duration
        yield self.env.timeout(duration)

        # Log the end of processing
        self.log_custom_event(
            "PROCESSING_END",
            {"duration": duration, "end_time": self.get_current_time()},
            container,
        )

        return container

    def process_with_variable_time(
        self, container: GenContainer, attribute: str
    ) -> TypingGen[Any, Any, GenContainer]:
        """
        Process a container with a duration specified by an attribute in the container.

        Args:
            container: The GenContainer to process
            attribute: The attribute name containing the processing duration

        Returns:
            The processed GenContainer

        Example:
            # Process a container using its 'processing_time' attribute
            processed_container = yield from component.process_with_variable_time(container, 'processing_time')
        """
        # Get the processing time from the container
        gen_types = container.get_name_in_Data()
        if not gen_types:
            print("Warning: Container has no GenTypes")
            return container

        gen_type = gen_types[0]
        try:
            duration = container.Data[gen_type].get_value(attribute)
            if duration is None or not isinstance(duration, (int, float)):
                print(
                    f"Warning: Invalid processing time in attribute '{attribute}': {duration}"
                )
                duration = 1  # Default to 1 time unit
        except Exception as e:
            print(f"Error getting processing time: {e}")
            duration = 1  # Default to 1 time unit

        # Process with the determined duration
        return (yield from self.process_with_timeout(container, duration))

    def calculate_processing_metrics(self, container: GenContainer) -> Dict[str, Any]:
        """
        Calculate processing metrics for a container.

        Args:
            container: The GenContainer to calculate metrics for

        Returns:
            Dictionary with processing metrics

        Example:
            # Calculate processing metrics for a container
            metrics = component.calculate_processing_metrics(container)
            print(f"Processing time: {metrics['processing_time']}")
        """
        # Get the current time
        current_time = self.get_current_time()

        # Get the container's entry time from its attributes or use current time
        gen_types = container.get_name_in_Data()
        if not gen_types:
            return {"processing_time": 0, "queue_time": 0, "total_time": 0}

        gen_type = gen_types[0]

        # Try to get entry time from container
        try:
            entry_time = container.Data[gen_type].get_value("entry_time")
            if entry_time is None:
                # Set entry time if not present
                entry_time = current_time
                container.Data[gen_type].update_value("entry_time", entry_time)
        except:
            # Set entry time if not present
            entry_time = current_time
            try:
                container.Data[gen_type].create_attribute(
                    "entry_time", "int", entry_time
                )
            except:
                pass

        # Try to get queue entry time from container
        try:
            queue_entry_time = container.Data[gen_type].get_value("queue_entry_time")
            if queue_entry_time is None:
                queue_entry_time = entry_time
        except:
            queue_entry_time = entry_time

        # Calculate metrics
        processing_time = current_time - queue_entry_time
        queue_time = queue_entry_time - entry_time
        total_time = current_time - entry_time

        return {
            "processing_time": max(0, processing_time),
            "queue_time": max(0, queue_time),
            "total_time": max(0, total_time),
            "entry_time": entry_time,
            "queue_entry_time": queue_entry_time,
            "exit_time": current_time,
        }

    def mark_queue_entry(self, container: GenContainer) -> GenContainer:
        """
        Mark the time a container enters the queue.

        Args:
            container: The GenContainer entering the queue

        Returns:
            The updated GenContainer

        Example:
            # Mark a container as entering the queue
            container = component.mark_queue_entry(container)
        """
        current_time = self.get_current_time()
        gen_types = container.get_name_in_Data()

        if not gen_types:
            return container

        gen_type = gen_types[0]

        # Try to set queue entry time
        try:
            container.Data[gen_type].update_value("queue_entry_time", current_time)
        except:
            try:
                container.Data[gen_type].create_attribute(
                    "queue_entry_time", "int", current_time
                )
            except Exception as e:
                print(f"Error marking queue entry: {e}")

        return container

    def mark_processing_start(self, container: GenContainer) -> GenContainer:
        """
        Mark the time a container starts processing.

        Args:
            container: The GenContainer starting processing

        Returns:
            The updated GenContainer

        Example:
            # Mark a container as starting processing
            container = component.mark_processing_start(container)
        """
        current_time = self.get_current_time()
        gen_types = container.get_name_in_Data()

        if not gen_types:
            return container

        gen_type = gen_types[0]

        # Try to set processing start time
        try:
            container.Data[gen_type].update_value("processing_start_time", current_time)
        except:
            try:
                container.Data[gen_type].create_attribute(
                    "processing_start_time", "int", current_time
                )
            except Exception as e:
                print(f"Error marking processing start: {e}")

        return container

    def run(self, input: Optional[GenContainer]) -> TypingGen[Any, Any, Any]:
        """
        this the method called when simulation need to run a process. previous component will send the input to this component.
        that way inside this fn will decide what are the thing should be done and need to be returned.
        inside this fn, user can call the custom code and pass the self to it.
        """
        self.inc_run_call_count()
        self.input_count = getattr(self, "input_count", 0) + 1

        if input is None:
            return

        # run method for resource
        with self.resource.request() as req:
            # Log QUEUED event with queue length
            self.log_event(
                action="QUEUED",
                values={
                    "queue_length": len(self.resource.queue),
                    "in_time": self.env.now,
                },
                PDV=input.Display(),
            )
            yield req
            # Log the IN event with queue length
            self.log_event(
                action="IN",
                values={
                    "queue_length": len(self.resource.queue),
                    "input_count": self.input_count,
                    "run_count": self.run_call_count,
                },
                PDV=input.Display(),
            )
            func_name, is_gen = self.input_processing(input)
            if func_name is None:
                return
            func = None
            if is_gen:
                func = self.executor.execute_genCustom_function(func_name)
            else:
                func = self.executor.execute_run_function(func_name)

            if func is None:
                return

            output: GenContainer = yield from func(self, input)

        # Log the OUT event with queue length
        if output is not None and output.targetHandler is not None:
            b, _ = output.targetHandler.rsplit("-", 1)
            output.targetHandler = b + "-out"
        if output is not None:
            self.log_event(
                action="OUT",
                values={
                    "queue_length": len(self.resource.queue),
                    "input_count": self.input_count,
                    "run_count": self.run_call_count,
                    "out_time": self.env.now,
                    "type": "out",
                },
                PDV=output.Display(),
            )
            self._next(output=output)
