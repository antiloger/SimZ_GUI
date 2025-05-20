# Component Visualization Guide

This guide explains how to create custom visualizations for your simulation components using the `outputCharts` and `outputTable` methods.

## Overview

SimZ allows you to define custom visualizations for your components by implementing two special methods in your component's event code:

1. `outputCharts(component)` - Creates charts and cards for your component
2. `outputTable(component)` - Creates tables for your component

These methods are called automatically when the simulation generates visualization data, allowing you to customize how your component's data is displayed.

## Implementing `outputCharts`

The `outputCharts` method should return a list of chart and card configurations. These will be displayed in the simulation dashboard.

### Example

```python
def outputCharts(component):
    """
    Generate custom charts for this component.
    
    Args:
        component: The component instance
        
    Returns:
        List of chart and card configurations
    """
    charts = []
    
    # Get processing times and create a line chart
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
            x_axis_label="Simulation Time"
        )
        charts.append(chart)
    
    # Get action counts and create a pie chart
    action_counts = component.get_action_counts()
    if action_counts:
        chart = component.create_pie_chart(
            header="Action Distribution",
            description="Distribution of actions in the component",
            data=[{'name': action, 'value': count} for action, count in action_counts.items()]
        )
        charts.append(chart)
    
    # Create a card with the total number of processed containers
    if 'OUT' in action_counts:
        card = component.create_card(
            header="Processed Containers",
            description="Total number of containers processed",
            value=action_counts.get('OUT', 0),
            suffix="containers"
        )
        charts.append(card)
    
    return charts
```

## Implementing `outputTable`

The `outputTable` method should return a list of table configurations. These will be displayed in the simulation dashboard.

### Example

```python
def outputTable(component):
    """
    Generate custom tables for this component.
    
    Args:
        component: The component instance
        
    Returns:
        List of table configurations
    """
    tables = []
    
    # Get container metrics and create a table
    container_metrics = component.get_container_metrics()
    if container_metrics:
        table = component.create_table(
            data=container_metrics,
            title="Container Processing Metrics",
            description="Processing and queue times for each container",
            column_order=['container_id', 'types', 'processing_time', 'queue_time'],
            column_labels={
                'container_id': 'Container ID',
                'types': 'Container Types',
                'processing_time': 'Processing Time',
                'queue_time': 'Queue Time'
            }
        )
        tables.append(table)
    
    return tables
```

## Helper Methods

The Component class provides several helper methods to make it easier to create visualizations:

### Chart Creation Helpers

- `create_line_chart(header, description, series_data, ...)` - Create a line chart
- `create_bar_chart(header, description, series_data, ...)` - Create a bar chart
- `create_pie_chart(header, description, data, ...)` - Create a pie chart
- `create_card(header, description, value, ...)` - Create a card with a single value
- `create_table(data, title, description, ...)` - Create a table

### Data Extraction Helpers

- `get_csv_data(csv_scraper)` - Get the CSV scraper for accessing simulation data
- `get_processing_times(csv_scraper)` - Get processing times for this component
- `get_action_counts(csv_scraper)` - Get counts of different actions for this component
- `get_queue_length_timeline(csv_scraper)` - Get queue length timeline for this component
- `get_container_metrics(csv_scraper)` - Get metrics for containers processed by this component

## Resource-Specific Visualizations

For Resource components, you might want to create visualizations that show queue length and utilization:

```python
def outputCharts(component):
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
            x_axis_label="Simulation Time"
        )
        charts.append(chart)
    
    # Create a utilization card if this is a Resource component
    if hasattr(component, 'get_utilization'):
        utilization = component.get_utilization() * 100  # Convert to percentage
        card = component.create_card(
            header="Resource Utilization",
            description="Percentage of time the resource was in use",
            value=round(utilization, 1),
            suffix="%"
        )
        charts.append(card)
    
    return charts
```

## Generator-Specific Visualizations

For Generator components, you might want to create visualizations that show generation rates and counts:

```python
def outputCharts(component):
    charts = []
    
    # Get action counts and create a card with generation count
    action_counts = component.get_action_counts()
    if 'GENERATE' in action_counts:
        card = component.create_card(
            header="Generated Containers",
            description="Total number of containers generated",
            value=action_counts.get('GENERATE', 0),
            suffix="containers"
        )
        charts.append(card)
    
    # Create a generation rate card if available
    generation_rate = component.get_data("generation_rate")
    if generation_rate is not None:
        card = component.create_card(
            header="Generation Rate",
            description="Number of containers generated per time unit",
            value=generation_rate,
            suffix="per time unit"
        )
        charts.append(card)
    
    return charts
```

## Best Practices

1. **Error Handling**: Always include error handling in your visualization methods to prevent failures from affecting the simulation.

2. **Check for Data**: Check if data is available before creating visualizations to avoid empty or meaningless charts.

3. **Use Helper Methods**: Use the provided helper methods to simplify chart creation and data extraction.

4. **Meaningful Descriptions**: Provide clear headers and descriptions for your visualizations to make them understandable.

5. **Appropriate Chart Types**: Choose the appropriate chart type for your data (line charts for time series, pie charts for distributions, etc.).

6. **Consistent Styling**: Maintain consistent styling across your visualizations for a cohesive dashboard.

7. **Performance**: Be mindful of performance when processing large datasets for visualizations.
