#!/usr/bin/env python3
"""
Test script for component-specific analytics.

This script tests the component-specific analytics system by:
1. Creating a simple simulation with Generator and Resource components
2. Running the simulation to generate log data
3. Using the analytics system to generate insights
4. Verifying that the insights are correctly generated
"""

import os
import simpy
from pathlib import Path
import json

from src.sim.comp import Component, Generator, Resource
from src.sim.sim_types import CompDataI, RunnerFile, DataGenerator, ConfigGenerator, TimeStepGenConfig
from src.sim.kvstorage import KVStorage
from src.sim.graph import WorkflowGraph
from src.sim.db import CsvLogger
from src.sim.sim_types import GenTypeState, GenTypes, GenAttributes, GenContainer
from src.sim.csvpaser import CSVScraper
from src.sim.analytics import AnalyticsFactory, GeneratorAnalytics, ResourceAnalytics

# Create a simple test environment
env = simpy.Environment()

# Create a workflow graph
workflow = WorkflowGraph()

# Create a logger with required fieldnames
log_file = "test_analytics.csv"
logger = CsvLogger(
    log_file,
    fieldnames=["time", "component_id", "component_type", "action", "values", "PDV", "addition"]
)

# Create a GenTypeState with an empty dictionary
gen_state = GenTypeState(root={})

# Set up the component class variables
Component.set_Gen_ref(gen_state)
Component.set_workflow(workflow)
Component.set_logger(logger)

# Define a simple GenType for testing
water_type = GenTypes(
    typeName="Water",
    genComponentId="gen1",
    attributes={
        "volume": GenAttributes(type="int", value=100),
        "temperature": GenAttributes(type="int", value=20)
    }
)

# Add the GenType to the GenTypeState
gen_state.insert(water_type)

# Create component data for a Generator
gen_comp_data = CompDataI(
    typeName="Generator",
    compName="Water Generator",
    id="gen1",
    category="generator",
    inputData={"gen_count": 5},  # Generate 5 entities
    customInput={},
    connectors=[],
    Runners=RunnerFile(run="", generator="", model="", event=""),
    GenData=DataGenerator(
        config=ConfigGenerator(genFn="", config=TimeStepGenConfig()),
        types=["Water"]
    )
)

# Create component data for a Resource
res_comp_data = CompDataI(
    typeName="Resource",
    compName="Water Processor",
    id="res1",
    category="resource",
    inputData={"capacity": 1},  # Single capacity resource
    customInput={},
    connectors=[],
    Runners=RunnerFile(run="", generator="", model="", event="")
)

# Create the components
generator = Generator.create(env, gen_comp_data)
resource = Resource.create(env, res_comp_data)

# Set up workflow connections
from src.sim.sim_types import Edge

# Create an edge for the connection
edge = Edge(
    source="gen1",
    sourceHandle="Water-out",
    target="res1",
    targetHandle="Water-in",
    id="edge1"
)

# Add the edge to the workflow
workflow.add_edge(edge)

# Define a simple generator function for the Generator component
def generator_function(component):
    # Create a container with Water type
    container = component.create_default_container("Water")

    # Log the generation
    component.log_event(
        action="GENERATE",
        values={"time": component.env.now},
        PDV=container.Display()
    )

    # Set the target handler for routing
    container = component.send_genOutput_next(container, "Water")

    # Yield a timeout to simulate processing time
    yield component.env.timeout(1)

    return container

# Define a simple processing function for the Resource component
def process_water(component, input_container):
    # Log the start of processing
    component.log_event(
        action="PROCESSING",
        values={"time": component.env.now},
        PDV=input_container.Display()
    )

    # Simulate processing time
    yield component.env.timeout(2)

    # Return the processed container
    return input_container

# Monkey-patch the generator and resource components with our test functions
# Since generator_funcs and run_funcs are lists, we need to modify the CodeExec class directly
# Let's create a simple wrapper to execute our functions
generator.executor.execute_gen_function = lambda: generator_function
resource.executor.execute_run_function = lambda func_name: process_water if func_name == "Water-in" else None

def test_analytics():
    """Run the test simulation and analyze the results."""
    print("Starting test simulation...")

    # Instead of running a simulation, use the pre-generated test data with QUEUED actions
    test_data_file = "test_queue_data.csv"
    if not os.path.exists(test_data_file):
        print(f"Test data file {test_data_file} not found. Running simulation to generate data...")
        # Run the simulation
        env.run(until=20)
        # Close the logger
        logger.close()
        print(f"Simulation completed. Log file: {log_file}")
        # Use the generated log file
        csv_file = log_file
    else:
        print(f"Using pre-generated test data from {test_data_file}")
        csv_file = test_data_file

    # Create a CSV scraper to analyze the log file
    csv_scraper = CSVScraper(csv_file)

    # Get component IDs from the test data
    component_ids = csv_scraper.components_data.keys()
    print(f"Available component IDs in the data: {component_ids}")

    # Find a generator and a resource component
    generator_id = next((cid for cid in component_ids if cid.startswith("gen_")), "gen1")
    resource_id = next((cid for cid in component_ids if cid.startswith("res_")), "res1")

    print(f"Using generator component ID: {generator_id}")
    print(f"Using resource component ID: {resource_id}")

    print("Generating analytics for Generator component...")
    generator_analytics = GeneratorAnalytics(generator_id, csv_scraper)
    generator_insights = generator_analytics.generate_component_insights()

    print("Generating analytics for Resource component...")
    resource_analytics = ResourceAnalytics(resource_id, csv_scraper)
    resource_insights = resource_analytics.generate_component_insights()

    # Print some basic information about the insights
    print(f"\nGenerator insights: {len(generator_insights.dashboradData)} charts/cards")
    print(f"Resource insights: {len(resource_insights.dashboradData)} charts/cards")

    # Save the insights to JSON files with unique names based on the test data file
    output_prefix = test_data_file.replace(".csv", "_")

    generator_file = f"{output_prefix}generator_insights.json"
    resource_file = f"{output_prefix}resource_insights.json"

    with open(generator_file, "w") as f:
        json.dump(generator_insights.model_dump(), f, indent=2)

    with open(resource_file, "w") as f:
        json.dump(resource_insights.model_dump(), f, indent=2)

    print(f"\nInsights saved to {generator_file} and {resource_file}")

    # Clean up
    Component.registry.clear()

    return generator_insights, resource_insights

if __name__ == "__main__":
    test_analytics()
