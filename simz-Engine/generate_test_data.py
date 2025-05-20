#!/usr/bin/env python3
"""
Generate test data for chart testing.
"""

import csv
import json
import random
import uuid
from datetime import datetime

def generate_test_csv(filename, num_rows=100):
    """Generate a test CSV file with simulated component actions."""
    # Define component types and actions
    component_types = ["generator", "resource"]
    actions = ["IN", "OUT", "QUEUED", "GENERATE", "ENTER", "Exit"]
    
    # Create component IDs
    components = {
        "generator": [f"gen_{i}" for i in range(1, 4)],
        "resource": [f"res_{i}" for i in range(1, 6)]
    }
    
    # Create container IDs
    containers = [str(uuid.uuid4())[:8] for _ in range(10)]
    
    # Prepare CSV data
    fieldnames = ["time", "component_id", "component_type", "action", "values", "PDV", "addition"]
    rows = []
    
    # Generate data with realistic processing patterns
    current_time = 0
    container_locations = {}  # Track where each container is
    
    for _ in range(num_rows):
        # Increment time
        current_time += random.randint(1, 3)
        
        # Select a component
        comp_type = random.choice(component_types)
        comp_id = random.choice(components[comp_type])
        
        # Determine action based on component type
        if comp_type == "generator":
            action = "GENERATE"
            container_id = random.choice(containers)
            container_locations[container_id] = comp_id
            
            values = {
                "out_time": current_time + random.randint(1, 5)
            }
            
            pdv = {
                "containerId": container_id,
                "types": {
                    "product": {
                        "typeName": "product",
                        "genComponentId": comp_id,
                        "attributes": {
                            "volume": {"type": "int", "value": random.randint(10, 100)},
                            "quality": {"type": "int", "value": random.randint(1, 10)}
                        }
                    }
                }
            }
        else:  # resource
            # Determine if this is an IN or OUT action
            if comp_id in container_locations.values():
                # This component has a container, so it can do an OUT action
                container_id = next(cid for cid, loc in container_locations.items() if loc == comp_id)
                action = "OUT"
                
                # Find a new location for the container
                new_location = random.choice(components["resource"])
                container_locations[container_id] = new_location
                
                values = {
                    "input_count": random.randint(1, 5),
                    "out_time": current_time
                }
            else:
                # No container in this component, so do an IN action
                available_containers = [cid for cid in containers if cid in container_locations]
                if not available_containers:
                    continue  # Skip if no containers available
                    
                container_id = random.choice(available_containers)
                action = "IN"
                container_locations[container_id] = comp_id
                
                values = {
                    "input_count": random.randint(1, 5),
                    "in_time": current_time
                }
            
            pdv = {
                "containerId": container_id,
                "types": {
                    "product": {
                        "typeName": "product",
                        "attributes": {
                            "volume": {"type": "int", "value": random.randint(10, 100)},
                            "quality": {"type": "int", "value": random.randint(1, 10)}
                        }
                    }
                }
            }
        
        # Create the row
        row = {
            "time": current_time,
            "component_id": comp_id,
            "component_type": comp_type,
            "action": action,
            "values": json.dumps(values),
            "PDV": json.dumps(pdv),
            "addition": ""
        }
        
        rows.append(row)
    
    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Generated {len(rows)} rows of test data in {filename}")
    return filename

if __name__ == "__main__":
    # Generate test data
    test_file = generate_test_csv("test_data.csv", num_rows=200)
    print(f"Test data saved to {test_file}")
