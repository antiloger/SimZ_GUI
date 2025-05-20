"""
Example ML model for routing containers in SimZ components.

This is a simple rule-based model that can be used with the run_ml_model method.
In a real application, this would be replaced with a trained machine learning model.
"""

def predict(input_data):
    """
    Determine the routing path for a container based on its attributes and component state.
    
    Args:
        input_data: Dictionary containing container and component attributes
            - temperature: Container temperature
            - volume: Container volume
            - queue_length: Current queue length
            - utilization: Current resource utilization
        
    Returns:
        Routing decision: 'fast', 'normal', or 'slow'
    """
    # Extract input features
    temperature = input_data.get('temperature', 0)
    volume = input_data.get('volume', 0)
    queue_length = input_data.get('queue_length', 0)
    utilization = input_data.get('utilization', 0)
    
    # Simple routing logic
    # In a real model, this would be a trained ML model
    
    # Fast track for high temperature containers when queue is short
    if temperature > 80 and queue_length < 3:
        return 'fast'
    
    # Normal track for medium temperature or when queue is moderate
    if temperature > 50 or (queue_length < 5 and utilization < 0.8):
        return 'normal'
    
    # Slow track for everything else
    return 'slow'
