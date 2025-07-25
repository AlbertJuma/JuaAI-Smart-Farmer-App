# 🌱 JuaAI Smart Farmer App

An AI-powered Progressive Web Application designed to assist farmers with crop management, disease detection, weather forecasting, and agricultural best practices. Built specifically for farmers in Kenya and East Africa.

## ✨ Features

### 🎯 Core Functionality
- **Crop Disease Detection**: AI-powered image analysis to identify plant diseases (healthy vs diseased)
- **Real-time Analysis**: Flask backend with machine learning model for plant health classification
- **Treatment Recommendations**: Detailed suggestions for diseased crops with urgency levels
- **Weather Forecasting**: Real-time weather data and 5-day forecasts for farming decisions
- **Farming Tips**: Localized agricultural advice and best practices
- **Multi-language Support**: Available in English and Kiswahili
- **Offline Functionality**: Works without internet connection using Progressive Web App technology

### 📱 Progressive Web App (PWA)
- **Installable**: Can be installed on mobile devices and desktops
- **Offline Capable**: Core features work without internet
- **Responsive Design**: Optimized for all screen sizes
- **Fast Loading**: Cached resources for instant access

### 🔬 AI-Powered Analysis
- **Binary Classification**: Healthy vs Diseased plant detection
- **Color Analysis Model**: Lightweight image processing for real-time results
- **Confidence Scoring**: Percentage confidence for analysis results
- **Treatment Suggestions**: Immediate actions, treatment options, and prevention tips
- **Model Flexibility**: Supports both TensorFlow/Keras models and simple color-based analysis

### 🌍 Localized Content
- Farming tips specific to East African agriculture
- Weather data for Kenyan locations
- Bilingual interface (English/Kiswahili)
- Cultural and climate-appropriate advice

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (for Flask backend)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for initial setup
- Camera-enabled device for crop analysis (optional)

### Installation

#### Option 1: Quick Start (Recommended)
1. **Clone the repository**
   ```bash
   git clone https://github.com/AlbertJuma/JuaAI-Smart-Farmer-App.git
   cd JuaAI-Smart-Farmer-App
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the model (optional)**
   ```bash
   python train_simple_model.py
   ```

4. **Start the Flask backend**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000` to access the application

#### Option 2: Frontend Only (PWA Mode)
1. Clone the repository
2. Open `index.html` in a web browser
3. For local server: `python -m http.server 8000`
4. Access via `http://localhost:8000`

### Model Training

The application includes a simple plant health classification model:

#### Quick Model Setup
```bash
# Create and train a simple color-based model
python train_simple_model.py
```

This creates:
- `model_simple.json` - Model configuration
- `model_weights.pkl` - Model weights
- `model_metadata.json` - Model metadata
- `sample_images/` - Test images

#### Advanced Model Training (Optional)
For a more sophisticated TensorFlow model:
```bash
# Install TensorFlow
pip install tensorflow

# Train a CNN model
python train_model.py
```

This creates:
- `model.h5` - Full TensorFlow/Keras model
- Training dataset with synthetic leaf images
- More accurate disease detection

## 🖥️ Flask Backend API

### Endpoints

#### Health Check
```
GET /api/health
```
Returns backend status and model information

#### Image Analysis
```
POST /api/predict
```
Upload image for plant health analysis
- **Input**: Image file (JPG, PNG, etc.)
- **Output**: JSON with prediction, confidence, and treatment suggestions

#### Model Information
```
GET /api/model-info
```
Returns loaded model details and capabilities

### Example Usage

```bash
# Test with curl
curl -X POST -F "image=@path/to/leaf.jpg" http://localhost:5000/api/predict
```

Response format:
```json
{
  "prediction": "diseased",
  "confidence": 75.2,
  "suggestions": {
    "immediate_actions": [
      "Remove affected leaves immediately to prevent spread",
      "Improve air circulation around plants"
    ],
    "treatment_options": [
      "Apply copper-based fungicide",
      "Use bactericide and improve drainage"
    ],
    "prevention_tips": [
      "Choose disease-resistant varieties",
      "Rotate crops annually"
    ],
    "urgency": "Monitor closely and take action within 24-48 hours"
  },
  "model_info": {
    "type": "Color Analysis",
    "version": "1.0.0"
  }
}
```

## 📁 Project Structure

```
JuaAI-Smart-Farmer-App/
├── app.py                      # Flask backend application
├── train_simple_model.py       # Simple model training script
├── train_model.py              # Advanced TensorFlow model training
├── requirements.txt            # Python dependencies
├── model_simple.json           # Simple model configuration
├── model_weights.pkl           # Model weights
├── model_metadata.json         # Model metadata
├── sample_images/              # Test images for demonstration
├── index.html                  # Main application interface
├── styles/
│   └── styles.css             # Application styling and responsive design
├── scripts/
│   ├── app.js                 # Main application logic and UI management
│   ├── weather.js             # Weather API integration and forecasting
│   ├── cropAI.js              # AI disease detection and analysis
│   └── storage.js             # Local storage and data management
├── data/
│   ├── diseases.json          # Crop disease database
│   ├── localTips.json         # Farming tips and advice
│   └── swahili-translation.json # Multilingual support data
├── images/
│   └── sample-leaf.svg        # Sample crop image for demonstration
├── icons/
│   └── app-icon.svg           # Application icon for PWA
├── service-worker.js          # Service worker for offline functionality
├── manifest.json             # PWA manifest for installation
├── README.md                 # Project documentation
└── LICENSE                   # License information
```

## 🛠 Technical Details

### Technologies Used
- **Backend**: Python, Flask, NumPy, Pillow
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **ML Framework**: TensorFlow/Keras (optional), Custom color analysis
- **Architecture**: Progressive Web App (PWA)
- **Storage**: Local Storage, IndexedDB (via abstraction)
- **Offline**: Service Worker for caching and offline functionality
- **Responsive**: CSS Grid and Flexbox for mobile-first design

