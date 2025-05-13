import simpy
from src.sim.comp import Component, Generator, Resource
from src.sim.sim_types import CompDataI, RunnerFile, DataGenerator, ConfigGenerator, TimeStepGenConfig
from src.sim.kvstorage import KVStorage
from src.sim.graph import WorkflowGraph
from src.sim.db import CsvLogger
from src.sim.sim_types import GenTypeState, GenTypes, GenAttributes, GenContainer

# Create a simple test environment
env = simpy.Environment()

# Create a workflow graph
workflow = WorkflowGraph()

# We'll add edges to the workflow graph later after creating the component

# Create a logger with required fieldnames
logger = CsvLogger("test_log.csv", fieldnames=["time", "component_id", "component_type", "action", "values", "PDV", "addition"])

# Create a GenTypeState with an empty dictionary
gen_state = GenTypeState(root={})

# Create test GenTypes
test_gen_type = GenTypes(
    typeName="test_type",
    genComponentId="test_component",
    attributes={
        "value": GenAttributes(type="int", value=42)
    }
)

custom_gen_type = GenTypes(
    typeName="custom_type",
    genComponentId="test_component",
    attributes={
        "value": GenAttributes(type="int", value=100)
    }
)

# Add the test GenTypes to the GenTypeState
gen_state.insert(test_gen_type)
gen_state.insert(custom_gen_type)

# Set up Component class resources
Component.set_workflow(workflow)
Component.set_logger(logger)
Component.set_Gen_ref(gen_state)

# Create generator code with functions that will be called
generator_code = """
def process_data(component, container):
    # This function would process the data in the container
    print(f"Processing data in container: {container.containerId}")
    yield component.env.timeout(1)
    return container

def special_process(component, container):
    # This function would perform special processing
    print(f"Special processing for container: {container.containerId}")
    yield component.env.timeout(1)
    return container

def generate(component):
    # This is just a placeholder for the test
    yield component.env.timeout(1)
    return component.BrakeLoop()
"""

# Create a CompDataI instance with the generator code
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
        generator=generator_code,
        event=""
    ),
    GenData=DataGenerator(
        types=["test_type"],
        config=ConfigGenerator(
            genFn="test",
            config=TimeStepGenConfig()
        )
    ),
    Yieldable=True
)

# Create a Resource component
resource = Resource(env=env, compData=comp_data)

# Add mock connections to the workflow graph for testing
# These connections don't need to point to real components for our test
from src.sim.sim_types import Edge as SimEdge

# Create edges for each possible output handler
workflow.add_edge(SimEdge(
    source="test_component",
    sourceHandle="process_data-in",
    target="mock_target_1",
    targetHandle="mock_handle_1",
    id="edge1"
))

workflow.add_edge(SimEdge(
    source="test_component",
    sourceHandle="special_process-in",
    target="mock_target_2",
    targetHandle="mock_handle_2",
    id="edge2"
))

workflow.add_edge(SimEdge(
    source="test_component",
    sourceHandle="test_type-out",
    target="mock_target_3",
    targetHandle="mock_handle_3",
    id="edge3"
))

workflow.add_edge(SimEdge(
    source="test_component",
    sourceHandle="custom_type-out",
    target="mock_target_4",
    targetHandle="mock_handle_4",
    id="edge4"
))

# Create a test container
def create_test_container():
    container = GenContainer(
        Data={
            "test_type": test_gen_type
        },
        targetComp=None,
        targetHandler=None
    )
    return container

# Test sending to a specific function
def test_specific_function():
    print("\nTesting sending to process_data function:")
    # Create a container
    container = create_test_container()
    # Set the target handler for process_data function
    result = resource.send_genOutput_next(container, "test_type", "process_data")
    print(f"Target handler set to: {result.targetHandler}")

# Test sending to another specific function
def test_another_function():
    print("\nTesting sending to special_process function:")
    # Create a container
    container = create_test_container()
    # Set the target handler for special_process function
    result = resource.send_genOutput_next(container, "test_type", "special_process")
    print(f"Target handler set to: {result.targetHandler}")

# Test with default routing (no function specified) for test_type
def test_default_routing():
    print("\nTesting default routing (no function specified) for test_type:")
    # Create a container
    container = create_test_container()
    # The default behavior should use the genType name as the handler
    result = resource.send_genOutput_next(container, "test_type")
    print(f"Target handler set to: {result.targetHandler}")

# Test with default routing for custom_type (which has a defined source handler in the workflow)
def test_custom_type_routing():
    print("\nTesting default routing for custom_type:")
    # Create a container with custom_type
    container = GenContainer(
        Data={
            "custom_type": custom_gen_type
        },
        targetComp=None,
        targetHandler=None
    )
    # The behavior should use the existing source handler in the workflow
    result = resource.send_genOutput_next(container, "custom_type")
    print(f"Target handler set to: {result.targetHandler}")

# Run the tests
test_specific_function()
test_another_function()
test_default_routing()
test_custom_type_routing()

print("\nTest completed.")
