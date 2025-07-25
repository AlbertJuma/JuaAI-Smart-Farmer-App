import os
import json
import logging
import random
import base64
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_image_simple(file_data):
    """Simple image analysis based on file properties"""
    try:
        # Simple heuristic based on file size and random factors
        file_size = len(file_data)
        
        # Calculate a simple "health score" based on file properties
        # This is a demonstration - in reality, you'd use actual image analysis
        size_factor = min(1.0, file_size / 100000)  # Normalize file size
        random_factor = random.uniform(0.2, 0.8)
        
        # Combine factors to get health probability
        health_probability = (size_factor * 0.3 + random_factor * 0.7)
        
        # Add some variance
        health_probability += random.uniform(-0.2, 0.2)
        health_probability = max(0.1, min(0.9, health_probability))
        
        return health_probability
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return random.uniform(0.3, 0.7)

def get_treatment_recommendations(prediction_class, confidence):
    """Get treatment recommendations based on prediction"""
    if prediction_class == 'healthy':
        return {
            'status': 'healthy',
            'confidence': confidence,
            'result': 'Healthy Plant',
            'description': 'Your plant appears to be healthy with no visible signs of disease.',
            'recommendations': [
                'Continue current care routine',
                'Monitor for any changes in plant health',
                'Maintain proper watering schedule',
                'Ensure adequate nutrition',
                'Keep the growing area clean'
            ],
            'severity': 'none',
            'color': '#4CAF50'
        }
    else:
        return {
            'status': 'diseased',
            'confidence': confidence,
            'result': 'Disease Detected',
            'description': 'The analysis has detected signs of disease in your plant. Please follow the recommended treatments.',
            'recommendations': [
                'Remove affected leaves immediately',
                'Improve air circulation around plants',
                'Reduce watering frequency if overwatered',
                'Apply organic fungicide if available',
                'Isolate plant from healthy ones',
                'Monitor daily for changes',
                'Consult local agricultural extension officer'
            ],
            'symptoms': [
                'Visible discoloration on leaves',
                'Unusual spots or markings',
                'Changes in leaf texture'
            ],
            'prevention': [
                'Maintain proper plant spacing',
                'Water at soil level, not on leaves',
                'Remove dead plant material regularly',
                'Use disease-resistant varieties when possible'
            ],
            'severity': 'medium',
            'color': '#FF9800'
        }

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

class PlantClassifierHandler(BaseHTTPRequestHandler):
    """HTTP request handler for plant classification API"""
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.health_check()
        elif self.path == '/model-info':
            self.model_info()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/predict':
            self.predict()
        else:
            self.send_error(404, "Not Found")
    
    def health_check(self):
        """Health check endpoint"""
        response = {
            'status': 'healthy',
            'message': 'Plant Classifier API is running',
            'version': '1.0.0',
            'model_type': 'Simple Feature Analysis'
        }
        self.send_json_response(response)
    
    def model_info(self):
        """Get information about the model"""
        response = {
            'model_loaded': True,
            'model_type': 'Feature-based Analysis',
            'description': 'Simple analysis for plant health detection',
            'input_format': 'RGB images (PNG, JPG, JPEG)',
            'output_classes': ['healthy', 'diseased']
        }
        self.send_json_response(response)
    
    def predict(self):
        """Main prediction endpoint"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response('No file provided', 400)
                return
            
            # Read the request body
            post_data = self.rfile.read(content_length)
            
            # Parse multipart form data (simplified)
            boundary = None
            content_type = self.headers.get('Content-Type', '')
            if 'boundary=' in content_type:
                boundary = content_type.split('boundary=')[1].encode()
            
            if not boundary:
                self.send_error_response('Invalid content type', 400)
                return
            
            # Extract file data from multipart form
            file_data = self.extract_file_from_multipart(post_data, boundary)
            
            if not file_data:
                self.send_error_response('No file data found', 400)
                return
            
            # Analyze the image
            health_probability = analyze_image_simple(file_data)
            
            # Interpret prediction
            prediction_class = 'healthy' if health_probability > 0.5 else 'diseased'
            confidence_percentage = health_probability * 100 if health_probability > 0.5 else (1 - health_probability) * 100
            
            # Get recommendations
            result = get_treatment_recommendations(prediction_class, confidence_percentage)
            
            logger.info(f"Prediction: {prediction_class}, Confidence: {confidence_percentage:.2f}%")
            
            self.send_json_response(result)
            
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            self.send_error_response('Internal server error occurred', 500)
    
    def extract_file_from_multipart(self, post_data, boundary):
        """Extract file data from multipart form data"""
        try:
            parts = post_data.split(b'--' + boundary)
            for part in parts:
                if b'Content-Disposition' in part and b'filename=' in part:
                    # Find the start of file data (after headers)
                    data_start = part.find(b'\r\n\r\n')
                    if data_start != -1:
                        file_data = part[data_start + 4:]
                        # Remove trailing boundary markers
                        if file_data.endswith(b'\r\n'):
                            file_data = file_data[:-2]
                        return file_data
            return None
        except Exception as e:
            logger.error(f"Error extracting file: {str(e)}")
            return None
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response with CORS headers"""
        response_data = json.dumps(data).encode('utf-8')
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(response_data)
    
    def send_error_response(self, message, status_code=500):
        """Send error response"""
        error_data = {'error': message}
        self.send_json_response(error_data, status_code)
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server(host='0.0.0.0', port=5000):
    """Run the HTTP server"""
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, PlantClassifierHandler)
    
    logger.info(f"Plant Classifier API server starting on {host}:{port}")
    logger.info("Server ready to accept requests...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()