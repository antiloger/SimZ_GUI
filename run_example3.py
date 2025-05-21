#!/usr/bin/env python3
"""
Script to run the example-3 project simulation.
"""

import os
import sys
import simpy
from src.sim.comp import Component
from src.sim.db import CsvLogger
from src.sim.graph import WorkflowGraph
from src.sim.sim_types import GenTypeState
from src.sim.sim_runner import SimRunner

def main():
    """Run the example-3 project simulation."""
    # Set up the simulation environment
    env = simpy.Environment()
    
    # Set up the workflow graph
    workflow = WorkflowGraph()
    
    # Set up the logger
    log_dir = os.path.join("projects", "example-3", "Run", "test_run")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "test_run.csv")
    logger = CsvLogger(log_file)
    
    # Set up the GenTypeState
    gen_state = GenTypeState()
    gen_state.load_from_file(os.path.join("projects", "example-3", "save", "genState.json"))
    
    # Set up Component class resources
    Component.set_workflow(workflow)
    Component.set_logger(logger)
    Component.set_Gen_ref(gen_state)
    
    # Create a SimRunner instance
    runner = SimRunner(
        env=env,
        workflow=workflow,
        logger=logger,
        gen_state=gen_state,
        project_path=os.path.join("projects", "example-3"),
        run_name="test_run"
    )
    
    # Load the simulation from the project
    runner.load_simulation()
    
    # Run the simulation
    print("Starting simulation...")
    runner.run_simulation()
    print(f"Simulation completed. Log file: {log_file}")
    
    # Close the logger
    logger.close()

if __name__ == "__main__":
    main()
