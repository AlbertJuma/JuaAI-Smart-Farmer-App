# 🌱 JuaAI Smart Farmer App

An AI-powered Progressive Web Application designed to assist farmers with crop management, disease detection, weather forecasting, and agricultural best practices. Built specifically for farmers in Kenya and East Africa.

## ✨ Features

### 🎯 Core Functionality
- **AI-Powered Crop Disease Detection**: Real machine learning model trained to classify plant leaves as healthy or diseased
- **Intelligent Analysis**: TensorFlow/Keras model with confidence scoring and treatment recommendations
- **Flexible Processing**: Seamless fallback between AI backend and local processing
- **Weather Forecasting**: Real-time weather data and 5-day forecasts for farming decisions
- **Farming Tips**: Localized agricultural advice and best practices
- **Multi-language Support**: Available in English and Kiswahili
- **Offline Functionality**: Works without internet connection using Progressive Web App technology

### 🤖 AI-Powered Disease Detection
- **Machine Learning Model**: Trained TensorFlow/Keras model for accurate plant health assessment
- **Real-time Analysis**: Upload photos for instant disease detection
- **Treatment Recommendations**: Specific treatment plans based on detected conditions
- **Prevention Tips**: Proactive advice to prevent common agricultural issues
- **Confidence Scoring**: Transparent confidence levels for all predictions
- **Fallback Processing**: Continues to work even when AI backend is unavailable

### 📱 Progressive Web App (PWA)
- **Installable**: Can be installed on mobile devices and desktops
- **Offline Capable**: Core features work without internet
- **Responsive Design**: Optimized for all screen sizes
- **Fast Loading**: Cached resources for instant access

### 🌍 Localized Content
- Farming tips specific to East African agriculture
- Weather data for Kenyan locations
- Bilingual interface (English/Kiswahili)
- Cultural and climate-appropriate advice

## 🚀 Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Python 3.8+ (for AI backend)
- Internet connection for initial setup
- Camera-enabled device for crop analysis (optional)

### Installation Options

#### Option 1: Quick Start (Frontend Only)
1. Open your web browser
2. Navigate to the app URL
3. The app will load with local processing capabilities

#### Option 2: Full AI Setup (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AlbertJuma/JuaAI-Smart-Farmer-App.git
   cd JuaAI-Smart-Farmer-App
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare Dataset (Optional)**
   ```bash
   python prepare_dataset.py
   ```

4. **Train Model (Optional)**
   ```bash
   python train_model.py
   ```

5. **Start Flask Backend**
   ```bash
   python app.py
   ```

6. **Access the Application**
   Open your browser and go to `http://localhost:5000`

#### Option 3: Install as PWA
1. Open the app in your browser
2. Look for "Install App" or "Add to Home Screen" option
3. Follow the browser prompts to install
4. Access the app from your device's home screen

### Basic Usage

#### 1. Dashboard
- View current weather conditions
- See recent crop analyses
- Access quick farming tips

#### 2. Weather Forecast
- Enter your location
- Get current weather and 5-day forecast
- Make informed farming decisions

#### 3. Crop Disease Detection
- Take or upload a photo of your crop
- Wait for AI analysis (2-5 seconds)
- Review disease identification and treatment recommendations
- Get specific treatment plans and prevention tips

#### 4. Farming Tips
- Browse categorized agricultural advice
- Switch between English and Kiswahili
- Find tips specific to your farming needs

## 🔧 AI Model Training

### Dataset Preparation
The app includes a dataset preparation script that creates sample data for training:

```bash
python prepare_dataset.py
```

This script:
- Creates a structured dataset with healthy and diseased plant images
- Preprocesses images for optimal model performance
- Generates sample data for demonstration purposes

### Model Training
Train your own plant disease classification model:

```bash
python train_model.py
```

The training script:
- Creates a CNN model using TensorFlow/Keras
- Trains on the prepared dataset
- Saves the model as `model.h5` for use by the Flask backend
- Includes data augmentation and validation

### Model Architecture
- **Input**: 224x224x3 RGB images
- **Architecture**: Convolutional Neural Network (CNN)
- **Output**: Binary classification (healthy/diseased)
- **Features**: Data augmentation, dropout for regularization
- **Format**: Saved as HDF5 (.h5) format

## 📁 Project Structure

