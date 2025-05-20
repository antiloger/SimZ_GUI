"""
Example demonstrating how to use the visualization capabilities in SimZ components.

This file contains example implementations of the outputCharts and outputTable methods
for different component types.
"""

# Example for a Resource component
def resource_event_code():
    """
    Example event code for a Resource component.
    
    This code demonstrates how to implement the outputCharts and outputTable methods
    for a Resource component.
    """
    return """
# Startup method to initialize component variables
def startup(component):
    # Initialize counters
    component.store_data('total_processed', 0)
    component.store_data('total_queued', 0)
    component.store_data('processing_times', [])
    
# Custom visualization charts for this component
def outputCharts(component):
    # Create a list to hold our charts
    charts = []
    
    # Get queue length timeline and create a chart
    queue_data = component.get_queue_length_timeline()
    if queue_data:
        chart = component.create_line_chart(
            header="Queue Length Over Time",
            description="Queue length throughout the simulation",
            series_data=[{
                'name': 'Queue Length',
                'data': [{'x': entry['time'], 'y': entry['length']} for entry in queue_data]
            }],
            y_axis_label="Queue Length",
            x_axis_label="Simulation Time",
            cols=2,
            rows=1
        )
        charts.append(chart)
    
    # Get processing times and create a chart
    processing_times = component.get_processing_times()
    if processing_times:
        chart = component.create_line_chart(
            header="Processing Times",
            description="Processing times over simulation time",
            series_data=[{
                'name': 'Processing Time',
                'data': [{'x': pt['time'], 'y': pt['duration']} for pt in processing_times]
            }],
            y_axis_label="Time",
            x_axis_label="Simulation Time",
            cols=2,
            rows=1
        )
        charts.append(chart)
    
    # Get action counts and create a pie chart
    action_counts = component.get_action_counts()
    if action_counts:
        chart = component.create_pie_chart(
            header="Action Distribution",
            description="Distribution of actions in the component",
            data=[{'name': action, 'value': count} for action, count in action_counts.items()],
            cols=1,
            rows=1
        )
        charts.append(chart)
    
    # Create a utilization card
    if hasattr(component, 'get_utilization'):
        utilization = component.get_utilization() * 100  # Convert to percentage
        card = component.create_card(
            header="Resource Utilization",
            description="Percentage of time the resource was in use",
            value=round(utilization, 1),
            suffix="%",
            cols=1,
            rows=1
        )
        charts.append(card)
    
    # Create a processed containers card
    if 'OUT' in action_counts:
        card = component.create_card(
            header="Processed Containers",
            description="Total number of containers processed",
            value=action_counts.get('OUT', 0),
            suffix="containers",
            cols=1,
            rows=1
        )
        charts.append(card)
    
    return charts

# Custom visualization tables for this component
def outputTable(component):
    # Create a list to hold our tables
    tables = []
    
    # Get container metrics and create a table
    container_metrics = component.get_container_metrics()
    if container_metrics:
        # Add calculated metrics
        for metric in container_metrics:
            if 'processing_time' in metric and 'queue_time' in metric:
                metric['total_time'] = metric.get('processing_time', 0) + metric.get('queue_time', 0)
                # Calculate efficiency as processing time / total time
                if metric['total_time'] > 0:
                    metric['efficiency'] = round(metric['processing_time'] / metric['total_time'] * 100, 1)
                else:
                    metric['efficiency'] = 0
        
        table = component.create_table(
            data=container_metrics,
            title="Container Processing Metrics",
            description="Processing and queue times for each container",
            column_order=['container_id', 'types', 'processing_time', 'queue_time', 'total_time', 'efficiency'],
            column_labels={
                'container_id': 'Container ID',
                'types': 'Container Types',
                'processing_time': 'Processing Time',
                'queue_time': 'Queue Time',
                'total_time': 'Total Time',
                'efficiency': 'Efficiency (%)'
            }
        )
        tables.append(table)
    
    # Create a summary table with aggregated metrics
    if container_metrics:
        # Calculate summary metrics
        total_containers = len(container_metrics)
        avg_processing_time = sum(m.get('processing_time', 0) for m in container_metrics) / total_containers if total_containers > 0 else 0
        avg_queue_time = sum(m.get('queue_time', 0) for m in container_metrics) / total_containers if total_containers > 0 else 0
        avg_total_time = sum(m.get('total_time', 0) for m in container_metrics) / total_containers if total_containers > 0 else 0
        avg_efficiency = sum(m.get('efficiency', 0) for m in container_metrics) / total_containers if total_containers > 0 else 0
        
        summary_data = [{
            'metric': 'Total Containers',
            'value': total_containers
        }, {
            'metric': 'Average Processing Time',
            'value': round(avg_processing_time, 2)
        }, {
            'metric': 'Average Queue Time',
            'value': round(avg_queue_time, 2)
        }, {
            'metric': 'Average Total Time',
            'value': round(avg_total_time, 2)
        }, {
            'metric': 'Average Efficiency',
            'value': f"{round(avg_efficiency, 1)}%"
        }]
        
        table = component.create_table(
            data=summary_data,
            title="Resource Performance Summary",
            description="Summary of resource performance metrics",
            column_order=['metric', 'value'],
            column_labels={
                'metric': 'Metric',
                'value': 'Value'
            }
        )
        tables.append(table)
    
    return tables

# Process Water containers
def Water-in(component, container):
    # Mark the container as entering the queue
    container = component.mark_queue_entry(container)
    
    # Get the temperature from the container
    temperature = component.get_container_data(container, 'Water', 'temperature')
    
    # Calculate processing time based on temperature
    processing_time = max(1, int(temperature / 10))
    
    # Mark the start of processing
    container = component.mark_processing_start(container)
    
    # Process the container
    yield from component.process_with_timeout(container, processing_time)
    
    # Calculate processing metrics
    metrics = component.calculate_processing_metrics(container)
    
    # Store processing time for later analysis
    processing_times = component.get_data('processing_times', [])
    processing_times.append(metrics['processing_time'])
    component.store_data('processing_times', processing_times)
    
    # Increment processed count
    component.increment_counter('total_processed')
    
    return container
"""

