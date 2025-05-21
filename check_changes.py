#!/usr/bin/env python3
"""
Script to check if our changes to the dataState.json file were applied.
"""

import json
import os

def main():
    """Check if our changes to the dataState.json file were applied."""
    # Load the dataState.json file
    data_state_path = os.path.join("..", "projects", "example-3", "save", "dataState.json")
    
    try:
        with open(data_state_path, "r") as f:
            data_state = json.load(f)
        
        # Get the generator component
        generator_id = "42d72e61-314c-4bf7-b781-b3124da9ebb7"
        generator = data_state.get(generator_id)
        
        if not generator:
            print(f"Generator component with ID {generator_id} not found in dataState.json")
            return
        
        # Check if the generator code was updated
        generator_code = generator.get("Runners", {}).get("generator", "")
        if "ctx.get_data" in generator_code:
            print("✅ Generator code was updated to use ctx.get_data() instead of ctx.var.get()")
        else:
            print("❌ Generator code was NOT updated to use ctx.get_data()")
        
        # Check if the startup method was added to the event code
        event_code = generator.get("Runners", {}).get("event", "")
        if "def startup" in event_code:
            print("✅ Startup method was added to the event code")
        else:
            print("❌ Startup method was NOT added to the event code")
        
        print("\nGenerator code:")
        print(generator_code[:200] + "..." if len(generator_code) > 200 else generator_code)
        
        print("\nEvent code:")
        print(event_code[:200] + "..." if len(event_code) > 200 else event_code)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
