#!/usr/bin/env python3
"""
SimZ Engine - Discrete Event Simulation Builder
This is a demonstration of the ProjectManager API
"""

import os
import json
from pathlib import Path
import argparse

from src.core.project_manager import ProjectManager


def demo_create_project(project_manager, project_name):
    """Create a new project and display its info"""
    try:
        project_info = project_manager.create_project(
            project_name, 
            "A demonstration simulation project"
        )
        print(f"Created project: {json.dumps(project_info, indent=2)}")
        return True
    except ValueError as e:
        print(f"Error creating project: {e}")
        return False


def demo_create_component(project_manager, project_name):
    """Create a simulation component and register it with the project"""
    # Example component code
    python_code = """
class QueueProcessor:
    \"\"\"
    A component that processes entities in a queue.
    \"\"\"
    
    def __init__(self, config):
        self.name = config.get('name', 'QueueProcessor')
        self.processing_time = config.get('processing_time', 1.0)
        self.input_queue = []
        self.entity_count = 0
    
    def process(self, simulation_time, input_data):
        # Add new entities to the queue
        if 'new_entities' in input_data:
            self.input_queue.extend(input_data['new_entities'])
        
        # Process entities in the queue
        processed_entities = []
        while self.input_queue and len(processed_entities) < input_data.get('max_process', 1):
            entity = self.input_queue.pop(0)
            entity['processed_at'] = simulation_time
            entity['processing_time'] = self.processing_time
            processed_entities.append(entity)
            self.entity_count += 1
        
        return {
            'processed_entities': processed_entities,
            'queue_length': len(self.input_queue),
            'entity_count': self.entity_count
        }
"""

    # Input schema for the component
    input_schema = {
        "type": "object",
        "properties": {
            "new_entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "arrival_time": {"type": "number"}
                    },
                    "required": ["id", "arrival_time"]
                }
            },
            "max_process": {"type": "integer", "minimum": 1}
        }
    }

    # Output schema for the component
    output_schema = {
        "type": "object",
        "properties": {
            "processed_entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "arrival_time": {"type": "number"},
                        "processed_at": {"type": "number"},
                        "processing_time": {"type": "number"}
                    }
                }
            },
            "queue_length": {"type": "integer"},
            "entity_count": {"type": "integer"}
        },
        "required": ["processed_entities", "queue_length", "entity_count"]
    }

    try:
        component_info = project_manager.register_component(
            project_name, 
            "QueueProcessor", 
            python_code, 
            input_schema, 
            output_schema
        )
        print(f"Created component: {json.dumps(component_info, indent=2)}")
        return True
    except ValueError as e:
        print(f"Error creating component: {e}")
        return False


def demo_create_run(project_manager, project_name):
    """Create a simulation run and add some test data"""
    try:
        run_info = project_manager.create_run(project_name)
        print(f"Created simulation run: {json.dumps(run_info, indent=2)}")
        
        # Save some test state data
        state_data = {
            "simulation_time": 0.0,
            "entities": [],
            "events": [],
            "random_seed": 12345
        }
        
        state_info = project_manager.save_simulation_state(
            project_name, 
            run_info["id"], 
            "initial_state", 
            state_data
        )
        print(f"Saved initial state: {json.dumps(state_info, indent=2)}")
        
        # Connect to the database and add some test data
        conn = project_manager.get_db_connection(project_name, run_info["id"])
        
        # Add test entity
        project_manager.db_manager.add_entity(
            conn, 
            "entity-001", 
            "customer", 
            "Customer 1", 
            {"arrival_time": 1.0, "service_time": 5.0}
        )
        
        # Add test event
        project_manager.db_manager.add_event(
            conn, 
            "event-001", 
            1.0, 
            "entity-001", 
            "arrival", 
            {"queue": "service_queue"}
        )
        
        # Create a custom table
        project_manager.db_manager.create_custom_table(
            conn,
            "queue_stats",
            [
                {"name": "time", "type": "DOUBLE"},
                {"name": "queue_name", "type": "VARCHAR"},
                {"name": "queue_length", "type": "INTEGER"},
                {"name": "waiting_time_avg", "type": "DOUBLE"}
            ]
        )
        
        # Add test data to the custom table
        project_manager.db_manager.insert_data(
            conn,
            "queue_stats",
            {
                "time": 1.0,
                "queue_name": "service_queue",
                "queue_length": 1,
                "waiting_time_avg": 0.0
            }
        )
        
        # Query the data
        query_result = project_manager.db_manager.query_data(
            conn,
            "SELECT * FROM queue_stats"
        )
        print(f"Database query result: {json.dumps(query_result, indent=2)}")
        
        # Get entities
        entities = project_manager.db_manager.query_data(
            conn,
            "SELECT * FROM simulation_entities"
        )
        print(f"Entities: {json.dumps(entities, indent=2)}")
        
        # Get events
        events = project_manager.db_manager.get_events(conn)
        print(f"Events: {json.dumps(events, indent=2)}")
        
        conn.close()
        
        return run_info["id"]
    except Exception as e:
        print(f"Error creating run: {e}")
        return None


def demo_list_projects(project_manager):
    """List all projects and their basic info"""
    try:
        projects = project_manager.list_projects()
        print(f"Projects: {json.dumps(projects, indent=2)}")
        return True
    except Exception as e:
        print(f"Error listing projects: {e}")
        return False


def demo_get_project_details(project_manager, project_name):
    """Get detailed information about a project"""
    try:
        project = project_manager.get_project(project_name)
        print(f"Project details: {json.dumps(project, indent=2)}")
        
        # List components
        components = project_manager.list_components(project_name)
        print(f"Components: {json.dumps(components, indent=2)}")
        
        # List runs
        runs = project_manager.list_runs(project_name)
        print(f"Runs: {json.dumps(runs, indent=2)}")
        
        return True
    except ValueError as e:
        print(f"Error getting project details: {e}")
        return False


def main():
    """Main function for the demo"""
    parser = argparse.ArgumentParser(description='SimZ Engine - Project Manager Demo')
    parser.add_argument('--project-dir', type=str, default='./projects',
                        help='Directory where projects are stored')
    parser.add_argument('--project-name', type=str, default='demo_project',
                        help='Name of the demo project to create')
    args = parser.parse_args()
    
    # Create ProjectManager
    project_manager = ProjectManager(args.project_dir)
    print(f"Project manager initialized with base directory: {args.project_dir}")
    
    # Run demos
    print("\n=== Creating Project ===")
    demo_create_project(project_manager, args.project_name)
    
    print("\n=== Creating Component ===")
    demo_create_component(project_manager, args.project_name)
    
    print("\n=== Creating Simulation Run ===")
    run_id = demo_create_run(project_manager, args.project_name)
    
    print("\n=== Listing Projects ===")
    demo_list_projects(project_manager)
    
    print("\n=== Getting Project Details ===")
    demo_get_project_details(project_manager, args.project_name)
    
    if run_id:
        print(f"\n=== Run created successfully: {run_id} ===")
        print(f"You can find the run data in: {args.project_dir}/{args.project_name}/Run/{run_id}")
    
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    main()
