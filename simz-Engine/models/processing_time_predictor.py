"""
Example ML model for predicting processing times in SimZ components.

This is a simple rule-based model that can be used with the run_ml_model method.
In a real application, this would be replaced with a trained machine learning model.
"""

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
