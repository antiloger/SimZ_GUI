# SimZ Engine

SimZ Engine is a discrete event simulation builder that provides a robust file management system for simulation projects.

## Overview

The SimZ Engine provides a structured way to manage simulation projects, components, runs, and their associated data. It uses an object-oriented design to make managing simulation data and files simple and efficient.

## Features

- Project management (create, list, get, update, delete)
- Component registration (register, list, get, delete)
- Simulation run management (create, list, get, delete)
- State and output data management
- DuckDB integration for simulation data storage
- Socket.IO server for real-time communication with clients

## Project Structure

```
simz-Engine/
├── src/
│   ├── core/
│   │   ├── file_manager.py     # Handles file operations for projects
│   │   ├── db_manager.py       # Manages DuckDB databases for simulation runs
│   │   ├── project_manager.py  # Integrates file and DB managers
│   │   └── socket_manager.py   # Socket.IO server for real-time communication
│   ├── utils/                  # Utility functions and helpers
│   └── models/                 # Data models and structures
├── tests/                      # Unit and integration tests
├── examples/                   # Example simulations and usage
│   └── socket_client.py        # Example Socket.IO client
├── main.py                     # Demo application
├── server.py                   # Socket.IO server
└── requirements.txt            # Python dependencies
```

## Data Structure

When a project is created, it follows this structure:

```
projects/
└── [project_name]/
    ├── config.json             # Project configuration and metadata
    ├── Run/                    # Simulation runs
    │   └── [run_id]/
    │       ├── [run_id].db     # DuckDB database for the run
    │       ├── state/          # JSON files with simulation state data
    │       │   └── *.json
    │       └── output/         # JSON files with simulation outputs
    │           └── *.json
    └── RegisterComponent/      # Registered simulation components
        └── [component_name]/
            ├── [component_name].py  # Python implementation
            ├── input.json      # Input schema
            └── output.json     # Output schema
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd simz-Engine
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### File Manager Demo

Run the demo application to see the basic functionality:

```
python main.py
```

You can specify a custom project directory and name:

```
python main.py --project-dir ./my_projects --project-name my_simulation
```

### Socket.IO Server

Run the Socket.IO server to enable real-time communication with clients:

```
python server.py
```

By default, the server binds to 0.0.0.0:5000. You can customize the host and port:

```
python server.py --host localhost --port 8080
```

### Socket.IO Client Example

To test the Socket.IO server, run the example client:

```
python examples/socket_client.py
```

The client will connect to the server and perform a series of operations to demonstrate the API.

### Basic API Usage

```python
from src.core.project_manager import ProjectManager

# Initialize project manager
project_manager = ProjectManager()

# Create a new project
project_info = project_manager.create_project("my_project", "My simulation project")

# Register a component
component_info = project_manager.register_component(
    "my_project",
    "MyComponent",
    python_code_string,
    input_schema_dict,
    output_schema_dict
)

# Create a simulation run
run_info = project_manager.create_run("my_project")
run_id = run_info["id"]

# Save simulation state
project_manager.save_simulation_state(
    "my_project",
    run_id,
    "state_name",
    state_data_dict
)

# Get a database connection
conn = project_manager.get_db_connection("my_project", run_id)

# Add entities, events, and custom data
# ...

# Close connection when done
conn.close()
```

### Socket.IO API

The Socket.IO server provides the following events:

- **Project Management**:
  - `list_projects`: List all available projects
  - `create_project`: Create a new project
  - `get_project`: Get project details

- **Component Management**:
  - `list_components`: List all components for a project
  - `register_component`: Register a new component
  - `get_component`: Get component details

- **Run Management**:
  - `list_runs`: List all runs for a project
  - `create_run`: Create a new simulation run
  - `get_run`: Get run details

## License

[MIT License](LICENSE) 