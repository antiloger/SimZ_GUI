#!/usr/bin/env python3
"""
Script to fix the generator function in the dataState.json file.
"""

import json
import os

def main():
    """Fix the generator function in the dataState.json file."""
    # Load the dataState.json file
    data_state_path = os.path.join("projects", "example-3", "save", "dataState.json")
    
    try:
        with open(data_state_path, "r") as f:
            data_state = json.load(f)
        
        # Get the generator component
        generator_id = "42d72e61-314c-4bf7-b781-b3124da9ebb7"
        generator = data_state.get(generator_id)
        
        if not generator:
            print(f"Generator component with ID {generator_id} not found in dataState.json")
            return
        
        # Update the generator code
        generator_code = """import random

def generate(ctx):
    """
    Generate soda containers with random properties.
    
    Args:
        ctx: The generator component instance (self)
        
    Returns:
        A GenContainer with soda type
    """
    # Get custom input parameters if available
    time_s = ctx.get_data("time_s", 3)  # Default processing time start: 3
    time_e = ctx.get_data("time_e", 5)  # Default processing time end: 5
    error_rate = ctx.get_data("error_rate", 0.02)  # Default error rate: 2%
    
    # Create a new soda entity with random properties
    attributes = {
        "amount": 200,  # ml
        "unit": "ml",
        "ph": round(random.uniform(2.8, 4.5), 1),  # pH between 2.8 and 3.2
        "Brix": round(random.uniform(9.5, 13.5), 1)  # Brix between 9.5 and 10.5
    }
    
    # Create the container
    container = ctx.create_entity("soda", attributes)
    
    # Simulate processing time
    processing_time = random.uniform(time_s, time_e)
    yield ctx.env.timeout(processing_time)
    
    return container"""
        
        # Update the event code
        event_code = """# Event handling functions

def startup(component):
    """Initialize component variables."""
    # Store default values in KVStorage
    component.store_data("time_s", component.customInput.get("time_s", {}).get("defaultValue", 3))
    component.store_data("time_e", component.customInput.get("time_e", {}).get("defaultValue", 5))
    component.store_data("error_rate", component.customInput.get("error_rate", {}).get("defaultValue", 2) / 100.0)
    print(f"Startup method called for component {component.compId}")
    return True

def process_event(event_data):
    print("Processing event data")
    return event_data"""
        
        # Update the component
        generator["Runners"]["generator"] = generator_code
        generator["Runners"]["event"] = event_code
        
        # Save the updated dataState.json file
        with open(data_state_path, "w") as f:
            json.dump(data_state, f, indent=4)
        
        print("✅ Successfully updated the generator function and added startup method")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
