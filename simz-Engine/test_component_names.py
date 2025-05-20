#!/usr/bin/env python3
"""
Test script for component ID-name mappings.

This script tests:
1. Creating a simple simulation with a few components
2. Saving component ID-name mappings to a JSON file
3. Verifying that the file is correctly created and contains the expected data
"""

import os
import json
from pathlib import Path
import shutil
import simpy

from src.sim.comp import Component, Generator, Resource
from src.sim.sim_types import CompDataI, RunnerFile, DataGenerator, ConfigGenerator, TimeStepGenConfig
from src.sim.kvstorage import KVStorage
from src.sim.graph import WorkflowGraph
from src.sim.db import CsvLogger
from src.sim.sim_types import GenTypeState, GenTypes, GenAttributes, GenContainer
from src.sim.build import SimulationBuilder

# Test directory for output
TEST_DIR = Path("test_component_names_output")
if TEST_DIR.exists():
    shutil.rmtree(TEST_DIR)
TEST_DIR.mkdir(parents=True, exist_ok=True)

def test_component_names():
    """Test saving component ID-name mappings."""
    print("Testing component ID-name mappings...")

    # Create a simple environment
    env = simpy.Environment()

    # Create a workflow graph
    workflow = WorkflowGraph()

    # Create a logger
    log_file = TEST_DIR / "test_component_names.csv"
    logger = CsvLogger(
        str(log_file),
        fieldnames=["time", "component_id", "component_type", "action", "values", "PDV", "addition"]
    )

    # Create a GenTypeState
    gen_state = GenTypeState(root={})

    # Set up the component class variables
    Component.set_Gen_ref(gen_state)
    Component.set_workflow(workflow)
    Component.set_logger(logger)

    # Create component data for a Generator
    gen_comp_data = CompDataI(
        typeName="Generator",
        compName="Water Generator",
        id="gen1",
        category="generator",
        inputData={"gen_count": 5},
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
        inputData={"capacity": 1},
        customInput={},
        connectors=[],
        Runners=RunnerFile(run="", generator="", model="", event="")
    )

    # Create another component data for a Resource
    res2_comp_data = CompDataI(
        typeName="Resource",
        compName="Secondary Processor",
        id="res2",
        category="resource",
        inputData={"capacity": 2},
        customInput={},
        connectors=[],
        Runners=RunnerFile(run="", generator="", model="", event="")
    )

    # Create the components
    generator = Generator.create(env, gen_comp_data)
    resource1 = Resource.create(env, res_comp_data)
    resource2 = Resource.create(env, res2_comp_data)

    # Create a custom SimulationBuilder instance that doesn't try to load files
    class TestSimulationBuilder(SimulationBuilder):
        def __init__(self, runName, components):
            self.runName = runName
            self.components = components
            self.genState = gen_state
            self.workflow = workflow
            self.logger = logger
            self.socketLog = print

        def load(self):
            # Skip loading files that don't exist
            pass

    # Create our test builder
    sim_builder = TestSimulationBuilder(
        runName="test_run",
        components={
            "gen1": generator,
            "res1": resource1,
            "res2": resource2
        }
    )

    # Components are already set in the constructor

    # Save component names
    sim_builder.save_component_names(TEST_DIR)

    # Verify that the file was created
    component_names_file = TEST_DIR / "component_names.json"
    print(f"Component names file: {component_names_file}")
    print(f"File exists: {component_names_file.exists()}")

    if component_names_file.exists():
        # Read the file
        with open(component_names_file, "r") as f:
            component_names = json.load(f)

        # Verify the content
        print(f"Component names: {component_names}")

        # Check that all components are included
        assert "gen1" in component_names
        assert "res1" in component_names
        assert "res2" in component_names

        # Check that the names are correct
        assert component_names["gen1"] == "Water Generator"
        assert component_names["res1"] == "Water Processor"
        assert component_names["res2"] == "Secondary Processor"

        print("Component names test passed!")
    else:
        print("Component names file was not created!")

    # Clean up
    Component.registry.clear()

    return component_names_file

if __name__ == "__main__":
    test_component_names()