### Model Architecture

#### Simple Color Analysis Model
- **Input**: RGB images (224x224 pixels)
- **Processing**: Color channel analysis and ratios
- **Classification**: Healthy vs Diseased based on green dominance
- **Confidence**: Calculated from color distribution
- **Performance**: Fast, lightweight, runs in real-time

#### Advanced CNN Model (Optional)
- **Architecture**: Convolutional Neural Network
- **Layers**: Conv2D, MaxPooling, Dropout, Dense
- **Input Shape**: (224, 224, 3)
- **Output**: Binary classification (sigmoid activation)
- **Training**: Synthetic dataset with data augmentation

### Browser Support
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+
- Mobile browsers (iOS Safari, Android Chrome)

### Performance Features
- **Fast Analysis**: Color-based model provides sub-second results
- **Graceful Fallback**: Frontend works with or without backend
- **Error Handling**: Comprehensive error handling and user feedback
- **Loading States**: Visual feedback during analysis
- **Caching**: Aggressive caching for fast load times

## 📊 Plant Health Classification

### Model Capabilities

#### Healthy Crop Detection
- **Indicators**: High green color ratios, uniform coloration
- **Confidence**: 85-95% for clearly healthy plants
- **Recommendations**: Maintenance tips and prevention strategies

#### Disease Detection
- **Indicators**: Brown spots, yellowing, color irregularities
- **Confidence**: 70-90% for diseased plants
- **Treatment**: Immediate actions, treatment options, urgency levels

### Treatment Suggestions

#### For Healthy Crops
- Continue current care routine
- Regular monitoring schedules
- Prevention strategies
- Maintenance best practices

#### For Diseased Crops
- **Immediate Actions**: Urgent steps to prevent spread
- **Treatment Options**: Specific fungicides, bactericides, organic treatments
- **Prevention Tips**: Long-term strategies to avoid recurrence
- **Urgency Levels**: Time-sensitive action recommendations

## 🌐 Multilingual Support

### Supported Languages
- **English**: Default language with full feature support
- **Kiswahili**: Complete translation of interface and content

### Content Localization
- Farming tips translated for local relevance
- Weather information in preferred language
- Disease information and treatments in Kiswahili

## 🔒 Privacy & Data

### Data Collection
- No personal data collection
- Local storage only (no external servers for PWA mode)
- Image analysis performed locally or on your own server

### Privacy Features
- No tracking or analytics
- No third-party data sharing
- Complete user control over data

## 🚀 Deployment

### Local Development
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Train model: `python train_simple_model.py`
4. Start server: `python app.py`
5. Access via `http://localhost:5000`

### Production Deployment

#### Option 1: Full Stack (Flask + Frontend)
```bash
# Install dependencies
pip install -r requirements.txt

# Train model
python train_simple_model.py

# Start production server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Option 2: Static Site (Frontend Only)
1. Upload HTML/CSS/JS files to web server
2. Ensure HTTPS for PWA functionality
3. Configure proper MIME types for service worker
4. Test installation and offline functionality

### Cloud Deployment
- **Heroku**: Use provided `requirements.txt` and `app.py`
- **AWS/GCP**: Deploy Flask app with container or serverless
- **Netlify/Vercel**: Static site deployment for frontend-only mode

## 🤝 Contributing

### Development Guidelines
1. Follow existing code style and structure
2. Test on multiple devices and browsers
3. Ensure offline functionality works
4. Update documentation for new features

### Adding New Features
- Disease detection improvements
- Additional treatment recommendations
- New language support
- Enhanced model accuracy

### Bug Reports
- Provide browser and device information
- Include steps to reproduce
- Screenshots or error messages helpful

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Agricultural experts for farming content
- Open source community for web technologies
- Farmers who inspired this project
- Contributors and testers

## 📞 Support

For support, questions, or feedback:
- Create an issue in the repository
- Check documentation for common questions
- Review troubleshooting section below

## 🔧 Troubleshooting

### Common Issues

#### Backend Not Starting
- Check Python version (3.8+ required)
- Install dependencies: `pip install -r requirements.txt`
- Verify port 5000 is available

#### Model Not Loading
- Run `python train_simple_model.py` to create model files
- Check for `model_simple.json` and `model_weights.pkl`
- Verify file permissions

#### Analysis Not Working
- Check backend is running at `http://localhost:5000`
- Verify image format (JPG, PNG supported)
- Check browser console for errors

#### App Not Installing (PWA)
- Ensure using HTTPS (or localhost for development)
- Check browser PWA support
- Clear cache and try again

#### Offline Features Not Working
- Verify service worker registration
- Check browser console for errors
- Ensure cache is populated

### Performance Issues
- Clear browser cache
- Close other applications
- Check available storage space
- Update browser to latest version

## 🔄 Version History

### v2.0.0 (Current)
- Added Flask backend with machine learning integration
- Real-time plant disease detection
- Detailed treatment recommendations with urgency levels
- Backend API for image analysis
- Simple color-based classification model
- Enhanced error handling and user feedback

### v1.0.0
- Initial release with PWA features
- Frontend-only implementation
- Mock disease detection
- Bilingual support
- Offline capabilities
- Responsive design

## 🗺 Roadmap

### Planned Features
- Real PlantVillage dataset integration
- Enhanced CNN model with transfer learning
- Multi-class disease classification (specific diseases)
- Real weather API integration
- Community features for farmers
- Advanced analytics and reporting

### Long-term Goals
- Expansion to other East African countries
- More language support
- Partnership with agricultural organizations
- Mobile app versions (iOS/Android)
- Integration with IoT sensors