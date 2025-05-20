"""
Example demonstrating how to use machine learning models in SimZ components.

This file contains example implementations of component event code that uses
the run_ml_model method to incorporate machine learning into simulation logic.
"""

# Example for a Resource component with ML-based processing time prediction
def resource_with_ml_prediction():
    """
    Example event code for a Resource component that uses ML to predict processing times.
    
    This code demonstrates how to use the run_ml_model method to predict
    processing times based on container attributes.
    """
    return """
# Startup method to initialize component variables
def startup(component):
    # Initialize counters
    component.store_data('total_processed', 0)
    component.store_data('ml_predictions', [])
    component.store_data('actual_times', [])
    
# Process Water containers with ML-based processing time prediction
def Water-in(component, container):
    # Get container attributes
    temperature = component.get_container_data(container, 'Water', 'temperature')
    volume = component.get_container_data(container, 'Water', 'volume')
    pressure = component.get_container_data(container, 'Water', 'pressure', 0)  # Default to 0 if not present
    
    # Prepare input data for the model
    features = [temperature, volume, pressure]
    
    # Run the ML model to predict processing time
    start_time = component.get_current_time()
    predicted_time = component.run_ml_model('processing_time_predictor', features)
    
    # Store the prediction
    ml_predictions = component.get_data('ml_predictions', [])
    ml_predictions.append({
        'container_id': container.containerId,
        'time': start_time,
        'predicted_time': predicted_time if predicted_time is not None else 0
    })
    component.store_data('ml_predictions', ml_predictions)
    
    # Use the prediction if available, otherwise use a formula
    if predicted_time is not None:
        processing_time = max(1, predicted_time)  # Ensure minimum processing time
    else:
        # Fallback formula if ML model fails
        processing_time = max(1, temperature / 10 + volume / 100)
    
    # Process the container
    yield from component.process_with_timeout(container, processing_time)
    
    # Record actual processing time
    end_time = component.get_current_time()
    actual_time = end_time - start_time
    
    actual_times = component.get_data('actual_times', [])
    actual_times.append({
        'container_id': container.containerId,
        'time': start_time,
        'actual_time': actual_time
    })
    component.store_data('actual_times', actual_times)
    
    # Increment processed count
    component.increment_counter('total_processed')
    
    return container

# Custom visualization charts for this component
def outputCharts(component):
    # Create a list to hold our charts
    charts = []
    
    # Get ML predictions and actual times
    ml_predictions = component.get_data('ml_predictions', [])
    actual_times = component.get_data('actual_times', [])
    
    # Create a comparison chart if we have both predictions and actual times
    if ml_predictions and actual_times:
        # Match predictions with actual times by container_id
        comparison_data = []
        for pred in ml_predictions:
            container_id = pred['container_id']
            actual = next((a for a in actual_times if a['container_id'] == container_id), None)
            if actual:
                comparison_data.append({
                    'container_id': container_id,
                    'time': pred['time'],
                    'predicted': pred['predicted_time'],
                    'actual': actual['actual_time']
                })
        
        # Create series data for the chart
        if comparison_data:
            series_data = [
                {
                    'name': 'Predicted Time',
                    'data': [{'x': d['time'], 'y': d['predicted']} for d in comparison_data]
                },
                {
                    'name': 'Actual Time',
                    'data': [{'x': d['time'], 'y': d['actual']} for d in comparison_data]
                }
            ]
            
            chart = component.create_line_chart(
                header="ML Prediction vs Actual Processing Time",
                description="Comparison of ML-predicted processing times with actual times",
                series_data=series_data,
                y_axis_label="Processing Time",
                x_axis_label="Simulation Time",
                cols=2,
                rows=1
            )
            charts.append(chart)
    
    # Create a prediction accuracy card
    if ml_predictions and actual_times:
        # Calculate prediction accuracy
        total_error = 0
        count = 0
        
        for pred in ml_predictions:
            container_id = pred['container_id']
            actual = next((a for a in actual_times if a['container_id'] == container_id), None)
            if actual and pred['predicted_time'] > 0:
                error = abs(pred['predicted_time'] - actual['actual_time']) / actual['actual_time']
                total_error += error
                count += 1
        
        if count > 0:
            accuracy = 100 * (1 - (total_error / count))
            card = component.create_card(
                header="ML Prediction Accuracy",
                description="Accuracy of ML processing time predictions",
                value=round(accuracy, 1),
                suffix="%",
                cols=1,
                rows=1
            )
            charts.append(card)
    
    return charts

# Custom visualization tables for this component
def outputTable(component):
    # Create a list to hold our tables
    tables = []
    
    # Get ML predictions and actual times
    ml_predictions = component.get_data('ml_predictions', [])
    actual_times = component.get_data('actual_times', [])
    
    # Create a comparison table if we have both predictions and actual times
    if ml_predictions and actual_times:
        # Match predictions with actual times by container_id
        comparison_data = []
        for pred in ml_predictions:
            container_id = pred['container_id']
            actual = next((a for a in actual_times if a['container_id'] == container_id), None)
            if actual:
                error = abs(pred['predicted_time'] - actual['actual_time'])
                error_percent = 100 * error / actual['actual_time'] if actual['actual_time'] > 0 else 0
                
                comparison_data.append({
                    'container_id': container_id,
                    'simulation_time': pred['time'],
                    'predicted_time': round(pred['predicted_time'], 2),
                    'actual_time': round(actual['actual_time'], 2),
                    'error': round(error, 2),
                    'error_percent': round(error_percent, 1)
                })
        
        if comparison_data:
            table = component.create_table(
                data=comparison_data,
                title="ML Prediction Comparison",
                description="Comparison of ML-predicted processing times with actual times",
                column_order=['container_id', 'simulation_time', 'predicted_time', 'actual_time', 'error', 'error_percent'],
                column_labels={
                    'container_id': 'Container ID',
                    'simulation_time': 'Simulation Time',
                    'predicted_time': 'Predicted Time',
                    'actual_time': 'Actual Time',
                    'error': 'Error',
                    'error_percent': 'Error (%)'
                }
            )
            tables.append(table)
    
    return tables
"""