```
JuaAI-Smart-Farmer-App/
├── index.html                 # Main application interface
├── app.py                     # Flask backend for AI predictions
├── requirements.txt           # Python dependencies
├── prepare_dataset.py         # Dataset preparation script
├── train_model.py            # Model training script
├── model.h5                  # Trained TensorFlow model
├── model_info.json          # Model metadata
├── styles/
│   └── styles.css            # Application styling and responsive design
├── scripts/
│   ├── app.js                # Main application logic and UI management
│   ├── weather.js            # Weather API integration and forecasting
│   ├── cropAI.js             # AI disease detection and analysis
│   └── storage.js            # Local storage and data management
├── data/
│   ├── diseases.json         # Crop disease database
│   ├── localTips.json        # Farming tips and advice
│   └── swahili-translation.json # Multilingual support data
├── dataset/                  # Training dataset (created by prepare_dataset.py)
│   ├── healthy/              # Healthy plant images
│   ├── diseased/             # Diseased plant images
│   └── processed/            # Preprocessed images for training
├── images/
│   └── sample-leaf.svg       # Sample crop image for demonstration
├── icons/
│   └── app-icon.svg          # Application icon for PWA
├── service-worker.js         # Service worker for offline functionality
├── manifest.json             # PWA manifest for installation
├── README.md                 # Project documentation
└── LICENSE                   # License information
```

## 🛠 Technical Details

### Technologies Used
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Flask (Python web framework)
- **AI/ML**: TensorFlow 2.x, Keras for deep learning
- **Image Processing**: PIL (Python Imaging Library), OpenCV
- **Architecture**: Progressive Web App (PWA) with REST API backend
- **Storage**: Local Storage, IndexedDB (via abstraction)
- **Offline**: Service Worker for caching and offline functionality
- **Responsive**: CSS Grid and Flexbox for mobile-first design

### AI Model Details
- **Framework**: TensorFlow/Keras
- **Model Type**: Convolutional Neural Network (CNN)
- **Input Size**: 224x224 pixels, RGB images
- **Classes**: Binary classification (healthy/diseased)
- **Training**: Includes data augmentation and validation
- **Deployment**: Served via Flask REST API

### API Endpoints
- `GET /api/health` - Backend health check
- `POST /api/predict` - Image upload and disease prediction
- `GET /api/model-info` - Model information and capabilities

### Browser Support
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+
- Mobile browsers (iOS Safari, Android Chrome)

### Performance Features
- **Lazy Loading**: Images and content loaded as needed
- **Caching**: Aggressive caching for fast load times
- **Compression**: Optimized assets for faster downloads
- **Progressive Enhancement**: Core functionality works on all devices

## 📊 Data Sources

### Disease Database
- Comprehensive database of common East African crop diseases
- Symptoms, treatments, and prevention strategies
- Region-specific disease information

### Weather Integration
- Mock weather API for demonstration
- Real-time weather data (when API key provided)
- Location-based forecasting

### Farming Tips
- Curated content from agricultural experts
- Localized advice for Kenyan farming conditions
- Seasonal and climate-appropriate recommendations

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
- Local storage only (no external servers)
- Image analysis performed locally (mock AI)

### Privacy Features
- No tracking or analytics
- No third-party data sharing
- Complete user control over data

## 🚀 Deployment

### Local Development
1. Clone the repository
2. Open `index.html` in a web browser
3. For local server: `python -m http.server 8000`
4. Access via `http://localhost:8000`

### Production Deployment
1. Upload files to web server
2. Ensure HTTPS for PWA functionality
3. Configure proper MIME types for service worker
4. Test installation and offline functionality

### CDN Deployment
- Compatible with static site hosting (Netlify, Vercel, GitHub Pages)
- No server-side processing required
- Automatic HTTPS and global distribution

## 🤝 Contributing

### Development Guidelines
1. Follow existing code style and structure
2. Test on multiple devices and browsers
3. Ensure offline functionality works
4. Update documentation for new features

### Feature Requests
- Submit issues with detailed descriptions
- Include use cases and target users
- Consider localization requirements

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

#### App Not Installing
- Ensure using HTTPS
- Check browser PWA support
- Clear cache and try again

#### Offline Features Not Working
- Verify service worker registration
- Check browser console for errors
- Ensure cache is populated

#### Image Analysis Not Working
- Check file format support (JPG, PNG, SVG)
- Ensure camera permissions granted
- Try different image sizes

#### Weather Data Not Loading
- Verify internet connection
- Check location permissions
- Try different location formats

### Performance Issues
- Clear browser cache
- Close other applications
- Check available storage space
- Update browser to latest version

## 🔄 Version History

### v1.0.0 (Current)
- Initial release with core features
- PWA functionality
- Bilingual support
- Offline capabilities
- Responsive design

## 🗺 Roadmap

### Planned Features
- Real weather API integration
- Enhanced AI disease detection
- Community features for farmers
- Advanced analytics and reporting
- Integration with local agricultural services

### Long-term Goals
- Expansion to other East African countries
- More language support
- Partnership with agricultural organizations
- Mobile app versions (iOS/Android)