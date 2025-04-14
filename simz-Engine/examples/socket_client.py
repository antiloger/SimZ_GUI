#!/usr/bin/env python3
"""
SimZ Engine - Socket.IO Client Example
This is a simple example client that connects to the SimZ Engine Socket.IO server
"""

import socketio
import time
import argparse
import json


def main():
    """Main function for the Socket.IO client example"""
    parser = argparse.ArgumentParser(description='SimZ Engine - Socket.IO Client Example')
    parser.add_argument('--host', type=str, default='localhost',
                        help='Host address of the Socket.IO server')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port of the Socket.IO server')
    args = parser.parse_args()
    
    # Create Socket.IO client
    sio = socketio.Client()
    
    # Define event handlers
    @sio.event
    def connect():
        print("Connected to the server")
    
    @sio.event
    def disconnect():
        print("Disconnected from the server")
    
    @sio.event
    def connect_error(data):
        print(f"Connection error: {data}")
    
    # Connect to the server
    server_url = f"http://{args.host}:{args.port}"
    print(f"Connecting to {server_url}...")
    
    try:
        sio.connect(server_url)
        
        # Test project operations
        print("\n=== Testing Project Operations ===")
        
        # Create a project
        project_name = f"test_project_{int(time.time())}"
        print(f"Creating project '{project_name}'...")
        
        response = sio.call("create_project", {
            "name": project_name,
            "description": "Test project created by Socket.IO client"
        })
        print_response(response)
        
        # List projects
        print("\nListing projects...")
        response = sio.call("list_projects")
        print_response(response)
        
        # Get project details
        print(f"\nGetting project '{project_name}' details...")
        response = sio.call("get_project", {"name": project_name})
        print_response(response)
        
        # Test component operations
        print("\n=== Testing Component Operations ===")
        
        # Register a component
        component_name = "TestComponent"
        print(f"Registering component '{component_name}'...")
        
        python_code = """
class TestComponent:
    def __init__(self, config):
        self.name = config.get('name', 'TestComponent')
        
    def process(self, simulation_time, input_data):
        return {
            'result': input_data.get('value', 0) * 2,
            'time': simulation_time
        }
"""
        
        input_schema = {
            "type": "object",
            "properties": {
                "value": {"type": "number"}
            }
        }
        
        output_schema = {
            "type": "object",
            "properties": {
                "result": {"type": "number"},
                "time": {"type": "number"}
            }
        }
        
        response = sio.call("register_component", {
            "project_name": project_name,
            "component_name": component_name,
            "python_code": python_code,
            "input_schema": input_schema,
            "output_schema": output_schema
        })
        print_response(response)
        
        # List components
        print(f"\nListing components for project '{project_name}'...")
        response = sio.call("list_components", {"project_name": project_name})
        print_response(response)
        
        # Get component details
        print(f"\nGetting component '{component_name}' details...")
        response = sio.call("get_component", {
            "project_name": project_name,
            "component_name": component_name
        })
        print_response(response)
        
        # Test run operations
        print("\n=== Testing Run Operations ===")
        
        # Create a run
        print(f"Creating run for project '{project_name}'...")
        response = sio.call("create_run", {"project_name": project_name})
        print_response(response)
        
        run_id = response.get("run", {}).get("id")
        
        # List runs
        print(f"\nListing runs for project '{project_name}'...")
        response = sio.call("list_runs", {"project_name": project_name})
        print_response(response)
        
        # Get run details
        if run_id:
            print(f"\nGetting run '{run_id}' details...")
            response = sio.call("get_run", {
                "project_name": project_name,
                "run_id": run_id
            })
            print_response(response)
        
        # Disconnect from the server
        print("\nDisconnecting from the server...")
        sio.disconnect()
    
    except Exception as e:
        print(f"Error: {e}")


def print_response(response):
    """Print a formatted response"""
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main() 