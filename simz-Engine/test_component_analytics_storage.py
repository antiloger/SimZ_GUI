#!/usr/bin/env python3
"""
Test script for component-specific analytics storage.

This script tests the component-specific analytics storage system by:
1. Creating a simple simulation with Generator and Resource components
2. Running the simulation to generate log data
3. Using the analytics system to generate insights
4. Saving the insights to separate JSON files
5. Verifying that the files are correctly created and contain the expected data
"""

import os
import simpy
from pathlib import Path
import json
import shutil

from src.sim.comp import Component, Generator, Resource
from src.sim.sim_types import CompDataI, RunnerFile, DataGenerator, ConfigGenerator, TimeStepGenConfig
from src.sim.kvstorage import KVStorage
from src.sim.graph import WorkflowGraph
from src.sim.db import CsvLogger
from src.sim.sim_types import GenTypeState, GenTypes, GenAttributes, GenContainer
from src.sim.csvpaser import CSVScraper
from src.sim.analytics import AnalyticsFactory, GeneratorAnalytics, ResourceAnalytics
from src.sim.build import SimulationBuilder

# Test directory for output
TEST_DIR = Path("test_analytics_output")
if TEST_DIR.exists():
    shutil.rmtree(TEST_DIR)
TEST_DIR.mkdir(parents=True, exist_ok=True)

# Create a simple test environment
env = simpy.Environment()

# Create a workflow graph
workflow = WorkflowGraph()

# Create a logger with required fieldnames
log_file = TEST_DIR / "test_analytics.csv"
logger = CsvLogger(
    str(log_file),
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

def test_analytics_storage():
    """Run the test simulation and analyze the results."""
    print("Starting test simulation...")

    # Run the simulation
    env.run(until=20)

    # Close the logger
    logger.close()

    print(f"Simulation completed. Log file: {log_file}")

    # Create a CSV scraper to analyze the log file
    csv_scraper = CSVScraper(str(log_file))

    # Instead of using SimulationBuilder, we'll create our own save methods
    # to avoid the need for project structure
    def save_component_analytics(component_insights):
        """Save component analytics to separate files."""
        # Create a components directory if it doesn't exist
        components_dir = TEST_DIR / "components"
        if not components_dir.exists():
            components_dir.mkdir(parents=True, exist_ok=True)

        # Save each component's analytics to a separate file
        for insight in component_insights:
            try:
                file_path = components_dir / f"component_analytics_{insight.id}.json"
                with open(file_path, "w") as f:
                    # Use model_dump instead of dict (which is deprecated)
                    try:
                        json.dump(insight.model_dump(), f, indent=4)
                    except AttributeError:
                        # Fallback for older versions that might not have model_dump
                        json.dump(insight.dict(), f, indent=4)
                print(f"Component analytics for {insight.id} saved to {file_path}")
            except Exception as e:
                print(f"Failed to save component analytics for {insight.id}: {e}")

    # Generate component insights
    print("Generating component insights...")

    # Create analytics for each component
    component_insights = []

    # Generate insights for generator
    print("Generating insights for generator...")
    generator_analytics = GeneratorAnalytics("gen1", csv_scraper)
    generator_insights = generator_analytics.generate_component_insights()
    component_insights.append(generator_insights)

    # Generate insights for resource
    print("Generating insights for resource...")
    resource_analytics = ResourceAnalytics("res1", csv_scraper)
    resource_insights = resource_analytics.generate_component_insights()
    component_insights.append(resource_insights)

    # Save component insights to separate files
    print("Saving component insights...")
    save_component_analytics(component_insights)

    # Verify that the files were created
    components_dir = TEST_DIR / "components"
    print(f"Components directory: {components_dir}")
    print(f"Directory exists: {components_dir.exists()}")

    if components_dir.exists():
        component_files = list(components_dir.glob("component_analytics_*.json"))
        print(f"Component files: {[f.name for f in component_files]}")

        # Verify that we have files for both components
        gen_file = components_dir / "component_analytics_gen1.json"
        res_file = components_dir / "component_analytics_res1.json"

        if gen_file.exists():
            print(f"Generator analytics file exists: {gen_file}")
            with open(gen_file, "r") as f:
                gen_data = json.load(f)
            print(f"Generator analytics data contains {len(gen_data.get('dashboradData', []))} charts/cards")
        else:
            print(f"Generator analytics file does not exist: {gen_file}")

        if res_file.exists():
            print(f"Resource analytics file exists: {res_file}")
            with open(res_file, "r") as f:
                res_data = json.load(f)
            print(f"Resource analytics data contains {len(res_data.get('dashboradData', []))} charts/cards")
        else:
            print(f"Resource analytics file does not exist: {res_file}")
    else:
        print("Components directory does not exist")

    # Clean up
    Component.registry.clear()

    return component_insights

if __name__ == "__main__":
    test_analytics_storage()
