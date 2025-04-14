import os
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


class FileManager:
    """
    FileManager handles the creation, manipulation, and management of project files and folders
    for the discrete event simulation builder.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the FileManager with a base directory.
        
        Args:
            base_dir: The base directory where all projects will be stored.
                     If None, defaults to the current directory.
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "projects"
        self.base_dir.mkdir(exist_ok=True, parents=True)
    
    def create_project(self, project_name: str) -> Path:
        """
        Create a new project with the required folder structure.
        
        Args:
            project_name: Name of the project to create
            
        Returns:
            Path to the created project
            
        Raises:
            ValueError: If the project already exists
        """
        project_path = self.base_dir / project_name
        
        if project_path.exists():
            raise ValueError(f"Project '{project_name}' already exists.")
        
        # Create project directory
        project_path.mkdir(parents=True)
        
        # Create Run directory
        (project_path / "Run").mkdir()
        
        # Create RegisterComponent directory
        (project_path / "RegisterComponent").mkdir()
        
        # Create and initialize config.json
        config = {
            "project_name": project_name,
            "created_at": datetime.now().isoformat(),
            "description": "",
            "version": "1.0.0",
            "components": [],
            "runs": []
        }
        
        with open(project_path / "config.json", "w") as f:
            json.dump(config, f, indent=4)
        
        return project_path
    
    def list_projects(self) -> List[str]:
        """
        List all available projects.
        
        Returns:
            List of project names
        """
        return [p.name for p in self.base_dir.iterdir() 
                if p.is_dir() and (p / "config.json").exists()]
    
    def project_exists(self, project_name: str) -> bool:
        """
        Check if a project exists.
        
        Args:
            project_name: Name of the project to check
            
        Returns:
            True if the project exists, False otherwise
        """
        project_path = self.base_dir / project_name
        return project_path.exists() and (project_path / "config.json").exists()
    
    def get_project_path(self, project_name: str) -> Path:
        """
        Get the path to a project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Path to the project
            
        Raises:
            ValueError: If the project doesn't exist
        """
        if not self.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")
        
        return self.base_dir / project_name
    
    def delete_project(self, project_name: str) -> None:
        """
        Delete a project.
        
        Args:
            project_name: Name of the project to delete
            
        Raises:
            ValueError: If the project doesn't exist
        """
        project_path = self.get_project_path(project_name)
        shutil.rmtree(project_path)
    
    def get_project_config(self, project_name: str) -> Dict:
        """
        Get the configuration for a project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Project configuration as a dictionary
            
        Raises:
            ValueError: If the project doesn't exist
        """
        project_path = self.get_project_path(project_name)
        
        with open(project_path / "config.json", "r") as f:
            return json.load(f)
    
    def update_project_config(self, project_name: str, config: Dict) -> None:
        """
        Update the configuration for a project.
        
        Args:
            project_name: Name of the project
            config: New configuration dictionary
            
        Raises:
            ValueError: If the project doesn't exist
        """
        project_path = self.get_project_path(project_name)
        
        with open(project_path / "config.json", "w") as f:
            json.dump(config, f, indent=4)
    
    def create_run(self, project_name: str, run_name: Optional[str] = None) -> str:
        """
        Create a new simulation run.
        
        Args:
            project_name: Name of the project
            run_name: Optional name for the run. If None, a UUID will be generated.
            
        Returns:
            ID of the created run
            
        Raises:
            ValueError: If the project doesn't exist
        """
        project_path = self.get_project_path(project_name)
        run_id = run_name or f"run_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        run_path = project_path / "Run" / run_id
        run_path.mkdir(parents=True)
        
        # Create state directory
        state_path = run_path / "state"
        state_path.mkdir()
        
        # Create output directory
        output_path = run_path / "output"
        output_path.mkdir()
        
        # Update project config
        config = self.get_project_config(project_name)
        config["runs"].append({
            "id": run_id,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        })
        self.update_project_config(project_name, config)
        
        return run_id
    
    def list_runs(self, project_name: str) -> List[str]:
        """
        List all simulation runs for a project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            List of run IDs
            
        Raises:
            ValueError: If the project doesn't exist
        """
        project_path = self.get_project_path(project_name)
        run_path = project_path / "Run"
        
        return [p.name for p in run_path.iterdir() if p.is_dir()]
    
    def delete_run(self, project_name: str, run_id: str) -> None:
        """
        Delete a simulation run.
        
        Args:
            project_name: Name of the project
            run_id: ID of the run to delete
            
        Raises:
            ValueError: If the project or run doesn't exist
        """
        project_path = self.get_project_path(project_name)
        run_path = project_path / "Run" / run_id
        
        if not run_path.exists():
            raise ValueError(f"Run '{run_id}' does not exist in project '{project_name}'.")
        
        shutil.rmtree(run_path)
        
        # Update project config
        config = self.get_project_config(project_name)
        config["runs"] = [r for r in config["runs"] if r["id"] != run_id]
        self.update_project_config(project_name, config)
    
    def save_state_data(self, project_name: str, run_id: str, state_name: str, data: Dict) -> Path:
        """
        Save simulation state data as JSON.
        
        Args:
            project_name: Name of the project
            run_id: ID of the run
            state_name: Name of the state file (without extension)
            data: Data to save
            
        Returns:
            Path to the saved state file
            
        Raises:
            ValueError: If the project or run doesn't exist
        """
        project_path = self.get_project_path(project_name)
        state_path = project_path / "Run" / run_id / "state"
        
        if not state_path.exists():
            raise ValueError(f"State directory for run '{run_id}' does not exist.")
        
        file_path = state_path / f"{state_name}.json"
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        
        return file_path
    
    def get_state_data(self, project_name: str, run_id: str, state_name: str) -> Dict:
        """
        Get simulation state data.
        
        Args:
            project_name: Name of the project
            run_id: ID of the run
            state_name: Name of the state file (without extension)
            
        Returns:
            State data as a dictionary
            
        Raises:
            ValueError: If the project, run, or state file doesn't exist
        """
        project_path = self.get_project_path(project_name)
        file_path = project_path / "Run" / run_id / "state" / f"{state_name}.json"
        
        if not file_path.exists():
            raise ValueError(f"State file '{state_name}' does not exist for run '{run_id}'.")
        
        with open(file_path, "r") as f:
            return json.load(f)
    
    def save_output_data(self, project_name: str, run_id: str, output_name: str, data: Dict) -> Path:
        """
        Save simulation output data as JSON.
        
        Args:
            project_name: Name of the project
            run_id: ID of the run
            output_name: Name of the output file (without extension)
            data: Data to save
            
        Returns:
            Path to the saved output file
            
        Raises:
            ValueError: If the project or run doesn't exist
        """
        project_path = self.get_project_path(project_name)
        output_path = project_path / "Run" / run_id / "output"
        
        if not output_path.exists():
            raise ValueError(f"Output directory for run '{run_id}' does not exist.")
        
        file_path = output_path / f"{output_name}.json"
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        
        return file_path
    
    def get_output_data(self, project_name: str, run_id: str, output_name: str) -> Dict:
        """
        Get simulation output data.
        
        Args:
            project_name: Name of the project
            run_id: ID of the run
            output_name: Name of the output file (without extension)
            
        Returns:
            Output data as a dictionary
            
        Raises:
            ValueError: If the project, run, or output file doesn't exist
        """
        project_path = self.get_project_path(project_name)
        file_path = project_path / "Run" / run_id / "output" / f"{output_name}.json"
        
        if not file_path.exists():
            raise ValueError(f"Output file '{output_name}' does not exist for run '{run_id}'.")
        
        with open(file_path, "r") as f:
            return json.load(f)
    
    def register_component(self, project_name: str, component_name: str, 
                          python_code: str, input_schema: Dict, output_schema: Dict) -> Path:
        """
        Register a simulation component.
        
        Args:
            project_name: Name of the project
            component_name: Name of the component
            python_code: Python code defining the component
            input_schema: Input JSON schema
            output_schema: Output JSON schema
            
        Returns:
            Path to the component directory
            
        Raises:
            ValueError: If the project doesn't exist or component already exists
        """
        project_path = self.get_project_path(project_name)
        component_path = project_path / "RegisterComponent" / component_name
        
        if component_path.exists():
            raise ValueError(f"Component '{component_name}' already exists in project '{project_name}'.")
        
        component_path.mkdir(parents=True)
        
        # Save Python file
        with open(component_path / f"{component_name}.py", "w") as f:
            f.write(python_code)
        
        # Save input schema
        with open(component_path / "input.json", "w") as f:
            json.dump(input_schema, f, indent=4)
        
        # Save output schema
        with open(component_path / "output.json", "w") as f:
            json.dump(output_schema, f, indent=4)
        
        # Update project config
        config = self.get_project_config(project_name)
        config["components"].append({
            "name": component_name,
            "created_at": datetime.now().isoformat()
        })
        self.update_project_config(project_name, config)
        
        return component_path
    
    def list_components(self, project_name: str) -> List[str]:
        """
        List all registered components for a project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            List of component names
            
        Raises:
            ValueError: If the project doesn't exist
        """
        project_path = self.get_project_path(project_name)
        component_path = project_path / "RegisterComponent"
        
        return [p.name for p in component_path.iterdir() if p.is_dir()]
    
    def get_component(self, project_name: str, component_name: str) -> Dict[str, Any]:
        """
        Get all information about a component.
        
        Args:
            project_name: Name of the project
            component_name: Name of the component
            
        Returns:
            Dictionary with component information
            
        Raises:
            ValueError: If the project or component doesn't exist
        """
        project_path = self.get_project_path(project_name)
        component_path = project_path / "RegisterComponent" / component_name
        
        if not component_path.exists():
            raise ValueError(f"Component '{component_name}' does not exist in project '{project_name}'.")
        
        # Read Python file
        with open(component_path / f"{component_name}.py", "r") as f:
            python_code = f.read()
        
        # Read input schema
        with open(component_path / "input.json", "r") as f:
            input_schema = json.load(f)
        
        # Read output schema
        with open(component_path / "output.json", "r") as f:
            output_schema = json.load(f)
        
        return {
            "name": component_name,
            "python_code": python_code,
            "input_schema": input_schema,
            "output_schema": output_schema
        }
    
    def delete_component(self, project_name: str, component_name: str) -> None:
        """
        Delete a component.
        
        Args:
            project_name: Name of the project
            component_name: Name of the component
            
        Raises:
            ValueError: If the project or component doesn't exist
        """
        project_path = self.get_project_path(project_name)
        component_path = project_path / "RegisterComponent" / component_name
        
        if not component_path.exists():
            raise ValueError(f"Component '{component_name}' does not exist in project '{project_name}'.")
        
        shutil.rmtree(component_path)
        
        # Update project config
        config = self.get_project_config(project_name)
        config["components"] = [c for c in config["components"] if c["name"] != component_name]
        self.update_project_config(project_name, config) 