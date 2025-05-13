from typing import Any, Dict, Optional, List, Generator as TypingGen
import simpy
from src.sim.codeExec import CodeExec
from src.sim.db import CsvLogger
from src.sim.graph import WorkflowGraph
from src.sim.kvstorage import KVStorage
from src.sim.sim_types import CompDataI, GenContainer, GenTypeState, GenTypes
from abc import ABC, abstractmethod
import weakref


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
                print(f"Error executing startup method for component {self.compId}: {e}")
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

    def send_genOutput_next(self, input: GenContainer, genType: str, func_name: str = None) -> GenContainer:
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
        if func_name:
            # Set the target handler to the function name with "-in" suffix
            # This will route to a specific function in the target component
            input.targetHandler = f"{func_name}-in"
        else:
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
            print(f"Using source handler: {input.targetHandler} for component {self.compId}")

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
            self.log_event(
                action="QUEUED",
                values={
                    "queue_length": len(self.resource.queue),
                    "in_time": self.env.now,
                },
                PDV=input.Display(),
            )
            yield req
            # Log the event of resource allocation
            self.log_event(
                action="ENTER",
                values={
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

        # Log the event of resource allocation
        self.log_event(
            action="Exit",
            values={
                "input_count": self.input_count,
                "run_count": self.run_call_count,
                "out_time": self.env.now,
            },
            PDV=input.Display(),
        )
        if output is not None and output.targetHandler is not None:
            b, _ = output.targetHandler.rsplit("-", 1)
            output.targetHandler = b + "-out"
        self._next(output=output)
