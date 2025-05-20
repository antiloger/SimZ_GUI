from pathlib import Path
import time
import socketio
import eventlet
from flask import Flask
from typing import Dict, Any, Optional, Callable, Union
import simplejson
import json

# Add env_manager import
from src.core.project_manager import ProjectManager
from src.sim.ContainerSearch import ContainerScraper
from src.sim.build import SimulationBuilder
from src.sim.csvpaser import CSVScraper
from src.utils.env_manager import env_manager


class SocketManager:
    """
    SocketManager handles Socket.IO server operations for real-time communication
    with the simulation clients.
    """

    def __init__(self, project_manager=None, config=None):
        """
        Initialize the SocketManager with an optional ProjectManager instance.

        Args:
            project_manager: Optional ProjectManager instance to use for project operations.
            config: Optional configuration dictionary to override environment values.
        """

        if project_manager is None:
            raise ValueError("ProjectManager instance is required")

        self.project_manager: ProjectManager = project_manager

        # Use provided config or get from env_manager
        self.config = config or env_manager.get_all()

        # Initialize Socket.IO server with cors options from config
        cors_origins = self.config.get("CORS_ALLOWED_ORIGINS", "*")
        self.sio = socketio.Server(
            cors_allowed_origins=cors_origins,
            ping_timeout=120,
            max_http_buffer_size=10 * 1024 * 1024,
        )
        # engineio_logger=True,
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.wsgi_app = socketio.WSGIApp(self.sio, self.app.wsgi_app)

        # Set debug mode from config
        self.app.debug = self.config.get("DEBUG", False)

        # Client tracking
        self.clients = {}

        # Register default event handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default Socket.IO event handlers."""

        @self.sio.event
        def connect(sid, environ):
            """Handle client connection."""
            print(f"Client connected: {sid}")
            self.clients[sid] = {
                "connected_at": time.time(),
                "current_project": None,
                "current_run": None,
            }

        @self.sio.event
        def disconnect(sid):
            """Handle client disconnection."""
            print(f"Client disconnected: {sid}")
            if sid in self.clients:
                del self.clients[sid]

        @self.sio.event
        def ping(sid):
            """Handle ping event."""
            print(f"Ping received from {sid}")
            return "pong"

    def register_event_handler(self, event: str, handler: Callable):
        """
        Register a custom event handler.

        Args:
            event: Name of the event
            handler: Callable handler function
        """
        self.sio.on(event, handler)

    def emit(self, event: str, data: Dict[str, Any], room=None):
        """
        Emit an event to connected clients.

        Args:
            event: Name of the event
            data: Data to send
            room: Optional room (client ID) to emit to
        """
        self.sio.emit(event, data, room=room)

    def setup_project_handlers(self):
        """Set up project-related event handlers."""

        @self.sio.event
        def list_projects(sid, data=None):
            """List all available projects."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                projects = self.project_manager.list_projects()
                return {"projects": projects}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def create_project(sid, data):
            """Create a new project."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                name = data.get("name")
                description = data.get("description", "")

                if not name:
                    return {"error": "Project name is required"}

                project_info = self.project_manager.create_project(name, description)
                return {"project": project_info}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def get_project(sid, data):
            """Get project details."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                name = data.get("name")

                if not name:
                    return {"error": "Project name is required"}

                project_info = self.project_manager.get_project(name)
                return {"project": project_info}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def project_config(sid, data):
            """Update project configuration."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")

                if not project_name:
                    return {"error": "Project name is required"}

                # Extract configuration data
                description = data.get("description")
                version = data.get("version")

                # Update project configuration
                updated_project = self.project_manager.update_project(
                    project_name=project_name,
                    description=description,
                    version=version
                )

                return {"data": updated_project}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def delete_project(sid, data):
            """Delete an entire project."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")

                if not project_name:
                    return {"error": "Project name is required"}

                # Delete the project
                self.project_manager.delete_project(project_name)

                return {"data": {"success": True, "message": f"Project '{project_name}' deleted successfully"}}
            except Exception as e:
                return {"error": str(e)}

    def setup_run_handlers(self):
        """Set up simulation run event handlers."""

        @self.sio.event
        def list_runs(sid, data):
            """List all runs for a project."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")

                if not project_name:
                    return {"error": "Project name is required"}

                runs = self.project_manager.list_runs(project_name)
                print(runs)
                return {"runs": runs}

            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def create_run(sid, data):
            """Create a new simulation run."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")
                run_name = data.get("run_name")

                if not project_name:
                    return {"error": "Project name is required"}

                run_info = self.project_manager.create_run(project_name, run_name)

                # Set client's current run
                if sid in self.clients:
                    self.clients[sid]["current_project"] = project_name
                    self.clients[sid]["current_run"] = run_info["id"]

                return {"run": run_info}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def get_run(sid, data):
            """Get run details."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")
                run_id = data.get("run_id")

                if not project_name or not run_id:
                    return {"error": "Project name and run ID are required"}

                run_info = self.project_manager.get_run(project_name, run_id)
                return {"run": run_info}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def delete_run(sid, data):
            """Delete a simulation run."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")
                run_id = data.get("run_id")

                if not project_name:
                    return {"error": "Project name is required"}

                if not run_id:
                    return {"error": "Run ID is required"}

                # Delete the run
                self.project_manager.delete_run(project_name, run_id)

                # If this client was using this run, clear the current run
                if sid in self.clients and self.clients[sid]["current_run"] == run_id:
                    self.clients[sid]["current_run"] = None

                return {"data": {"success": True, "message": f"Run '{run_id}' deleted successfully"}}
            except Exception as e:
                return {"error": str(e)}

    def setup_component_handlers(self):
        """Set up component event handlers."""

        @self.sio.event
        def list_components(sid, data):
            """List all components for a project."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                components = self.project_manager.list_components()
                # Convert Pydantic models to dictionaries
                serializable_components = {}
                for category, comps in components.items():
                    serializable_components[category] = {
                        comp_type: comp_data.model_dump()
                        if hasattr(comp_data, "model_dump")
                        else comp_data.dict()
                        for comp_type, comp_data in comps.items()
                    }

                return {"components": serializable_components}
            except Exception as e:
                return {"error": str(e)}

        # @self.sio.event
        # def register_component(sid, data):
        #     """Register a new component."""
        #     if not self.project_manager:
        #         return {"error": "Project manager not available"}
        #
        #     try:
        #         project_name = data.get("project_name")
        #         component_name = data.get("component_name")
        #         python_code = data.get("python_code")
        #         input_schema = data.get("input_schema")
        #         output_schema = data.get("output_schema")
        #
        #         if not all(
        #             [
        #                 project_name,
        #                 component_name,
        #                 python_code,
        #                 input_schema,
        #                 output_schema,
        #             ]
        #         ):
        #             return {"error": "Missing required fields"}
        #
        #         component_info = self.project_manager.register_component(
        #             project_name,
        #             component_name,
        #             python_code,
        #             input_schema,
        #             output_schema,
        #         )
        #         return {"component": component_info}
        #     except Exception as e:
        #         return {"error": str(e)}

        @self.sio.event
        def get_component(sid, data):
            """Get component details."""
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")
                component_name = data.get("component_name")

                if not project_name or not component_name:
                    return {"error": "Project name and component name are required"}

                component_info = self.project_manager.get_component(
                    project_name, component_name
                )
                return {"component": component_info}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def save_state(sid, data):
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")
                stateData = data.get("stateData")
                genData = data.get("genData")

                if not project_name or not stateData:
                    return {"error": "Project name and component name are required"}

                self.project_manager.save_simulation_state(
                    project_name, stateData, genData
                )

                return {"response": "Simulation state saved successfully"}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def get_state(sid, data):
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")

                if not project_name:
                    return {"error": "Project name required"}

                dataState = self.project_manager.get_simulation_state(project_name)

                return dataState
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def save_node(sid, data):
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")
                stateData = data.get("data")

                if not project_name or not stateData:
                    return {"error": "Project name and component name are required"}

                self.project_manager.save_simulation_node(project_name, stateData)

                return {"response": "Simulation state saved successfully"}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def get_node(sid, data):
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")

                if not project_name:
                    return {"error": "Project name required"}

                dataState = self.project_manager.get_simulation_node(project_name)

                return {"data": dataState}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def save_edge(sid, data):
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")
                stateData = data.get("data")

                if not project_name or not stateData:
                    return {"error": "Project name and component name are required"}

                self.project_manager.save_simulation_edge(project_name, stateData)

                return {"response": "Simulation state saved successfully"}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def get_edge(sid, data):
            if not self.project_manager:
                return {"error": "Project manager not available"}

            try:
                project_name = data.get("project_name")

                if not project_name:
                    return {"error": "Project name required"}

                dataState = self.project_manager.get_simulation_edge(project_name)

                return {"data": dataState}
            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def run_simulation(sid, data):
            try:
                project_name = data.get("project_name")
                if not project_name:
                    return {"error": "Project name is required"}

                run_id = data.get(
                    "run_name", time.strftime("%Y%m%d%H%M%S", time.localtime())
                )
                # run_count_syb = data.get("run_count_syb", "s")
                # sim_param = data.get("sim_param", {})
                sim_time: Union[int, None] = data.get("sim_time", 0)
                if sim_time == 0:
                    sim_time = None

                project_data = self.project_manager.get_project(project_name)
                project_path: str = project_data["path"]
                self.emit("sim_run_status", {"status": "building"}, sid)
                self.emit("sim_update", {"status": "[SIM] Simulation started"}, sid)

                def update_progress(progress):
                    self.emit("sim_update", {"status": progress}, sid)

                try:
                    sim_builder = SimulationBuilder(
                        runName=run_id,
                        ProjectPath=Path(f"{project_path}/save"),
                        runPath=Path(f"{project_path}/Run"),
                        run_time=sim_time,
                        socketLog=update_progress,
                    )
                    self.emit(
                        "sim_update",
                        {"status": f"[SIM]current_run time {sim_builder.env.now}"},
                        sid,
                    )

                    self.emit("sim_run_status", {"status": "running"}, sid)
                    sim_builder.run_all()
                    self.emit(
                        "sim_update", {"status": "[SIM] add run to config file"}, sid
                    )
                    self.project_manager.add_run_to_project(project_name, run_id)

                    # Use context manager to ensure proper cleanup of CSVScraper
                    csv_file_path = f"{project_path}/Run/{run_id}/{run_id}.csv"
                    print(f"[SIM] Opening CSV file: {csv_file_path}")
                    csvOutput = CSVScraper(csv_file_path)

                    # Generate component-specific analytics
                    print("[SIM] Generating component-specific analytics...")
                    component_insights = sim_builder.generate_component_insights(
                        csvOutput
                    )

                    # Save component analytics to separate files
                    output_path = Path(f"{project_path}/Run/{run_id}")
                    sim_builder.save_component_analytics(
                        output_path, component_insights
                    )
                    print(
                        f"[SIM] Component analytics saved to {output_path}/components/"
                    )

                    # Save component ID-name mappings
                    print("[SIM] Saving component ID-name mappings...")
                    sim_builder.save_component_names(output_path)
                    print(
                        f"[SIM] Component names saved to {output_path}/component_names.json"
                    )

                    # Generate overall simulation output
                    print("[SIM] Generating simulation output...")
                    outputData = sim_builder.output(csvOutput)

                    print("[SIM] Saving simulation output...")
                    sim_builder.save_simulation_output(output_path, outputData)
                    print(f"[SIM] Output saved to {output_path}/simData.json")

                    # Clean up simulation resources properly
                    print("[SIM] Cleaning up simulation resources...")
                    sim_builder.cleanup()
                    self.emit("sim_run_status", {"status": "completed"}, sid)
                    print("[DATA] Simulation completed successfully")

                    # Safely access env.now with error handling
                    try:
                        current_time = sim_builder.env.now
                        self.emit(
                            "sim_update",
                            {"status": f"[SIM]current_run time {current_time}"},
                            sid,
                        )
                    except Exception as e:
                        print(f"Warning: Could not access simulation time: {e}")
                        self.emit(
                            "sim_update",
                            {"status": "[SIM] Simulation completed"},
                            sid,
                        )
                    # Explicitly delete objects to ensure garbage collection
                    del sim_builder
                    del csvOutput

                    # Force garbage collection to free memory
                    import gc

                    gc.collect()

                except Exception as e:
                    print(f"Simulation error: {e}")
                    self.emit("sim_run_status", {"status": "error"}, sid)
                    self.emit(
                        "sim_update",
                        {"status": f"[ERROR] Simulation ERROR: \n{e}"},
                        sid,
                    )

                    # Force garbage collection
                    import gc

                    gc.collect()

            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def full_event_list(sid, data):
            try:
                project_name = data.get("project_name")
                if not project_name:
                    return {"error": "Project name is required"}
                run_id = data.get("run_id")
                if not run_id:
                    return {"error": "Run ID is required"}

                table_data: Dict[str, Any] = data.get("table_data")

                run_path = self.project_manager.get_run_path(project_name, run_id)
                if not run_path:
                    return {"error": "Run path not found"}

                paser = CSVScraper(run_path)

                print(f"[REQData] {table_data}")

                page = table_data.get("page", 1)
                page_size = table_data.get("page_size", 10)
                sort_column = table_data.get("sort_column", None)
                sort_direction = table_data.get("sort_direction", "asc")
                search_query = table_data.get("search_query", None)
                search_columns = table_data.get("search_columns", None)
                filter_conditions = table_data.get("filter_conditions", None)
                include_columns = table_data.get("include_columns", None)

                data = paser.get_table_data(
                    page=page,
                    page_size=page_size,
                    sort_column=sort_column,
                    sort_direction=sort_direction,
                    search_query=search_query,
                    search_columns=search_columns,
                    filter_conditions=filter_conditions,
                    include_columns=include_columns,
                )
                paser.close()

                jsonStr = simplejson.dumps(data, ignore_nan=True)
                clean_data = json.loads(jsonStr)

                print(f"[RESData] {clean_data}")
                return {"data": clean_data}

            except Exception as e:
                return {"error": str(e)}

        @self.sio.event
        def filter_data(sid, data):
            pass

        @self.sio.event
        def get_sim_data(sid, data):
            """
            Get simulation data including dashboard charts and tables for a specific run.

            Args:
                data: Dictionary containing project_name and run_id

            Returns:
                Dictionary containing dashboard data (charts and tables)
            """
            project_name = data.get("project_name")
            if not project_name:
                return {"error": "Project name is required"}
            run_id = data.get("run_id")
            if not run_id:
                return {"error": "Run ID is required"}

            sim_data = self.project_manager.get_Run_Sim_data(project_name, run_id)
            if sim_data is None:
                return {"data": {"charts": [], "tables": []}}

            # Prepare response with both charts and tables
            response_data = {
                "charts": sim_data.get("dashboradData", []),
                "tables": sim_data.get("dashboardTable", [])
            }

            print(f"[SIM_DATA] Returning charts and tables for {project_name}/{run_id}")
            return {"data": response_data}

        @self.sio.event
        def get_container_data(sid, data):
            project_name = data.get("project_name")
            if not project_name:
                return {"error": "Project name is required"}
            run_id = data.get("run_id")
            if not run_id:
                return {"error": "Run ID is required"}
            container_id = data.get("container_id")
            if not container_id:
                return {"error": "Container ID is required"}
            run_path = self.project_manager.get_run_path(project_name, run_id)
            if run_path is None:
                return {"error": "Run path not found"}
            inst = ContainerScraper(run_path)
            data = inst.analyze_container_workflow_enhanced(container_id)
            print(f"[RESData] {data}")
            return {"data": data}

        @self.sio.event
        def get_component_analytics(sid, data):
            """
            Get component-specific analytics data for a specific component.

            Args:
                data: Dictionary containing project_name, run_id, and component_id

            Returns:
                Dictionary containing component analytics data or error message
            """
            try:
                # Validate required parameters
                project_name = data.get("project_name")
                if not project_name:
                    return {"error": "Project name is required"}

                run_id = data.get("run_id")
                if not run_id:
                    return {"error": "Run ID is required"}

                component_id = data.get("component_id")
                if not component_id:
                    return {"error": "Component ID is required"}

                # Convert component_id to string to ensure compatibility with ComponentOutput
                component_id = str(component_id)

                # Get the run path (which is the CSV file path)
                csv_file_path = self.project_manager.get_run_path(project_name, run_id)
                print(f"CSV file path: {csv_file_path}")
                if csv_file_path is None:
                    return {"error": "Run path not found"}

                # Extract the directory path from the CSV file path
                # The CSV file path is like: projects/test-min/Run/2025-05-18-13-57-00/2025-05-18-13-57-00.csv
                # We need: projects/test-min/Run/2025-05-18-13-57-00/
                run_dir_path = str(Path(csv_file_path).parent)
                print(f"Run directory path: {run_dir_path}")

                # Check if component analytics file exists
                component_file_path = (
                    Path(run_dir_path)
                    / "components"
                    / f"component_analytics_{component_id}.json"
                )
                if not component_file_path.exists():
                    # If file doesn't exist, generate analytics on-the-fly
                    # We already have the CSV file path from above
                    print(f"Component analytics file not found, generating on-the-fly")
                    print(f"Using CSV file: {csv_file_path}")
                    if not Path(csv_file_path).exists():
                        return {"error": "CSV file not found"}

                    # Create CSVScraper
                    csv_scraper = CSVScraper(str(csv_file_path))

                    # Create analytics for the specific component
                    from src.sim.analytics import AnalyticsFactory

                    # Get component type from CSV data
                    component_type = "unknown"
                    try:
                        component_data = csv_scraper.components_data.get(
                            component_id, {}
                        )
                        if component_data and "type" in component_data:
                            component_type = component_data["type"]
                    except Exception as e:
                        print(f"Error getting component type: {e}")

                    # Create analytics instance
                    analytics = AnalyticsFactory.create_analytics(
                        component_id=str(component_id),  # Ensure component_id is a string
                        component_type=component_type,
                        csv_scraper=csv_scraper,
                    )

                    # Generate insights
                    component_insights = analytics.generate_component_insights()

                    # Convert to dictionary
                    try:
                        # Try the newer model_dump method first
                        analytics_data = component_insights.model_dump()
                    except AttributeError:
                        # Fall back to dict() for older versions, but with a warning
                        print("Warning: Using deprecated dict() method. Update to model_dump()")
                        analytics_data = component_insights.dict()

                    # Save for future use
                    components_dir = Path(run_dir_path) / "components"
                    if not components_dir.exists():
                        components_dir.mkdir(parents=True, exist_ok=True)

                    with open(component_file_path, "w") as f:
                        json.dump(analytics_data, f, indent=4)

                    return {"data": analytics_data}
                else:
                    # Load existing analytics data
                    with open(component_file_path, "r") as f:
                        analytics_data = json.load(f)

                    return {"data": analytics_data}

            except Exception as e:
                print(f"Error getting component analytics: {e}")
                return {"error": str(e)}

        @self.sio.event
        def list_component_analytics(sid, data):
            """
            List all available component analytics for a specific run.

            Args:
                data: Dictionary containing project_name and run_id

            Returns:
                Dictionary containing list of component IDs with available analytics
            """
            try:
                # Validate required parameters
                project_name = data.get("project_name")
                if not project_name:
                    return {"error": "Project name is required"}

                run_id = data.get("run_id")
                if not run_id:
                    return {"error": "Run ID is required"}

                # Get the run path (which is the CSV file path)
                csv_file_path = self.project_manager.get_run_path(project_name, run_id)
                if csv_file_path is None:
                    return {"error": "Run path not found"}

                # Extract the directory path from the CSV file path
                run_dir_path = str(Path(csv_file_path).parent)
                print(f"Run directory path for component analytics list: {run_dir_path}")

                # Check if components directory exists
                components_dir = Path(run_dir_path) / "components"
                if not components_dir.exists():
                    # If directory doesn't exist, no component analytics are available
                    return {"components": []}

                # List all component analytics files
                component_files = list(
                    components_dir.glob("component_analytics_*.json")
                )

                # Extract component IDs from filenames
                component_ids = []
                for file_path in component_files:
                    file_name = file_path.name
                    # Extract component ID from filename (component_analytics_[component_id].json)
                    if file_name.startswith(
                        "component_analytics_"
                    ) and file_name.endswith(".json"):
                        component_id = file_name[
                            len("component_analytics_") : -len(".json")
                        ]
                        component_ids.append(component_id)

                return {"components": component_ids}

            except Exception as e:
                print(f"Error listing component analytics: {e}")
                return {"error": str(e)}

        @self.sio.event
        def get_component_names(sid, data):
            """
            Get component ID-name mappings for a specific run.

            Args:
                data: Dictionary containing project_name and run_id

            Returns:
                Dictionary containing component ID-name mappings
            """
            try:
                # Validate required parameters
                project_name = data.get("project_name")
                if not project_name:
                    return {"error": "Project name is required"}

                run_id = data.get("run_id")
                if not run_id:
                    return {"error": "Run ID is required"}

                # Get the run path (which is the CSV file path)
                csv_file_path = self.project_manager.get_run_path(project_name, run_id)
                if csv_file_path is None:
                    return {"error": "Run path not found"}

                # Extract the directory path from the CSV file path
                run_dir_path = str(Path(csv_file_path).parent)
                print(f"Run directory path for component names: {run_dir_path}")

                # Check if component_names.json exists
                component_names_path = Path(run_dir_path) / "component_names.json"
                if not component_names_path.exists():
                    print(f"Component names file not found: {component_names_path}")
                    return {
                        "error": "Component names file not found",
                        "component_names": {},
                    }

                # Read the component names file
                try:
                    with open(component_names_path, "r") as f:
                        component_names = json.load(f)
                    return {"data": component_names}
                except Exception as e:
                    print(f"Error reading component names file: {e}")
                    return {
                        "error": f"Error reading component names file: {str(e)}",
                        "component_names": {},
                    }

            except Exception as e:
                print(f"Error getting component names: {e}")
                return {"error": str(e)}

    def run(self, host: Optional[str] = None, port: Optional[str] = None):
        """
        Run the Socket.IO server.

        Args:
            host: Optional host address to bind to (overrides config)
            port: Optional port to listen on (overrides config)
        """
        # Set up event handlers if project manager is available
        if self.project_manager:
            self.setup_project_handlers()
            self.setup_run_handlers()
            self.setup_component_handlers()

        # Use provided host/port or get from config
        host = host or self.config.get("HOST")
        port = port or self.config.get("PORT")

        print(f"Socket.IO server running on http://{host}:{port}")
        eventlet.wsgi.server(eventlet.listen((host, port)), self.app)
