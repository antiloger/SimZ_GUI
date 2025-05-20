# Machine Learning Integration in SimZ

This guide explains how to integrate machine learning models into your SimZ simulation components.

## Overview

SimZ allows you to incorporate machine learning models into your simulation components using the `run_ml_model` method. This enables components to make predictions, classify data, or perform other ML tasks as part of their processing logic.

## Supported Model Types

The `run_ml_model` method supports various types of machine learning models:

1. **Scikit-learn models** (.pkl, .joblib)
2. **TensorFlow models** (saved_model.pb)
3. **PyTorch models** (.pt, .pth)
4. **Custom Python models** (.py)
5. **General pickle models** (.pkl, .pickle)

## Model Directory Structure

By default, models should be placed in a `models` directory in the project root. You can also specify a custom directory when calling the `run_ml_model` method.

Example directory structure:
```
simz-Engine/
├── models/
│   ├── processing_time_predictor.pkl
│   ├── container_classifier.py
│   ├── resource_optimizer/
│   │   └── saved_model.pb
│   └── queue_predictor.pt
├── src/
│   └── ...
└── ...
```

## Using the `run_ml_model` Method

The `run_ml_model` method is available in all component types and can be used as follows:

```python
def process_water(component, container):
    # Get container attributes
    temperature = component.get_container_data(container, 'Water', 'temperature')
    volume = component.get_container_data(container, 'Water', 'volume')
    pressure = component.get_container_data(container, 'Water', 'pressure')
    
    # Prepare input data for the model
    features = [temperature, volume, pressure]
    
    # Run the ML model to predict processing time
    predicted_time = component.run_ml_model('processing_time_predictor', features)
    
    # Use the prediction if available
    if predicted_time is not None:
        # Process the container for the predicted time
        yield from component.process_with_timeout(container, predicted_time)
    else:
        # Fallback to a default processing time
        yield from component.process_with_timeout(container, 5)
    
    return container
```

## Creating Custom Python Models

You can create custom Python models by defining a `.py` file with a `predict` function:

```python
# models/container_classifier.py

def predict(input_data):
    """
    Classify a container based on its attributes.
    
    Args:
        input_data: A dictionary with container attributes
        
    Returns:
        The predicted class (e.g., 'high_priority', 'normal', 'low_priority')
    """
    temperature = input_data.get('temperature', 0)
    volume = input_data.get('volume', 0)
    
    # Simple rule-based classification
    if temperature > 80:
        return 'high_priority'
    elif temperature > 50:
        return 'normal'
    else:
        return 'low_priority'
```

## Using Scikit-learn Models

Here's an example of creating and saving a scikit-learn model for use in SimZ:

```python
# train_model.py
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib

# Generate synthetic training data
X = np.random.rand(100, 3) * 100  # temperature, volume, pressure
y = 2 * X[:, 0] + 0.5 * X[:, 1] + 0.1 * X[:, 2] + np.random.randn(100) * 5  # processing time

# Train a random forest model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Save the model
joblib.dump(model, 'models/processing_time_predictor.joblib')
```

## Using TensorFlow Models

Here's an example of creating and saving a TensorFlow model:

```python
# train_tf_model.py
import tensorflow as tf
import numpy as np

# Generate synthetic training data
X = np.random.rand(100, 3) * 100  # temperature, volume, pressure
y = 2 * X[:, 0] + 0.5 * X[:, 1] + 0.1 * X[:, 2] + np.random.randn(100) * 5  # processing time

# Create a simple neural network
model = tf.keras.Sequential([
    tf.keras.layers.Dense(10, activation='relu', input_shape=(3,)),
    tf.keras.layers.Dense(1)
])

# Compile and train the model
model.compile(optimizer='adam', loss='mse')
model.fit(X, y, epochs=50, verbose=0)

# Save the model
model.save('models/resource_optimizer')
```

## Using PyTorch Models

Here's an example of creating and saving a PyTorch model:

```python
# train_torch_model.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Generate synthetic training data
X = np.random.rand(100, 3) * 100  # temperature, volume, pressure
y = 2 * X[:, 0] + 0.5 * X[:, 1] + 0.1 * X[:, 2] + np.random.randn(100) * 5  # processing time

# Convert to PyTorch tensors
X_tensor = torch.FloatTensor(X)
y_tensor = torch.FloatTensor(y).view(-1, 1)

# Define a simple neural network
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(3, 10)
        self.fc2 = nn.Linear(10, 1)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Create and train the model
model = SimpleNet()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

for epoch in range(100):
    optimizer.zero_grad()
    outputs = model(X_tensor)
    loss = criterion(outputs, y_tensor)
    loss.backward()
    optimizer.step()

# Save the model
torch.save(model, 'models/queue_predictor.pt')
```

## Error Handling

The `run_ml_model` method includes comprehensive error handling:

1. If the model file is not found, it returns `None` and logs an error.
2. If a required ML library is not installed, it returns `None` and logs an error.
3. If the model fails to load or run, it returns `None` and logs an error.

You should always check if the result is `None` before using it in your component logic.

## Logging

The `run_ml_model` method logs the following events:

1. `ML_MODEL_RUN` - When a model execution is attempted
2. `ML_MODEL_RESULT` - When a model execution succeeds
3. `ML_MODEL_ERROR` - When a model execution fails

These logs can be useful for debugging and monitoring your ML-enabled components.

## Best Practices

1. **Input Data Preparation**: Ensure your input data is in the format expected by the model.
2. **Error Handling**: Always check if the model result is `None` before using it.
3. **Fallback Logic**: Provide fallback logic in case the model fails to run.
4. **Model Size**: Keep your models reasonably sized to avoid performance issues.
5. **Model Versioning**: Consider versioning your models to track changes over time.
6. **Testing**: Test your ML-enabled components thoroughly to ensure they work as expected.

## Example: Resource Optimization

Here's a complete example of using an ML model to optimize resource allocation:

```python
def optimize_resource(component, container):
    # Get current resource state
    utilization = component.get_utilization()
    queue_length = component.get_queue_length()
    
    # Get container attributes
    gen_type = container.get_name_in_Data()[0]
    priority = component.get_container_data(container, gen_type, 'priority')
    
    # Prepare input data for the model
    input_data = {
        'utilization': utilization,
        'queue_length': queue_length,
        'priority': priority
    }
    
    # Run the ML model to determine processing strategy
    strategy = component.run_ml_model('resource_optimizer', input_data)
    
    if strategy == 'fast_track':
        # Process with high priority
        yield from component.process_with_timeout(container, 1)
    elif strategy == 'normal':
        # Process with normal priority
        yield from component.process_with_timeout(container, 3)
    else:
        # Default processing
        yield from component.process_with_timeout(container, 5)
    
    return container
```
