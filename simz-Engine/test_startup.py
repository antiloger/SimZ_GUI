import simpy
from src.sim.comp import Component, Generator, Resource
from src.sim.sim_types import CompDataI, RunnerFile, DataGenerator, ConfigGenerator, TimeStepGenConfig
from src.sim.kvstorage import KVStorage
from src.sim.graph import WorkflowGraph
from src.sim.db import CsvLogger
from src.sim.sim_types import GenTypeState

# Create a simple test environment
env = simpy.Environment()

# Create a workflow graph
workflow = WorkflowGraph()

# Create a logger with required fieldnames
logger = CsvLogger("test_log.csv", fieldnames=["time", "component_id", "component_type", "action", "values", "PDV", "addition"])

# Create a GenTypeState with an empty dictionary
gen_state = GenTypeState(root={})

# Set up Component class resources
Component.set_workflow(workflow)
Component.set_logger(logger)
Component.set_Gen_ref(gen_state)

# Create event code with a startup method
event_code = """
def startup(component):
    print(f"Startup method called for component {component.compId}")
    # Initialize some variables in the component's KVStorage
    component.var.set("initialized", True)
    component.var.set("counter", 0)
    component.var.set("name", "TestComponent")
    return True
"""

# Create a CompDataI instance with the event code
comp_data = CompDataI(
    id="test_component",
    compName="TestComponent",
    typeName="Resource",
    category="Resource",
    inputData={"capacity": 1},
    customInput={},
    connectors=[],
    Runners=RunnerFile(
        run="",
        model="",
        generator="",
        event=event_code
    ),
    GenData=DataGenerator(
        types=["test"],
        config=ConfigGenerator(
            genFn="test",
            config=TimeStepGenConfig()
        )
    ),
    Yieldable=True
)

# Create a Resource component
resource = Resource(env=env, compData=comp_data)

# Check if the variables were set in the KVStorage
print(f"Initialized: {resource.var.get('initialized')}")
print(f"Counter: {resource.var.get('counter')}")
print(f"Name: {resource.var.get('name')}")

# Create another component without a startup method
comp_data_no_startup = CompDataI(
    id="test_component_no_startup",
    compName="TestComponentNoStartup",
    typeName="Resource",
    category="Resource",
    inputData={"capacity": 1},
    customInput={},
    connectors=[],
    Runners=RunnerFile(
        run="",
        model="",
        generator="",
        event=""
    ),
    GenData=DataGenerator(
        types=["test"],
        config=ConfigGenerator(
            genFn="test",
            config=TimeStepGenConfig()
        )
    ),
    Yieldable=True
)

# Create a Resource component without a startup method
resource_no_startup = Resource(env=env, compData=comp_data_no_startup)

# Check if the variables were set in the KVStorage (should be None)
print(f"Initialized (should be None): {resource_no_startup.var.get('initialized')}")
print(f"Counter (should be None): {resource_no_startup.var.get('counter')}")
print(f"Name (should be None): {resource_no_startup.var.get('name')}")

print("Test completed.")
