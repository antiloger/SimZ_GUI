import socketio
import eventlet
from flask import Flask
from typing import Dict, Any, Optional, Callable

# Add env_manager import
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
        self.project_manager = project_manager
        
        # Use provided config or get from env_manager
        self.config = config or env_manager.get_all()
        
        # Initialize Socket.IO server with cors options from config
        cors_origins = self.config.get('CORS_ALLOWED_ORIGINS', '*')
        self.sio = socketio.Server(cors_allowed_origins=cors_origins)
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.wsgi_app = socketio.WSGIApp(self.sio, self.app.wsgi_app)
        
        # Set debug mode from config
        self.app.debug = self.config.get('DEBUG', False)
        
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
                'connected_at': socketio.time.time(),
                'current_project': None,
                'current_run': None
            }
            
        @self.sio.event
        def disconnect(sid):
            """Handle client disconnection."""
            print(f"Client disconnected: {sid}")
            if sid in self.clients:
                del self.clients[sid]
    
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
        def list_projects(sid):
            """List all available projects."""
            if not self.project_manager:
                return {'error': 'Project manager not available'}
            
            try:
                projects = self.project_manager.list_projects()
                return {'projects': projects}
            except Exception as e:
                return {'error': str(e)}
        
        @self.sio.event
        def create_project(sid, data):
            """Create a new project."""
            if not self.project_manager:
                return {'error': 'Project manager not available'}
            
            try:
                name = data.get('name')
                description = data.get('description', '')
                
                if not name:
                    return {'error': 'Project name is required'}
                
                project_info = self.project_manager.create_project(name, description)
                return {'project': project_info}
            except Exception as e:
                return {'error': str(e)}
        
        @self.sio.event
        def get_project(sid, data):
            """Get project details."""
            if not self.project_manager:
                return {'error': 'Project manager not available'}
            
            try:
                name = data.get('name')
                
                if not name:
                    return {'error': 'Project name is required'}
                
                project_info = self.project_manager.get_project(name)
                return {'project': project_info}
            except Exception as e:
                return {'error': str(e)}
    
    def setup_run_handlers(self):
        """Set up simulation run event handlers."""
        @self.sio.event
        def list_runs(sid, data):
            """List all runs for a project."""
            if not self.project_manager:
                return {'error': 'Project manager not available'}
            
            try:
                project_name = data.get('project_name')
                
                if not project_name:
                    return {'error': 'Project name is required'}
                
                runs = self.project_manager.list_runs(project_name)
                return {'runs': runs}
            except Exception as e:
                return {'error': str(e)}
        
        @self.sio.event
        def create_run(sid, data):
            """Create a new simulation run."""
            if not self.project_manager:
                return {'error': 'Project manager not available'}
            
            try:
                project_name = data.get('project_name')
                run_name = data.get('run_name')
                
                if not project_name:
                    return {'error': 'Project name is required'}
                
                run_info = self.project_manager.create_run(project_name, run_name)
                
                # Set client's current run
                if sid in self.clients:
                    self.clients[sid]['current_project'] = project_name
                    self.clients[sid]['current_run'] = run_info['id']
                
                return {'run': run_info}
            except Exception as e:
                return {'error': str(e)}
        
        @self.sio.event
        def get_run(sid, data):
            """Get run details."""
            if not self.project_manager:
                return {'error': 'Project manager not available'}
            
            try:
                project_name = data.get('project_name')
                run_id = data.get('run_id')
                
                if not project_name or not run_id:
                    return {'error': 'Project name and run ID are required'}
                
                run_info = self.project_manager.get_run(project_name, run_id)
                return {'run': run_info}
            except Exception as e:
                return {'error': str(e)}
    
    def setup_component_handlers(self):
        """Set up component event handlers."""
        @self.sio.event
        def list_components(sid, data):
            """List all components for a project."""
            if not self.project_manager:
                return {'error': 'Project manager not available'}
            
            try:
                project_name = data.get('project_name')
                
                if not project_name:
                    return {'error': 'Project name is required'}
                
                components = self.project_manager.list_components(project_name)
                return {'components': components}
            except Exception as e:
                return {'error': str(e)}
        
        @self.sio.event
        def register_component(sid, data):
            """Register a new component."""
            if not self.project_manager:
                return {'error': 'Project manager not available'}
            
            try:
                project_name = data.get('project_name')
                component_name = data.get('component_name')
                python_code = data.get('python_code')
                input_schema = data.get('input_schema')
                output_schema = data.get('output_schema')
                
                if not all([project_name, component_name, python_code, input_schema, output_schema]):
                    return {'error': 'Missing required fields'}
                
                component_info = self.project_manager.register_component(
                    project_name, component_name, python_code, input_schema, output_schema
                )
                return {'component': component_info}
            except Exception as e:
                return {'error': str(e)}
        
        @self.sio.event
        def get_component(sid, data):
            """Get component details."""
            if not self.project_manager:
                return {'error': 'Project manager not available'}
            
            try:
                project_name = data.get('project_name')
                component_name = data.get('component_name')
                
                if not project_name or not component_name:
                    return {'error': 'Project name and component name are required'}
                
                component_info = self.project_manager.get_component(project_name, component_name)
                return {'component': component_info}
            except Exception as e:
                return {'error': str(e)}
    
    def run(self, host: str = None, port: int = None):
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
        host = host or self.config.get('HOST')
        port = port or self.config.get('PORT')
        
        print(f"Socket.IO server running on http://{host}:{port}")
        eventlet.wsgi.server(eventlet.listen((host, port)), self.app) 