# Example for a Generator component
def generator_event_code():
    """
    Example event code for a Generator component.
    
    This code demonstrates how to implement the outputCharts and outputTable methods
    for a Generator component.
    """
    return """
# Startup method to initialize component variables
def startup(component):
    # Initialize generation rate
    component.set_generation_rate(5)
    component.store_data('generation_times', [])
    component.store_data('temperature_distribution', {})

# Custom visualization charts for this component
def outputCharts(component):
    # Create a list to hold our charts
    charts = []
    
    # Get action counts and create a card with generation count
    action_counts = component.get_action_counts()
    if 'GENERATE' in action_counts:
        card = component.create_card(
            header="Generated Containers",
            description="Total number of containers generated",
            value=action_counts.get('GENERATE', 0),
            suffix="containers",
            cols=1,
            rows=1
        )
        charts.append(card)
    
    # Create a generation rate card
    generation_rate = component.get_data("generation_rate")
    if generation_rate is not None:
        card = component.create_card(
            header="Generation Rate",
            description="Number of containers generated per time unit",
            value=generation_rate,
            suffix="per time unit",
            cols=1,
            rows=1
        )
        charts.append(card)
    
    # Create a temperature distribution chart
    temp_distribution = component.get_data("temperature_distribution", {})
    if temp_distribution:
        # Convert dictionary to list of data points
        data = [{'name': str(temp), 'value': count} for temp, count in temp_distribution.items()]
        chart = component.create_pie_chart(
            header="Temperature Distribution",
            description="Distribution of generated temperatures",
            data=data,
            cols=2,
            rows=1
        )
        charts.append(chart)
    
    # Create a generation timeline chart
    generation_times = component.get_data("generation_times", [])
    if generation_times:
        # Group by time intervals
        time_intervals = {}
        interval_size = 10  # Group by 10 time units
        
        for time in generation_times:
            interval = (time // interval_size) * interval_size
            time_intervals[interval] = time_intervals.get(interval, 0) + 1
        
        # Convert to series data
        series_data = [{
            'name': 'Generation Count',
            'data': [{'x': interval, 'y': count} for interval, count in sorted(time_intervals.items())]
        }]
        
        chart = component.create_bar_chart(
            header="Generation Timeline",
            description="Number of containers generated over time",
            series_data=series_data,
            y_axis_label="Count",
            x_axis_label="Simulation Time",
            cols=2,
            rows=1
        )
        charts.append(chart)
    
    return charts

# Custom visualization tables for this component
def outputTable(component):
    # Create a list to hold our tables
    tables = []
    
    # Create a generation summary table
    action_counts = component.get_action_counts()
    generation_rate = component.get_data("generation_rate", 0)
    temp_distribution = component.get_data("temperature_distribution", {})
    
    # Calculate average temperature
    total_temp = sum(temp * count for temp, count in temp_distribution.items())
    total_count = sum(temp_distribution.values())
    avg_temp = total_temp / total_count if total_count > 0 else 0
    
    summary_data = [{
        'metric': 'Total Generated',
        'value': action_counts.get('GENERATE', 0)
    }, {
        'metric': 'Generation Rate',
        'value': f"{generation_rate} per time unit"
    }, {
        'metric': 'Average Temperature',
        'value': round(avg_temp, 1)
    }, {
        'metric': 'Temperature Range',
        'value': f"{min(temp_distribution.keys()) if temp_distribution else 0} - {max(temp_distribution.keys()) if temp_distribution else 0}"
    }]
    
    table = component.create_table(
        data=summary_data,
        title="Generator Summary",
        description="Summary of generator performance metrics",
        column_order=['metric', 'value'],
        column_labels={
            'metric': 'Metric',
            'value': 'Value'
        }
    )
    tables.append(table)
    
    return tables

# Generate Water containers
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
    temperature = component.get_container_data(container, 'Water', 'temperature')
    
    # Update temperature distribution
    temp_distribution = component.get_data("temperature_distribution", {})
    temp_rounded = round(temperature)
    temp_distribution[temp_rounded] = temp_distribution.get(temp_rounded, 0) + 1
    component.store_data("temperature_distribution", temp_distribution)
    
    # Store generation time
    generation_times = component.get_data("generation_times", [])
    generation_times.append(component.get_current_time())
    component.store_data("generation_times", generation_times)
    
    # Wait according to generation rate
    generation_rate = component.get_generation_rate()
    wait_time = 1 / generation_rate if generation_rate > 0 else 1
    yield component.wait(wait_time)
    
    return container
"""

# Usage example
if __name__ == "__main__":
    print("This file contains example implementations of the outputCharts and outputTable methods.")
    print("To use these examples, copy the relevant code into your component's event code.")
    print("\nResource component example:")
    print(resource_event_code())
    print("\nGenerator component example:")
    print(generator_event_code())
