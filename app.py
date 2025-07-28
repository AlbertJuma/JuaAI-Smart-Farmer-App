#!/usr/bin/env python3
"""
Flask Backend for Plant Leaf Classification

This Flask application provides an API endpoint for plant leaf disease detection.
It loads a pre-trained TensorFlow model and provides predictions for uploaded images.
"""

import os
import io
import json
import numpy as np
from PIL import Image
import pickle
import time
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import logging

# Import Gemini AI helper
try:
    from gemini_helper import get_enhanced_explanation
    GEMINI_HELPER_AVAILABLE = True
except ImportError as e:
    GEMINI_HELPER_AVAILABLE = False
    logging.warning(f"Gemini helper not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for frontend communication

# Configuration
MODEL_PATH = 'model.h5'
MODEL_SIMPLE_PATH = 'model_simple.json'
MODEL_WEIGHTS_PATH = 'model_weights.pkl'
MODEL_METADATA_PATH = 'model_metadata.json'
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class PlantClassifier:
    def __init__(self):
        self.model = None
        self.simple_model = None
        self.weights = None
        self.metadata = None
        self.input_shape = (224, 224)
        self.class_names = ['diseased', 'healthy']
        self.load_model()
    
    def load_model(self):
        """Load the trained model and metadata"""
        try:
            # Try to load TensorFlow model first
            if os.path.exists(MODEL_PATH):
                logger.info(f"Loading TensorFlow model from {MODEL_PATH}")
                try:
                    import tensorflow as tf
                    self.model = tf.keras.models.load_model(MODEL_PATH)
                    logger.info("TensorFlow model loaded successfully")
                except ImportError:
                    logger.warning("TensorFlow not available, falling back to simple model")
                except Exception as e:
                    logger.warning(f"Error loading TensorFlow model: {str(e)}")
            
            # Load simple model as fallback
            if os.path.exists(MODEL_SIMPLE_PATH):
                logger.info(f"Loading simple model from {MODEL_SIMPLE_PATH}")
                with open(MODEL_SIMPLE_PATH, 'r') as f:
                    self.simple_model = json.load(f)
                
                if os.path.exists(MODEL_WEIGHTS_PATH):
                    with open(MODEL_WEIGHTS_PATH, 'rb') as f:
                        self.weights = pickle.load(f)
                
                logger.info("Simple model loaded successfully")
            
            # Load metadata if available
            if os.path.exists(MODEL_METADATA_PATH):
                with open(MODEL_METADATA_PATH, 'r') as f:
                    self.metadata = json.load(f)
                    self.input_shape = tuple(self.metadata.get('input_shape', [224, 224, 3])[:2])
                    self.class_names = self.metadata.get('class_names', ['diseased', 'healthy'])
                logger.info("Model metadata loaded successfully")
                
            if not self.model and not self.simple_model:
                logger.warning("No model found. Using mock predictions.")
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model = None
            self.simple_model = None
    
    def preprocess_image(self, image):
        """Preprocess image for model prediction"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image
            image = image.resize(self.input_shape)
            
            # Convert to numpy array and normalize
            img_array = np.array(image) / 255.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def predict(self, image):
        """Make prediction on image"""
        try:
            # Try TensorFlow model first
            if self.model is not None:
                return self.predict_tensorflow(image)
            
            # Fall back to simple model
            elif self.simple_model is not None:
                return self.predict_simple(image)
            
            # Fall back to mock prediction
            else:
                return self.mock_prediction()
                
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return {
                'prediction': 'error',
                'confidence': 0,
                'error': str(e),
                'status': 'error'
            }
    
    def predict_tensorflow(self, image):
        """Make prediction using TensorFlow model"""
        # Preprocess image
        processed_image = self.preprocess_image(image)
        
        # Make prediction
        prediction = self.model.predict(processed_image, verbose=0)
        confidence = float(prediction[0][0])
        
        # Determine class (sigmoid output: >0.5 = healthy, <0.5 = diseased)
        is_healthy = confidence > 0.5
        predicted_class = 'healthy' if is_healthy else 'diseased'
        
        # Adjust confidence for the predicted class
        if is_healthy:
            final_confidence = confidence
        else:
            final_confidence = 1 - confidence
        
        return {
            'prediction': predicted_class,
            'confidence': float(final_confidence * 100),
            'raw_score': float(confidence),
            'status': 'tensorflow',
            'model_type': 'TensorFlow/Keras CNN'
        }
    
    def predict_simple(self, image):
        """Make prediction using simple color-based model"""
        # Convert to RGB and resize
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize(self.input_shape)
        
        # Convert to numpy array
        img_array = np.array(image) / 255.0
        
        # Simple color analysis
        green_ratio = np.mean(img_array[:, :, 1])  # Green channel
        red_ratio = np.mean(img_array[:, :, 0])    # Red channel
        blue_ratio = np.mean(img_array[:, :, 2])   # Blue channel
        
        # Simple health detection based on green dominance
        health_score = green_ratio - (red_ratio + blue_ratio) / 2
        
        # Use weights if available
        if self.weights:
            green_threshold = self.weights.get('green_threshold', 0.4)
            confidence_base = self.weights.get('confidence_base', 0.75)
        else:
            green_threshold = 0.4
            confidence_base = 0.75
        
        if health_score > 0.1:  # Green dominant = healthy
            prediction = 'healthy'
            confidence = min(0.95, confidence_base + health_score)
        else:  # Red/brown dominant = diseased
            prediction = 'diseased'
            confidence = min(0.90, confidence_base + abs(health_score))
        
        return {
            'prediction': prediction,
            'confidence': float(confidence * 100),
            'raw_score': float(health_score),
            'status': 'simple_model',
            'model_type': 'Color Analysis',
            'color_analysis': {
                'green_ratio': float(green_ratio),
                'red_ratio': float(red_ratio),
                'blue_ratio': float(blue_ratio),
                'health_score': float(health_score)
            }
        }
    
    def mock_prediction(self):
        """Provide mock prediction when model is not available"""
        import random
        
        # 70% chance healthy, 30% chance diseased
        is_healthy = random.random() > 0.3
        predicted_class = 'healthy' if is_healthy else 'diseased'
        confidence = random.uniform(75, 95) if is_healthy else random.uniform(70, 90)
        
        return {
            'prediction': predicted_class,
            'confidence': confidence,
            'raw_score': confidence / 100,
            'status': 'mock',
            'model_type': 'Mock Prediction',
            'note': 'Using mock prediction - no model loaded'
        }

# Initialize classifier
classifier = PlantClassifier()

# Treatment suggestions database
TREATMENT_SUGGESTIONS = {
    'diseased': {
        'general': [
            "Remove affected leaves immediately to prevent spread",
            "Improve air circulation around plants",
            "Avoid overhead watering - water at soil level",
            "Apply organic fungicide or neem oil spray",
            "Monitor plant closely for further symptoms"
        ],
        'specific_tips': [
            "For fungal infections: Apply copper-based fungicide",
            "For bacterial issues: Use bactericide and improve drainage", 
            "For viral diseases: Remove infected plants to prevent spread",
            "Ensure proper plant spacing for good air flow",
            "Clean garden tools after working with infected plants"
        ],
        'prevention': [
            "Choose disease-resistant plant varieties",
            "Rotate crops annually to break disease cycles",
            "Maintain proper soil drainage",
            "Avoid working with plants when they're wet",
            "Remove plant debris regularly"
        ]
    },
    'healthy': {
        'maintenance': [
            "Continue current care routine",
            "Monitor regularly for early disease signs",
            "Maintain consistent watering schedule",
            "Ensure adequate nutrition",
            "Keep area around plants clean"
        ],
        'prevention': [
            "Inspect plants weekly for changes",
            "Maintain good garden hygiene",
            "Provide appropriate spacing between plants",
            "Water early morning to allow leaves to dry",
            "Use organic mulch to retain soil moisture"
        ]
    }
}

@app.route('/')
def index():
    """Serve the main application"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': classifier.model is not None or classifier.simple_model is not None,
        'version': '1.0.0'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'status': 'error'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'status': 'error'
            }), 400
        
        # Check file size
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({
                'error': 'File too large. Maximum size is 16MB',
                'status': 'error'
            }), 413
        
        # Reset file pointer
        file.seek(0)
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            return jsonify({
                'error': 'Invalid file type. Please upload an image file',
                'status': 'error'
            }), 400
        
        # Load and process image
        try:
            image = Image.open(io.BytesIO(file.read()))
        except Exception as e:
            return jsonify({
                'error': f'Invalid image file: {str(e)}',
                'status': 'error'
            }), 400
        
        # Make prediction
        result = classifier.predict(image)
        
        if result['status'] == 'error':
            return jsonify(result), 500
        
        # Add treatment suggestions
        prediction_class = result['prediction']
        suggestions = {}
        
        if prediction_class == 'diseased':
            suggestions = {
                'immediate_actions': TREATMENT_SUGGESTIONS['diseased']['general'][:3],
                'treatment_options': TREATMENT_SUGGESTIONS['diseased']['specific_tips'][:3],
                'prevention_tips': TREATMENT_SUGGESTIONS['diseased']['prevention'][:3],
                'severity': 'medium',  # Could be determined by confidence
                'urgency': 'Monitor closely and take action within 24-48 hours'
            }
        elif prediction_class == 'healthy':
            suggestions = {
                'maintenance_tips': TREATMENT_SUGGESTIONS['healthy']['maintenance'][:3],
                'prevention_tips': TREATMENT_SUGGESTIONS['healthy']['prevention'][:3],
                'next_steps': ['Continue monitoring', 'Maintain current care routine']
            }
        
        # Prepare final response
        response = {
            'prediction': prediction_class,
            'confidence': round(result['confidence'], 2),
            'status': result.get('status', 'success'),
            'suggestions': suggestions,
            'timestamp': int(time.time() * 1000),
            'model_info': {
                'type': result.get('model_type', 'Unknown'),
                'version': '1.0.0',
                'classes': classifier.class_names,
                'status': result.get('status', 'unknown')
            }
        }
        
        # Add mock note if using mock predictions
        if result.get('note'):
            response['note'] = result['note']
        
        logger.info(f"Prediction completed: {prediction_class} ({result['confidence']:.1f}%)")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {str(e)}")
        return jsonify({
            'error': 'Internal server error occurred during prediction',
            'status': 'error',
            'details': str(e) if app.debug else None
        }), 500

