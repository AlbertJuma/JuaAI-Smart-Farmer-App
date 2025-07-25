# Plant Leaf Classification System

This document provides comprehensive setup and usage instructions for the TensorFlow-based plant leaf classification system integrated into the JuaAI Smart Farmer App.

## 🌱 Overview

The Plant Leaf Classification System enables farmers to upload images of plant leaves and receive AI-powered analysis to determine if the plant is healthy or diseased. The system provides detailed treatment recommendations and prevention tips.

## 🏗️ Architecture

### Backend (Flask + TensorFlow)
- **Framework**: Flask web server with CORS support
- **AI Engine**: Simple feature-based image analysis (designed to be extended with TensorFlow models)
- **Image Processing**: PIL for image handling and analysis
- **API Endpoints**: RESTful API for image classification

### Frontend (HTML/CSS/JavaScript)
- **Interface**: Integrated into existing JuaAI Smart Farmer PWA
- **Upload**: Drag-and-drop and file selection for plant images
- **Display**: Rich results with confidence scores, symptoms, and recommendations
- **Fallback**: Local simulation when backend is unavailable

## 📋 Requirements

### System Requirements
- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for initial setup

### Python Dependencies
```
Flask>=2.0.0
Pillow>=8.0.0
flask-cors>=3.0.0
Werkzeug>=2.0.0
```

For advanced TensorFlow model integration (optional):
```
tensorflow>=2.16.0
numpy>=1.20.0
```

## 🚀 Installation & Setup

### 1. Backend Setup

Navigate to the backend directory:
```bash
cd backend/
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Start the Flask backend:
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup

The frontend is already integrated into the existing JuaAI Smart Farmer App. Start the frontend server:

```bash
# From the root directory
python -m http.server 8000
```

Access the application at `http://localhost:8000`

### 3. Verification

Check backend health:
```bash
curl http://localhost:5000/
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Plant Classifier API is running",
  "version": "1.0.0",
  "model_type": "Simple Feature Analysis"
}
```

## 📱 Usage Instructions

### For Farmers

1. **Access the App**: Open `http://localhost:8000` in your web browser
2. **Navigate to Crop AI**: Click the "Crop AI" tab in the navigation
3. **Upload Image**: 
   - Click "Choose File" or drag and drop an image
   - Supported formats: PNG, JPG, JPEG
   - Maximum file size: 16MB
4. **Analyze**: Click "Analyze Crop" button
5. **Review Results**: 
   - View health classification (Healthy/Diseased)
   - Check confidence score
   - Read symptoms and recommendations
   - Follow treatment advice

### Image Guidelines

- **Quality**: Use clear, well-lit images
- **Focus**: Ensure leaves are the main subject
- **Angle**: Take photos from multiple angles if needed
- **Distance**: Close-up shots work best for disease detection

## 🔧 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### Health Check
```
GET /
```
Returns server status and model information.

#### Image Classification
```
POST /predict
```
**Request**: Multipart form data with 'file' field containing image
**Response**: JSON with classification results

Example response:
```json
{
  "status": "diseased",
  "confidence": 78.5,
  "result": "Disease Detected",
  "description": "The analysis has detected signs of disease in your plant.",
  "recommendations": [
    "Remove affected leaves immediately",
    "Improve air circulation around plants",
    "Apply organic fungicide if available"
  ],
  "symptoms": [
    "Visible discoloration on leaves",
    "Unusual spots or markings"
  ],
  "prevention": [
    "Water at soil level, not on leaves",
    "Remove dead plant material regularly"
  ],
  "severity": "medium",
  "color": "#FF9800"
}
```

#### Model Information
```
GET /model-info
```
Returns information about the loaded model.

## 🧠 Model Information

### Current Implementation
The system currently uses a **feature-based analysis approach** that:
- Analyzes image properties and file characteristics
- Provides simulated AI predictions for demonstration
- Returns realistic confidence scores and recommendations

### TensorFlow Integration (Future Enhancement)
The codebase includes infrastructure for:
- Training custom CNN models with TensorFlow
- Loading and serving trained models
- Real image preprocessing and prediction

### Training Data
For production use, consider these datasets:
- **PlantVillage Dataset**: Open-source plant disease images
- **PlantNet**: Collaborative plant identification
- **Custom Data**: Local plant species and disease patterns

## 🔄 Error Handling

### Backend Failures
- Frontend automatically falls back to local simulation
- User receives warning notification
- Analysis continues with reduced accuracy

### File Upload Errors
- Invalid file formats rejected with clear message
- File size limits enforced
- Timeout handling for large files

### Network Issues
- Automatic retry logic
- Graceful degradation to offline mode
- Status indicators for connection health

## 🛠️ Development

### Adding New Features

1. **New Disease Types**: Update disease database in `data/diseases.json`
2. **Enhanced Analysis**: Integrate TensorFlow models in `backend/app.py`
3. **UI Improvements**: Modify `scripts/cropAI.js` for new features

### Testing

Test the API directly:
```bash
# Test with sample image
curl -X POST -F "file=@sample_leaf.jpg" http://localhost:5000/predict
```

Test frontend integration:
1. Open browser developer tools
2. Upload test images through the interface
3. Check console for API communication logs

### Extending with TensorFlow

The included `train_model.py` provides a foundation for:
- Creating synthetic training datasets
- Building CNN models for binary classification
- Training with real plant disease data
- Saving and loading trained models

## 📊 Performance Considerations

### Backend Optimization
- Image preprocessing caching
- Model inference batching
- Response compression
- Connection pooling

### Frontend Optimization
- Image compression before upload
- Progress indicators for large files
- Cached results for repeated analyses
- Offline capability maintenance

## 🔒 Security & Privacy

### Data Protection
- Images are not permanently stored
- Temporary files cleaned up after processing
- No personal data collection
- Local analysis option for sensitive cases

### Security Measures
- File type validation
- Size limits enforcement
- CORS configuration
- Input sanitization

## 🚀 Deployment

### Local Development
```bash
# Backend
cd backend && python app.py

# Frontend
python -m http.server 8000
```

### Production Deployment

#### Backend (Flask)
```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Frontend
- Deploy to static hosting (Netlify, Vercel, GitHub Pages)
- Ensure HTTPS for PWA functionality
- Configure backend URL in production

#### Docker Deployment (Optional)
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🤝 Contributing

### Code Style
- Follow PEP 8 for Python code
- Use ESLint for JavaScript
- Maintain consistent documentation

### Testing Guidelines
- Test with various image formats
- Verify error handling paths
- Check mobile responsiveness
- Validate API responses

## 📞 Support & Troubleshooting

### Common Issues

**Backend not starting:**
- Check Python version compatibility
- Verify all dependencies installed
- Ensure port 5000 is available

**Frontend not connecting to backend:**
- Confirm backend is running on localhost:5000
- Check CORS configuration
- Verify network connectivity

**Image upload failures:**
- Check file format (PNG, JPG, JPEG only)
- Verify file size under 16MB
- Test with different image types

**Low prediction accuracy:**
- Use higher quality images
- Ensure good lighting
- Try multiple angles of the same plant

### Getting Help
- Check browser console for error messages
- Review backend logs for API issues
- Test with sample images first
- Verify system requirements are met

## 📈 Future Enhancements

### Short Term
- Real TensorFlow model integration
- Expanded disease database
- Mobile camera integration
- Batch image processing

### Long Term
- Multi-language support for recommendations
- Integration with agricultural databases
- Expert consultation features
- Community sharing platform

---

For technical support or feature requests, please create an issue in the repository or contact the development team.