# Example for a custom Python ML model
def custom_ml_model():
    """
    Example of a custom Python ML model that can be used with the run_ml_model method.
    
    This code demonstrates how to create a simple custom ML model that can be
    saved as a .py file in the models directory.
    """
    return """
# models/processing_time_predictor.py

def predict(input_data):
    """
    Predict processing time based on container attributes.
    
    Args:
        input_data: List containing [temperature, volume, pressure]
        
    Returns:
        Predicted processing time
    """
    # Unpack input features
    temperature, volume, pressure = input_data
    
    # Simple prediction formula
    # In a real model, this would be a trained ML model
    predicted_time = 0.1 * temperature + 0.05 * volume + 0.02 * pressure
    
    return predicted_time
"""

# Example for a Resource component with ML-based routing
def resource_with_ml_routing():
    """
    Example event code for a Resource component that uses ML for routing decisions.
    
    This code demonstrates how to use the run_ml_model method to make routing
    decisions based on container attributes and component state.
    """
    return """
# Startup method to initialize component variables
def startup(component):
    # Initialize counters for different routes
    component.store_data('route_counts', {'fast': 0, 'normal': 0, 'slow': 0})
    
# Process Water containers with ML-based routing
def Water-in(component, container):
    # Get container attributes
    temperature = component.get_container_data(container, 'Water', 'temperature')
    volume = component.get_container_data(container, 'Water', 'volume')
    
    # Get component state
    queue_length = component.get_queue_length()
    utilization = component.get_utilization()
    
    # Prepare input data for the model
    input_data = {
        'temperature': temperature,
        'volume': volume,
        'queue_length': queue_length,
        'utilization': utilization
    }
    
    # Run the ML model to determine routing
    route = component.run_ml_model('container_router', input_data)
    
    # Update route counts
    route_counts = component.get_data('route_counts', {'fast': 0, 'normal': 0, 'slow': 0})
    if route in route_counts:
        route_counts[route] = route_counts[route] + 1
    component.store_data('route_counts', route_counts)
    
    # Process based on the determined route
    if route == 'fast':
        # Fast track processing
        yield from component.process_with_timeout(container, 1)
    elif route == 'normal':
        # Normal processing
        yield from component.process_with_timeout(container, 3)
    else:
        # Slow processing (default)
        yield from component.process_with_timeout(container, 5)
    
    return container
"""

# Usage example
if __name__ == "__main__":
    print("This file contains example implementations of ML-enabled components.")
    print("To use these examples, copy the relevant code into your component's event code.")
    print("\nResource with ML prediction example:")
    print(resource_with_ml_prediction())
    print("\nCustom ML model example:")
    print(custom_ml_model())
    print("\nResource with ML routing example:")
    print(resource_with_ml_routing())
