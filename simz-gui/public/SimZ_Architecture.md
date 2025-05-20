# SimZ Architecture Documentation

## Table of Contents

1. [Project Structure](#project-structure)
2. [Core Classes](#core-classes)
3. [Component System](#component-system)
4. [Engine Functionality](#engine-functionality)
5. [User Interaction](#user-interaction)

## Project Structure

SimZ is a discrete event simulation engine built on top of SimPy, providing a structured way to create, manage, and execute simulation projects. The system follows a well-defined project structure that organizes simulation components, data, and execution results.

### Project Organization

When a user creates a project in SimZ, the following directory structure is established:

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
    └── save/                   # Saved state for components, GenTypes, and edges
        ├── dataState.json      # Component and connection state
        └── genState.json       # GenType definitions
```

### State Management

SimZ maintains project state through several key files:

1. **dataState.json**: Stores the state of components and their connections (edges). This includes component configurations, positions, and properties.

2. **genState.json**: Contains definitions of GenTypes (entity types) that flow through the simulation.

3. **edge.json**: Defines the connections between components, specifying source and target components and their respective handlers.

The `ProjectManager` class integrates with `FileManager` and `DBManager` to provide a unified interface for managing simulation projects, handling file operations, and database interactions.

## Core Classes

### Component Classes

The `Component` abstract base class is the foundation of all simulation components. It provides:

- Registration in a component registry
- Access to shared resources (GenState, WorkflowGraph, Logger)
- Methods for handling simulation flow
- Variable storage through KVStorage
- Event logging capabilities

Key component implementations include:

1. **Generator**: Creates and emits GenType entities into the simulation
2. **Resource**: Processes entities with capacity constraints using SimPy's Resource

### GenState Classes

The GenType system defines the entities that flow through the simulation:

1. **GenTypeState**: A dictionary-like container that stores all GenTypes in the simulation
2. **GenTypes**: Defines a specific entity type with attributes
3. **GenAttributes**: Defines the attributes and their types for a GenType
4. **GenContainer**: A wrapper that holds GenType instances as they flow through the simulation

Example of a GenContainer:

```python
container = GenContainer(
    Data={"Water": water_gen_type},
    targetComp="resource1",
    targetHandler="Water-in"
)
```

### Workflow Classes

The workflow system defines how components are connected:

1. **WorkflowGraph**: Uses NetworkX to represent the simulation as a directed graph
2. **Edge**: Defines a connection between components with source and target handles

The workflow graph enables:
- Finding execution paths
- Detecting cycles
- Determining root components
- Visualizing the simulation flow

### Container System

Containers are the primary mechanism for passing data between components:

1. Containers hold GenType instances with their current attribute values
2. Each container has a target component and handler
3. The `_next()` method routes containers to their next destination
4. Components can modify container data during processing

## Component System

### Variable Storage

Components store variables using the `KVStorage` system:

```python
# Store data
component.store_data('processed_count', 42)

# Retrieve data
count = component.get_data('processed_count', 0)

# Increment counter
new_count = component.increment_counter('processed_count')
```

This provides a flexible key-value store for maintaining component state across simulation runs.

### Execution Logic

Components execute through the following mechanism:

1. The simulation engine calls the component's `run()` method
2. For generators, this creates entities at specified intervals
3. For resources, this processes entities with capacity constraints
4. Custom code is executed via the `CodeExec` system
5. The `_next()` method routes output to the next component

The execution flow is controlled by SimPy's environment:

```python
# Start root components
for comp in root_comps:
    self.env.process(comp.run(input=None))

# Run the simulation
self.env.run(until=self.run_time)
```

### Component Types

SimZ includes several built-in component types:

1. **Generator**: Creates entities at specified intervals or based on custom logic
   - Can generate entities with fixed or random attributes
   - Supports various distribution patterns (uniform, normal, etc.)

2. **Resource**: Processes entities with capacity constraints
   - Uses SimPy's Resource for managing concurrent processing
   - Tracks queue length and processing times
   - Supports custom processing logic

Components can be extended with custom code through the `CodeExec` system, which allows users to define:
- Startup initialization
- Custom generation logic
- Processing behavior
- Event handling

## Engine Functionality

### Simulation Execution

The simulation engine executes components according to the workflow through these steps:

1. **Loading**: The `SimulationBuilder` loads component definitions, GenTypes, and the workflow graph
2. **Building**: Components are instantiated and configured
3. **Execution**: Root components are started, and the SimPy environment runs the simulation
4. **Cleanup**: Resources are released, and logs are closed

The execution is driven by SimPy's event-based simulation engine, which manages the simulation timeline and event processing.

### Data Generation

During simulation, the engine generates several data files:

1. **CSV Logs**: Detailed event logs with timestamps, component IDs, actions, and values
2. **Component Analytics**: Performance metrics for each component
3. **Visualization Data**: Chart and table data for the UI

The `CsvLogger` records events with the following structure:
- time: Simulation time
- component_id: ID of the component
- component_type: Type of the component
- action: Action being performed (IN, OUT, GENERATE, etc.)
- values: Additional values related to the action
- PDV: Container data display

### Tracking and Recording

The engine tracks simulation behavior through:

1. **Event Logging**: Components log events using the `log_event()` method
2. **Analytics**: The `AnalyticsFactory` creates analytics for different component types
3. **Metrics**: Components can track custom metrics using `track_metric()`

This data is used to generate visualizations and performance reports.

## User Interaction

### Graph Interface

Users interact with the simulation through a graph-based interface that:

1. Allows creating and connecting components visually
2. Provides a workflow representation of the simulation
3. Enables visualization of simulation execution

The `WorkflowGraph` class supports visualization with:
```python
workflow.visualize(
    figsize=(12, 8),
    title="Workflow Graph Visualization",
    show_handles=True
)
```

### Table Views

The system generates table data for visualization using the `Table` class:

```python
table_props = Table.create_table_props(
    data=[{"component": "Generator1", "processed": 100}],
    column_order=["component", "processed"],
    column_labels={"component": "Component Name", "processed": "Processed Count"}
)
```

Tables can display:
- Component performance metrics
- Entity counts and distributions
- Queue statistics
- Custom metrics

### Code Customization

Users can customize component behavior by writing Python code that is executed within the component:

1. **Generator Functions**: Define how entities are created
2. **Processing Functions**: Define how entities are processed
3. **Event Handlers**: Respond to simulation events

Example of a custom generator function:

```python
def generate(component):
    # Create a new entity with random temperature
    container = component.generate_with_normal_distribution('Water', 'temperature', 25, 5)
    
    # Add more attributes
    component.set_container_data(container, 'Water', 'volume', 100)
    
    # Wait before returning the container
    yield component.wait_random(1, 3)
    
    return container
```

The system provides a rich set of helper methods documented in `component_helper_methods.md` to simplify writing custom component functions.

### Socket.IO API

The system exposes a Socket.IO API that allows external applications to:

1. Create and manage projects
2. Register components
3. Create simulation runs
4. Retrieve simulation data

This enables integration with web-based user interfaces and other systems.

## Conclusion

SimZ provides a flexible, extensible architecture for building discrete event simulations. By combining the power of SimPy with a structured project management system and customizable components, it enables users to create complex simulations with minimal effort.

The component-based design, workflow graph, and GenType system provide a clear separation of concerns while allowing for rich interactions between simulation elements. The comprehensive logging and analytics capabilities enable detailed analysis of simulation performance and behavior.
