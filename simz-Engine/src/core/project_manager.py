import os
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from src.models.ts_sim import CompRegDataI

from src.core.file_manager import FileManager
from src.core.db_manager import DBManager


class ProjectManager:
    """
    ProjectManager integrates FileManager and DBManager to provide a unified interface
    for managing simulation projects.
    """

    def __init__(self, comp_reg_dir: str, base_dir: str):
        """
        Initialize the ProjectManager with optional base directory.

        Args:
            base_dir: Optional base directory for projects.
                     If None, uses the default from FileManager.
        """
        self.file_manager = FileManager(comp_reg_dir=comp_reg_dir, base_dir=base_dir)
        self.db_manager = DBManager(self.file_manager)

    def create_project(
        self, project_name: str, description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new project with the required structure.

        Args:
            project_name: Name of the project
            description: Optional description of the project

        Returns:
            Project information dictionary

        Raises:
            ValueError: If the project already exists
        """
        # Create project directories and files
        project_path = self.file_manager.create_project(project_name)

        # Update project config with description
        config = self.file_manager.get_project_config(project_name)
        config["description"] = description
        self.file_manager.update_project_config(project_name, config)

        return {
            "name": project_name,
            "description": description,
            "path": str(project_path),
            "created_at": config["created_at"],
        }

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all available projects with their information.

        Returns:
            List of project information dictionaries
        """
        project_names = self.file_manager.list_projects()
        projects = []

        for name in project_names:
            try:
                config = self.file_manager.get_project_config(name)
                projects.append(
                    {
                        "name": name,
                        "description": config.get("description", ""),
                        "created_at": config.get("created_at", ""),
                        "runs_count": len(config.get("runs", [])),
                    }
                )
            except Exception as e:
                # Skip projects with errors
                print(f"Error loading project '{name}': {str(e)}")

        return projects

    def get_project(self, project_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a project.

        Args:
            project_name: Name of the project

        Returns:
            Project information dictionary

        Raises:
            ValueError: If the project doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        config = self.file_manager.get_project_config(project_name)
        project_path = self.file_manager.get_project_path(project_name)

        # Get component and run information
        runs = self.file_manager.list_runs(project_name)

        return {
            "name": project_name,
            "description": config.get("description", ""),
            "created_at": config.get("created_at", ""),
            "version": config.get("version", "1.0.0"),
            "path": str(project_path),
            "runs": runs,
        }

    def update_project(
        self,
        project_name: str,
        description: Optional[str] = None,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update project information.

        Args:
            project_name: Name of the project
            description: Optional new description
            version: Optional new version

        Returns:
            Updated project information

        Raises:
            ValueError: If the project doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        config = self.file_manager.get_project_config(project_name)

        if description is not None:
            config["description"] = description

        if version is not None:
            config["version"] = version

        self.file_manager.update_project_config(project_name, config)

        return self.get_project(project_name)

    def delete_project(self, project_name: str) -> None:
        """
        Delete a project and all its contents.

        Args:
            project_name: Name of the project

        Raises:
            ValueError: If the project doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        self.file_manager.delete_project(project_name)

    def add_run_to_project(self, project_name: str, run_id: str) -> Dict[str, Any]:
        """
        Add an existing run to a project.

        Args:
            project_name: Name of the project
            run_id: ID of the run
            run_name: Optional name for the run

        Returns:
            Run information dictionary

        Raises:
            ValueError: If the project or run doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        if not self.file_manager.run_exists(project_name, run_id):
            raise ValueError(
                f"Run '{run_id}' does not exist in project '{project_name}'."
            )

        # Add run to project config
        config = self.file_manager.get_project_config(project_name)
        config["runs"].append({"id": run_id, "name": run_id})
        self.file_manager.update_project_config(project_name, config)

        return {
            "id": run_id,
            "project_name": project_name,
            "created_at": config["created_at"],
            "status": "added",
        }

    def create_run(
        self, project_name: str, run_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new simulation run with database.

        Args:
            project_name: Name of the project
            run_name: Optional name for the run

        Returns:
            Run information dictionary

        Raises:
            ValueError: If the project doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        # Create run directories
        run_id = self.file_manager.create_run(project_name, run_name)

        # Create run database
        db_path = self.db_manager.create_run_db(project_name, run_id)

        # Get run information
        config = self.file_manager.get_project_config(project_name)
        run_info = next((r for r in config.get("runs", []) if r["id"] == run_id), {})

        return {
            "id": run_id,
            "project_name": project_name,
            "created_at": run_info.get("created_at", ""),
            "status": run_info.get("status", "created"),
            "db_path": str(db_path),
        }

    def list_runs(self, project_name: str) -> List[Dict[str, Any]]:
        """
        List all simulation runs for a project with their information.

        Args:
            project_name: Name of the project

        Returns:
            List of run information dictionaries

        Raises:
            ValueError: If the project doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        config = self.file_manager.get_project_config(project_name)
        return config.get("runs", [])

    def get_run(self, project_name: str, run_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a run.

        Args:
            project_name: Name of the project
            run_id: ID of the run

        Returns:
            Run information dictionary

        Raises:
            ValueError: If the project or run doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        project_path = self.file_manager.get_project_path(project_name)
        run_path = project_path / "Run" / run_id

        if not run_path.exists():
            raise ValueError(
                f"Run '{run_id}' does not exist in project '{project_name}'."
            )

        config = self.file_manager.get_project_config(project_name)
        run_info = next((r for r in config.get("runs", []) if r["id"] == run_id), {})

        # Check for state files
        state_path = run_path / "state"
        state_files = []
        if state_path.exists():
            state_files = [f.stem for f in state_path.glob("*.json")]

        # Check for output files
        output_path = run_path / "output"
        output_files = []
        if output_path.exists():
            output_files = [f.stem for f in output_path.glob("*.json")]

        # Check for database
        db_path = run_path / f"{run_id}.db"
        has_db = db_path.exists()

        return {
            "id": run_id,
            "project_name": project_name,
            "created_at": run_info.get("created_at", ""),
            "status": run_info.get("status", "unknown"),
            "path": str(run_path),
            "state_files": state_files,
            "output_files": output_files,
            "has_database": has_db,
        }

    def delete_run(self, project_name: str, run_id: str) -> None:
        """
        Delete a simulation run and all its contents.

        Args:
            project_name: Name of the project
            run_id: ID of the run

        Raises:
            ValueError: If the project or run doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        self.file_manager.delete_run(project_name, run_id)

    def list_components(self) -> Dict[str, Dict[str, CompRegDataI]]:
        """
        List all registered components for a project with their information.
        """
        return self.file_manager.list_components()

    def get_component(self, project_name: str, component_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a component, including its code and schemas.

        Args:
            project_name: Name of the project
            component_name: Name of the component

        Returns:
            Component information dictionary

        Raises:
            ValueError: If the project or component doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        component = self.file_manager.get_component(project_name, component_name)

        config = self.file_manager.get_project_config(project_name)
        component_info = next(
            (c for c in config.get("components", []) if c["name"] == component_name), {}
        )

        return {
            "name": component_name,
            "project_name": project_name,
            "created_at": component_info.get("created_at", ""),
            "python_code": component["python_code"],
            "input_schema": component["input_schema"],
            "output_schema": component["output_schema"],
        }

    def delete_component(self, project_name: str, component_name: str) -> None:
        """
        Delete a component and all its files.

        Args:
            project_name: Name of the project
            component_name: Name of the component

        Raises:
            ValueError: If the project or component doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        self.file_manager.delete_component(project_name, component_name)

    def save_simulation_state(
        self, project_name: str, state: Dict, gen: Dict
    ) -> Dict[str, Any]:
        """
        Save simulation state data to a JSON file.

        Args:
            project_name: Name of the project
            data: Data to save

        Returns:
            Information about the saved state

        Raises:
            ValueError: If the project or run doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        file_path = self.file_manager.save_state_data(
            project_name, stateData=state, genData=gen
        )

        return {
            "project_name": project_name,
            "file_path": str(file_path),
        }

    def get_simulation_state(self, project_name: str) -> Dict[str, Any]:
        """
        Get simulation state data from a JSON file.

        Args:
            project_name: Name of the project

        Returns:
            State data

        Raises:
            ValueError: If the project, run, or state file doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        return self.file_manager.get_state_data(project_name)

    def save_simulation_edge(self, project_name: str, data: Dict) -> Dict[str, Any]:
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        file_path = self.file_manager.save_edge_data(project_name, data)

        return {
            "project_name": project_name,
            "file_path": str(file_path),
        }

    def get_simulation_edge(self, project_name: str) -> List[Dict]:
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        return self.file_manager.get_edge_data(project_name)

    def save_simulation_node(self, project_name: str, data: Dict) -> Dict[str, Any]:
        """
        Save simulation output data to a JSON file.

        Args:
            project_name: Name of the project
            data: Data to save

        Returns:
            Information about the saved output

        Raises:
            ValueError: If the project or run doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        file_path = self.file_manager.save_node_data(project_name, data)

        return {
            "project_name": project_name,
            "file_path": str(file_path),
        }

    def get_simulation_node(self, project_name: str) -> List[Dict]:
        """
        Get simulation output data from a JSON file.

        Args:
            project_name: Name of the project

        Returns:
            Output data

        Raises:
            ValueError: If the project, run, or output file doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        return self.file_manager.get_node_data(project_name)

    def get_db_connection(self, project_name: str, run_id: str):
        """
        Get a database connection for a simulation run.

        Args:
            project_name: Name of the project
            run_id: ID of the run

        Returns:
            DuckDB connection

        Raises:
            ValueError: If the project or run doesn't exist
            FileNotFoundError: If the database file doesn't exist
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        return self.db_manager.get_run_db_connection(project_name, run_id)

    def get_run_path(self, project_name: str, run: str) -> Union[str, None]:
        """
        Get the path to a specific run within a project.

        Args:
            project_name: Name of the project
            run: Name of the run

        Returns:
            Path to the run directory
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        project_path = self.file_manager.get_project_path(project_name)
        path = project_path / "Run" / run / f"{run}.csv"
        if not path.is_file():
            return None
        return str(path)

    def get_Run_Sim_data(self, project_name: str, run: str) -> Union[Dict[str, Any], None]:
        """
        Get the simulation data for a specific run within a project.

        Args:
            project_name: Name of the project
            run: Name of the run

        Returns:
            Simulation data as a dictionary
        """
        if not self.file_manager.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")

        project_path = self.file_manager.get_project_path(project_name)
        path = project_path / "Run" / run / "simData.json"
        if not path.is_file():
            return None
        with open(path, "r") as f:
            data = json.load(f)
        return data