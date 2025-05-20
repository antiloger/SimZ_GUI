#!/usr/bin/env python3
"""
Test script to verify the component ID fix.

This script tests:
1. Creating a ComponentOutput with an integer ID (which should fail)
2. Creating a ComponentOutput with a string ID (which should succeed)
3. Converting an integer ID to a string before creating a ComponentOutput
"""

from src.sim.sim_types import ComponentOutput

def test_component_output_creation():
    """Test creating ComponentOutput with different ID types."""
    print("Testing ComponentOutput creation...")
    
    # Test with integer ID (should fail)
    try:
        component_output = ComponentOutput(
            id=12,
            name="Test Component",
            type="test"
        )
        print("ERROR: Created ComponentOutput with integer ID (should have failed)")
    except Exception as e:
        print(f"SUCCESS: Failed to create ComponentOutput with integer ID: {e}")
    
    # Test with string ID (should succeed)
    try:
        component_output = ComponentOutput(
            id="12",
            name="Test Component",
            type="test"
        )
        print("SUCCESS: Created ComponentOutput with string ID")
    except Exception as e:
        print(f"ERROR: Failed to create ComponentOutput with string ID: {e}")
    
    # Test with integer ID converted to string (should succeed)
    try:
        component_id = 12
        component_output = ComponentOutput(
            id=str(component_id),
            name="Test Component",
            type="test"
        )
        print("SUCCESS: Created ComponentOutput with integer ID converted to string")
    except Exception as e:
        print(f"ERROR: Failed to create ComponentOutput with integer ID converted to string: {e}")

if __name__ == "__main__":
    test_component_output_creation()
