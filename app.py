#!/usr/bin/env python3
"""
Flask backend for plant leaf classification.
Loads the trained model and provides prediction API.
"""

import os
import json
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import io
import base64

# Try to import TensorFlow
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("Warning: TensorFlow not available. Using mock predictions.")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class PlantClassifier:
    def __init__(self):
        self.model = None
        self.class_names = ['healthy', 'diseased']
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load the trained model."""
        model_path = "model.h5"
        info_path = "model_info.json"
        
        if not TF_AVAILABLE:
            print("TensorFlow not available. Using mock classifier.")
            return
        
        try:
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                print(f"Model loaded from {model_path}")
                
                # Load model info if available
                if os.path.exists(info_path):
                    with open(info_path, 'r') as f:
                        model_info = json.load(f)
                        self.class_names = model_info.get('class_names', self.class_names)
                
                self.model_loaded = True
            else:
                print(f"Model file {model_path} not found. Please train the model first.")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def preprocess_image(self, image):
        """Preprocess image for model prediction."""
        # Resize to model input size
        image = image.resize((224, 224))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array and normalize
        image_array = np.array(image, dtype=np.float32)
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    def predict(self, image):
        """Make prediction on image."""
        if not TF_AVAILABLE or not self.model_loaded:
            return self.mock_prediction()
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            
            # Prepare result
            result = {
                'status': 'success',
                'prediction': self.class_names[predicted_class_idx],
                'confidence': confidence,
                'probabilities': {
                    self.class_names[i]: float(predictions[0][i]) 
                    for i in range(len(self.class_names))
                }
            }
            
            # Add treatment suggestions based on prediction
            if self.class_names[predicted_class_idx] == 'diseased':
                result['treatment'] = self.get_treatment_suggestions()
            else:
                result['treatment'] = self.get_healthy_recommendations()
            
            return result
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                'status': 'error',
                'message': f'Prediction failed: {str(e)}'
            }
    
    def mock_prediction(self):
        """Provide mock prediction when model is not available."""
        import random
        
        # 70% chance of healthy, 30% chance of diseased
        is_healthy = random.random() > 0.3
        
        if is_healthy:
            prediction = 'healthy'
            confidence = 0.85 + random.random() * 0.1  # 85-95%
            treatment = self.get_healthy_recommendations()
        else:
            prediction = 'diseased'
            confidence = 0.75 + random.random() * 0.15  # 75-90%
            treatment = self.get_treatment_suggestions()
        
        return {
            'status': 'success',
            'prediction': prediction,
            'confidence': confidence,
            'probabilities': {
                'healthy': confidence if is_healthy else 1 - confidence,
                'diseased': 1 - confidence if is_healthy else confidence
            },
            'treatment': treatment,
            'note': 'This is a mock prediction for demonstration purposes.'
        }
    
    def get_treatment_suggestions(self):
        """Get treatment suggestions for diseased plants."""
        return {
            'immediate_actions': [
                'Remove affected leaves immediately',
                'Isolate the plant if possible',
                'Inspect other plants for similar symptoms'
            ],
            'treatments': [
                'Apply organic fungicide spray',
                'Improve air circulation around plants',
                'Reduce watering frequency',
                'Apply copper-based treatment'
            ],
            'prevention': [
                'Water at soil level, not on leaves',
                'Ensure proper plant spacing',
                'Remove fallen leaves and debris',
                'Monitor plants regularly'
            ]
        }
    
    def get_healthy_recommendations(self):
        """Get recommendations for healthy plants."""
        return {
            'maintenance': [
                'Continue current care routine',
                'Monitor for any changes',
                'Maintain consistent watering',
                'Ensure adequate nutrition'
            ],
            'prevention': [
                'Regular plant inspection',
                'Proper watering techniques',
                'Good air circulation',
                'Clean gardening tools'
            ],
            'optimization': [
                'Consider companion planting',
                'Monitor soil pH levels',
                'Seasonal care adjustments',
                'Harvest at optimal times'
            ]
        }

# Initialize classifier
classifier = PlantClassifier()

@app.route('/')
def index():
    """Serve the main application."""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('.', filename)

@app.route('/api/predict', methods=['POST'])
def predict():
    """Handle plant disease prediction requests."""
    try:
        # Check if image is provided
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No image provided'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No image selected'
            }), 400
        
        # Read and process image
        try:
            image = Image.open(file.stream)
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Invalid image format: {str(e)}'
            }), 400
        
        # Make prediction
        result = classifier.predict(image)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': classifier.model_loaded,
        'tensorflow_available': TF_AVAILABLE
    })

@app.route('/api/model-info')
def model_info():
    """Get model information."""
    return jsonify({
        'class_names': classifier.class_names,
        'model_loaded': classifier.model_loaded,
        'tensorflow_available': TF_AVAILABLE
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("=== JuaAI Plant Classification Backend ===")
    print(f"Model loaded: {classifier.model_loaded}")
    print(f"TensorFlow available: {TF_AVAILABLE}")
    print(f"Starting server on port {port}...")
    
    app.run(host='0.0.0.0', port=port, debug=debug)