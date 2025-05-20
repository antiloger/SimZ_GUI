# SimZ Engine Component Helper Methods

This document provides a comprehensive guide to all helper methods available in the SimZ Engine component classes. These methods are designed to simplify the process of writing custom component functions.

## Table of Contents

1. [Component Base Class Helper Methods](#component-base-class-helper-methods)
   - [Container Management](#container-management)
   - [Simulation Flow Control](#simulation-flow-control)
   - [Component Communication](#component-communication)
   - [Data Storage and Retrieval](#data-storage-and-retrieval)
   - [Logging and Monitoring](#logging-and-monitoring)
   - [Error Handling](#error-handling)
   - [Utility Functions](#utility-functions)

2. [Generator Class Helper Methods](#generator-class-helper-methods)
   - [Entity Generation](#entity-generation)
   - [Generation Control](#generation-control)
   - [Distribution Functions](#distribution-functions)

3. [Resource Class Helper Methods](#resource-class-helper-methods)
   - [Resource Management](#resource-management)
   - [Queue Management](#queue-management)
   - [Processing Control](#processing-control)

## Component Base Class Helper Methods

These methods are available in all component types as they are defined in the base `Component` class.

### Container Management

#### `get_container_data(container, gen_type, attribute)`
Get a specific attribute value from a container.

```python
# Get the 'temperature' attribute from a 'Water' type in the container
temp = component.get_container_data(container, 'Water', 'temperature')
```

#### `set_container_data(container, gen_type, attribute, value)`
Set a specific attribute value in a container.

```python
# Set the 'temperature' attribute to 25 for a 'Water' type in the container
component.set_container_data(container, 'Water', 'temperature', 25)
```

#### `copy_container(container)`
Create a deep copy of a container.

```python
# Create a copy of a container
new_container = component.copy_container(original_container)
```

#### `merge_container_data(target, source, overwrite=True)`
Merge data from source container into target container.

```python
# Merge data from container2 into container1
component.merge_container_data(container1, container2)
```

### Simulation Flow Control

#### `wait(duration)`
Wait for a specified duration in simulation time.

```python
# Wait for 5 time units
yield component.wait(5)
```

#### `wait_until(time_point)`
Wait until a specific simulation time point.

```python
# Wait until simulation time 100
yield component.wait_until(100)
```

#### `wait_random(min_duration, max_duration)`
Wait for a random duration between min_duration and max_duration.

```python
# Wait for a random duration between 5 and 10 time units
yield component.wait_random(5, 10)
```

### Component Communication

#### `get_component_by_id(comp_id)`
Get a component reference by ID.

```python
# Get a reference to a component with ID 'resource1'
resource = component.get_component_by_id('resource1')
```

#### `get_components_by_type(comp_type)`
Get all components of a specific type.

```python
# Get all Resource components
resources = component.get_components_by_type('Resource')
```

#### `send_to_component(container, comp_id, handler=None)`
Send a container directly to a specific component.

```python
# Send a container to component 'resource1' with handler 'Water-in'
component.send_to_component(container, 'resource1', 'Water-in')
```

### Data Storage and Retrieval

#### `store_data(key, value)`
Store data in component's KVStorage.

```python
# Store a counter value
component.store_data('processed_count', 42)
```

#### `get_data(key, default=None)`
Get data from component's KVStorage.

```python
# Get a counter value, defaulting to 0 if not found
count = component.get_data('processed_count', 0)
```

#### `increment_counter(key, amount=1)`
Increment a counter in KVStorage.

```python
# Increment a counter
new_count = component.increment_counter('processed_count')
```

#### `decrement_counter(key, amount=1)`
Decrement a counter in KVStorage.

```python
# Decrement a counter
new_count = component.decrement_counter('remaining_items')
```

### Logging and Monitoring

#### `log_custom_event(action, values, container=None)`
Log a custom event with optional container data.

```python
# Log a custom processing event
component.log_custom_event('CUSTOM_PROCESS', {'duration': 5}, container)
```

#### `get_current_time()`
Get the current simulation time.

```python
# Get the current simulation time
current_time = component.get_current_time()
```

#### `track_metric(metric_name, value)`
Track a custom metric by storing it and logging it.

```python
# Track a processing time metric
component.track_metric('processing_time', 5.2)
```

### Error Handling

#### `handle_error(error, container=None)`
Handle and log an error.

```python
# Handle an error that occurred during processing
try:
    # Some processing code
    pass
except Exception as e:
    component.handle_error(e, container)
```

#### `validate_container(container, required_attributes=None)`
Validate a container has required attributes.

```python
# Validate a container has required attributes
is_valid = component.validate_container(
    container,
    {'Water': ['temperature', 'volume']}
)
```

### Utility Functions

#### `format_time(time_value)`
Format a time value for display.

```python
# Format the current time
formatted_time = component.format_time(component.get_current_time())
```

#### `calculate_duration(start_time, end_time)`
Calculate duration between two time points.

```python
# Calculate processing duration
duration = component.calculate_duration(start_time, component.get_current_time())
```

#### `generate_id(prefix="")`
Generate a unique ID.

```python
# Generate a unique ID for a batch
batch_id = component.generate_id('batch-')
```

## Generator Class Helper Methods

These methods are specific to the `Generator` class and are used for generating entities.

### Entity Generation

#### `create_entity(gen_type, attributes=None)`
Create a new entity with specified attributes.

```python
# Create a new Water entity with temperature 25
container = component.create_entity('Water', {'temperature': 25, 'volume': 100})
```

#### `create_batch(gen_type, count, attributes=None)`
Create multiple entities at once.

```python
# Create 5 Water entities with the same attributes
containers = component.create_batch('Water', 5, {'temperature': 25})
```

#### `create_entity_with_variations(gen_type, base_attributes, variations=None)`
Create an entity with random variations of attributes.

```python
# Create a Water entity with temperature varying between 20-30
container = component.create_entity_with_variations(
    'Water',
    {'temperature': 25, 'volume': 100},
    {'temperature': (-5, 5)}
)
```

### Generation Control

#### `set_generation_rate(rate)`
Set the generation rate.

```python
# Set generation rate to 5 entities per time unit
component.set_generation_rate(5)
```

#### `get_generation_rate()`
Get the current generation rate.

```python
# Get the current generation rate
rate = component.get_generation_rate()
```

#### `pause_generation()`
Pause generation.

```python
# Pause generation
component.pause_generation()
```

#### `resume_generation()`
Resume generation.

```python
# Resume generation
component.resume_generation()
```

#### `is_generation_paused()`
Check if generation is currently paused.

```python
# Check if generation is paused
if component.is_generation_paused():
    # Do something
```

#### `stop_generation()`
Stop generation completely.

```python
# Stop generation
component.stop_generation()
```

### Distribution Functions

#### `generate_with_normal_distribution(gen_type, attribute, mean, std_dev)`
Generate an entity with an attribute following a normal distribution.

```python
# Create a Water entity with temperature following normal distribution
container = component.generate_with_normal_distribution('Water', 'temperature', 25, 5)
```

#### `generate_with_exponential_distribution(gen_type, attribute, lambda_val)`
Generate an entity with an attribute following an exponential distribution.

```python
# Create a Customer entity with service_time following exponential distribution
container = component.generate_with_exponential_distribution('Customer', 'service_time', 0.5)
```

#### `generate_with_uniform_distribution(gen_type, attribute, min_val, max_val)`
Generate an entity with an attribute following a uniform distribution.

```python
# Create a Water entity with temperature uniformly distributed between 20 and 30
container = component.generate_with_uniform_distribution('Water', 'temperature', 20, 30)
```

## Resource Class Helper Methods

These methods are specific to the `Resource` class and are used for resource management and processing.

### Resource Management

#### `get_capacity()`
Get the current capacity of the resource.

```python
# Get the current capacity
capacity = component.get_capacity()
```

#### `set_capacity(capacity)`
Set a new capacity for the resource.

```python
# Set a new capacity
component.set_capacity(5)
```

#### `get_utilization()`
Get the current utilization of the resource (0.0 to 1.0).

```python
# Get the current utilization
util = component.get_utilization()
if util > 0.8:
    print("Resource is heavily utilized")
```

#### `is_available()`
Check if the resource has available capacity.

```python
# Check if the resource is available
if component.is_available():
    # Process something
```

### Queue Management

#### `get_queue_length()`
Get the current queue length.

```python
# Get the current queue length
queue_length = component.get_queue_length()
```

#### `get_queue_statistics()`
Get statistics about the queue.

```python
# Get queue statistics
stats = component.get_queue_statistics()
print(f"Average queue length: {stats['avg_length']}")
```

#### `mark_queue_entry(container)`
Mark the time a container enters the queue.

```python
# Mark a container as entering the queue
container = component.mark_queue_entry(container)
```

### Processing Control

#### `process_with_timeout(container, duration)`
Process a container with a specified timeout.

```python
# Process a container for 5 time units
processed_container = yield from component.process_with_timeout(container, 5)
```

#### `process_with_variable_time(container, attribute)`
Process a container with a duration specified by an attribute in the container.

```python
# Process a container using its 'processing_time' attribute
processed_container = yield from component.process_with_variable_time(container, 'processing_time')
```

#### `calculate_processing_metrics(container)`
Calculate processing metrics for a container.

```python
# Calculate processing metrics for a container
metrics = component.calculate_processing_metrics(container)
print(f"Processing time: {metrics['processing_time']}")
```

#### `mark_processing_start(container)`
Mark the time a container starts processing.

```python
# Mark a container as starting processing
container = component.mark_processing_start(container)
```

## Best Practices

When using these helper methods in your custom component functions, consider the following best practices:

1. **Error Handling**: Always handle potential errors, especially when working with containers and attributes.

2. **Logging**: Use the logging methods to track important events and metrics for later analysis.

3. **Resource Management**: Be mindful of resource utilization and queue lengths to avoid bottlenecks.

4. **Container Validation**: Validate containers before processing to ensure they have the required attributes.

5. **Time Management**: Use the time-related methods to control the flow of your simulation.

## Example: Custom Generator Function

Here's an example of a custom generator function that uses several helper methods:

```python
def generate(component):
    # Check if generation is paused
    if component.is_generation_paused():
        yield component.wait(1)  # Wait a bit and try again
        return component.BrakeLoop()

    # Create a new entity with random temperature
    container = component.generate_with_normal_distribution('Water', 'temperature', 25, 5)

    # Add more attributes
    component.set_container_data(container, 'Water', 'volume', 100)
    component.set_container_data(container, 'Water', 'creation_time', component.get_current_time())

    # Track metrics
    component.track_metric('temperature', component.get_container_data(container, 'Water', 'temperature'))

    # Wait a bit before returning the container
    yield component.wait_random(1, 3)

    return container
```

## Example: Custom Resource Function

Here's an example of a custom resource function that uses several helper methods:

```python
def process_water(component, container):
    # Validate the container
    if not component.validate_container(container, {'Water': ['temperature', 'volume']}):
        component.handle_error(ValueError("Invalid container"), container)
        return container

    # Mark the start of processing
    container = component.mark_processing_start(container)

    # Get the temperature
    temperature = component.get_container_data(container, 'Water', 'temperature')

    # Calculate processing time based on temperature
    processing_time = max(1, int(temperature / 10))

    # Process the container
    yield from component.process_with_timeout(container, processing_time)

    # Modify the container data
    component.set_container_data(container, 'Water', 'processed', True)
    component.set_container_data(container, 'Water', 'processing_time', processing_time)

    # Calculate and log metrics
    metrics = component.calculate_processing_metrics(container)
    component.track_metric('processing_time', metrics['processing_time'])

    return container
```

These examples demonstrate how to use the helper methods to simplify your custom component functions and make them more robust.