@app.route('/api/analyze_leaf', methods=['POST'])
def analyze_leaf():
    """
    Enhanced leaf analysis endpoint with Gemini AI explanations
    
    This endpoint provides the same diagnosis functionality as /api/predict
    but includes enhanced explanations powered by Google Gemini AI.
    """
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'status': 'error'
            }), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'status': 'error'
            }), 400
        
        # Check file size
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({
                'error': 'File too large. Maximum size is 16MB',
                'status': 'error'
            }), 413
        
        # Reset file pointer
        file.seek(0)
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            return jsonify({
                'error': 'Invalid file type. Please upload an image file',
                'status': 'error'
            }), 400
        
        # Load and process image
        try:
            image = Image.open(io.BytesIO(file.read()))
        except Exception as e:
            return jsonify({
                'error': f'Invalid image file: {str(e)}',
                'status': 'error'
            }), 400
        
        # Make prediction using existing classifier logic
        result = classifier.predict(image)
        
        if result['status'] == 'error':
            return jsonify(result), 500
        
        # Add treatment suggestions (reusing existing logic)
        prediction_class = result['prediction']
        suggestions = {}
        
        if prediction_class == 'diseased':
            suggestions = {
                'immediate_actions': TREATMENT_SUGGESTIONS['diseased']['general'][:3],
                'treatment_options': TREATMENT_SUGGESTIONS['diseased']['specific_tips'][:3],
                'prevention_tips': TREATMENT_SUGGESTIONS['diseased']['prevention'][:3],
                'severity': 'medium',  # Could be determined by confidence
                'urgency': 'Monitor closely and take action within 24-48 hours'
            }
        elif prediction_class == 'healthy':
            suggestions = {
                'maintenance_tips': TREATMENT_SUGGESTIONS['healthy']['maintenance'][:3],
                'prevention_tips': TREATMENT_SUGGESTIONS['healthy']['prevention'][:3],
                'next_steps': ['Continue monitoring', 'Maintain current care routine']
            }
        
        # Prepare diagnosis result for Gemini AI
        diagnosis_data = {
            'prediction': prediction_class,
            'confidence': round(result['confidence'], 2),
            'status': result.get('status', 'success'),
            'suggestions': suggestions,
            'timestamp': int(time.time() * 1000),
            'model_info': {
                'type': result.get('model_type', 'Unknown'),
                'version': '1.0.0',
                'classes': classifier.class_names,
                'status': result.get('status', 'unknown')
            }
        }
        
        # Generate Gemini AI enhanced explanation
        gemini_ai_response = None
        if GEMINI_HELPER_AVAILABLE:
            try:
                gemini_ai_response = get_enhanced_explanation(diagnosis_data)
                logger.info("Gemini AI explanation generated successfully")
            except Exception as e:
                logger.warning(f"Error generating Gemini AI explanation: {str(e)}")
                gemini_ai_response = "Enhanced explanation temporarily unavailable. Please refer to the standard diagnosis and suggestions."
        else:
            logger.warning("Gemini helper not available, providing fallback explanation")
            gemini_ai_response = "Enhanced AI explanations are not currently available. Please refer to the diagnosis and treatment suggestions provided."
        
        # Prepare final response with both original diagnosis and Gemini AI response
        response = {
            'diagnosis': diagnosis_data,  # Original diagnosis logic preserved
            'gemini_ai_response': gemini_ai_response,  # Enhanced AI explanation
            'enhanced_features': {
                'gemini_ai_available': GEMINI_HELPER_AVAILABLE and gemini_ai_response is not None,
                'explanation_source': 'gemini_ai' if (GEMINI_HELPER_AVAILABLE and gemini_ai_response and 'temporarily unavailable' not in gemini_ai_response) else 'fallback'
            }
        }
        
        # Add mock note if using mock predictions
        if result.get('note'):
            response['diagnosis']['note'] = result['note']
        
        logger.info(f"Leaf analysis completed: {prediction_class} ({result['confidence']:.1f}%) with Gemini AI explanation")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Unexpected error in leaf analysis: {str(e)}")
        return jsonify({
            'error': 'Internal server error occurred during leaf analysis',
            'status': 'error',
            'details': str(e) if app.debug else None
        }), 500

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    return jsonify({
        'model_loaded': classifier.model is not None or classifier.simple_model is not None,
        'input_shape': list(classifier.input_shape) + [3],
        'class_names': classifier.class_names,
        'metadata': classifier.metadata,
        'simple_model': classifier.simple_model is not None,
        'tensorflow_model': classifier.model is not None
    })

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'error': 'File too large. Maximum size is 16MB',
        'status': 'error'
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    print("🌱 Starting JuaAI Plant Leaf Classification Server")
    print("=" * 50)
    print(f"Model loaded: {classifier.model is not None}")
    print(f"Simple model loaded: {classifier.simple_model is not None}")
    print(f"Input shape: {classifier.input_shape}")
    print(f"Classes: {classifier.class_names}")
    print("-" * 50)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    )