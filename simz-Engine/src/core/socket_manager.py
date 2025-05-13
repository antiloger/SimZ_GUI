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
                    print("[SIM] Generating simulation output...")
                    outputData = sim_builder.output(csvOutput)

                    print("[SIM] Saving simulation output...")
                    output_path = Path(f"{project_path}/Run/{run_id}")
                    sim_builder.save_simulation_output(output_path, outputData)
                    print(f"[SIM] Output saved to {output_path}/simData.json")

                    # Clean up simulation resources properly
                    print("[SIM] Cleaning up simulation resources...")
                    sim_builder.cleanup()
                    self.emit("sim_run_status", {"status": "completed"}, sid)
                    print("[DATA] Simulation completed successfully")

                    self.emit(
                        "sim_update",
                        {"status": f"[SIM]current_run time {sim_builder.env.now}"},
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
            project_name = data.get("project_name")
            if not project_name:
                return {"error": "Project name is required"}
            run_id = data.get("run_id")
            if not run_id:
                return {"error": "Run ID is required"}

            data = self.project_manager.get_Run_Sim_data(project_name, run_id)
            if data is None:
                return {"data": []}
            return {"data": data["dashboradData"]}

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
