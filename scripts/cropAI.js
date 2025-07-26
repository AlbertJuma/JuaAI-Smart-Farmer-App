// Crop AI analysis module
class CropAI {
    constructor() {
        this.diseases = null;
        this.apiBaseUrl = window.location.origin; // Use same origin for API calls
        this.loadDiseaseDatabase();
    }

    async loadDiseaseDatabase() {
        try {
            this.diseases = await storageManager.getDiseases();
        } catch (error) {
            console.error('Error loading disease database:', error);
            // Use fallback data if file doesn't exist
            this.diseases = this.getFallbackDiseases();
        }
    }

    async analyzeImage(imageFile) {
        try {
            app.showLoading(true);
            
            // First try to use the Flask backend
            const backendResult = await this.analyzeWithBackend(imageFile);
            
            if (backendResult && backendResult.status !== 'error') {
                // Backend analysis successful
                this.displayAnalysisResult(backendResult);
                storageManager.saveAnalysisResult(this.convertBackendResult(backendResult));
                app.showNotification('Crop analysis completed using AI model!', 'success');
                return;
            }
            
            // Fall back to local simulation
            console.warn('Backend analysis failed, falling back to local simulation');
            await this.analyzeWithLocalSimulation(imageFile);
            
        } catch (error) {
            console.error('Analysis error:', error);
            app.showNotification('Error analyzing image. Please try again.', 'error');
        } finally {
            app.showLoading(false);
        }
    }
    
    async analyzeWithBackend(imageFile) {
        try {
            // Check if backend is available
            const healthCheck = await fetch(`${this.apiBaseUrl}/api/health`);
            if (!healthCheck.ok) {
                throw new Error('Backend not available');
            }
            
            // Create form data for image upload
            const formData = new FormData();
            formData.append('image', imageFile);
            
            // Send prediction request
            const response = await fetch(`${this.apiBaseUrl}/api/predict`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Backend error: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.status === 'error') {
                throw new Error(result.error || 'Backend prediction error');
            }
            
            return result;
            
        } catch (error) {
            console.error('Backend analysis error:', error);
            return null;
        }
    }
    
    async analyzeWithLocalSimulation(imageFile) {
        // Simulate AI analysis with realistic delay
        await this.delay(2000 + Math.random() * 3000);
        
        // For demo purposes, simulate analysis based on file properties
        const analysisResult = this.simulateAnalysis(imageFile);
        
        // Store the analysis result
        storageManager.saveAnalysisResult(analysisResult);
        
        // Display the result
        this.displayAnalysisResult(analysisResult);
        
        app.showNotification('Crop analysis completed using local simulation!', 'success');
    }
    
    convertBackendResult(backendResult) {
        // Convert backend result format to local storage format
        const suggestions = backendResult.suggestions || {};
        const recommendations = [];
        
        if (suggestions.immediate_actions) {
            recommendations.push(...suggestions.immediate_actions);
        }
        if (suggestions.treatment_options) {
            recommendations.push(...suggestions.treatment_options);
        }
        if (suggestions.maintenance_tips) {
            recommendations.push(...suggestions.maintenance_tips);
        }
        
        return {
            id: Date.now(),
            date: new Date().toISOString(),
            status: backendResult.prediction === 'healthy' ? 'healthy' : 'disease_detected',
            confidence: backendResult.confidence,
            result: backendResult.prediction === 'healthy' ? 'Healthy Crop' : 'Disease Detected',
            description: this.getDescriptionForPrediction(backendResult.prediction),
            recommendations: recommendations,
            severity: suggestions.severity || (backendResult.prediction === 'healthy' ? 'none' : 'medium'),
            color: this.getSeverityColor(suggestions.severity || (backendResult.prediction === 'healthy' ? 'none' : 'medium')),
            backend_used: true,
            model_info: backendResult.model_info
        };
    }
    
    getDescriptionForPrediction(prediction) {
        if (prediction === 'healthy') {
            return 'Your crop appears to be healthy with no visible signs of disease.';
        } else {
            return 'Disease detected in your crop. Please follow the recommended treatment actions.';
        }
    }

    simulateAnalysis(imageFile) {
        // Simulate AI analysis by randomly selecting from disease database
        if (!this.diseases || this.diseases.length === 0) {
            return this.getHealthyResult();
        }

        // 70% chance of healthy crop, 30% chance of disease detection
        const isHealthy = Math.random() > 0.3;
        
        if (isHealthy) {
            return this.getHealthyResult();
        } else {
            const randomDisease = this.diseases[Math.floor(Math.random() * this.diseases.length)];
            return this.getDiseaseResult(randomDisease);
        }
    }

    getHealthyResult() {
        return {
            id: Date.now(),
            date: new Date().toISOString(),
            status: 'healthy',
            confidence: 85 + Math.random() * 10, // 85-95% confidence
            result: 'Healthy Crop',
            description: 'Your crop appears to be healthy with no visible signs of disease.',
            recommendations: [
                'Continue current care routine',
                'Monitor for any changes in plant health',
                'Maintain proper watering schedule',
                'Ensure adequate nutrition'
            ],
            severity: 'none',
            color: '#4CAF50',
            backend_used: false
        };
    }

    getDiseaseResult(disease) {
        return {
            id: Date.now(),
            date: new Date().toISOString(),
            status: 'disease_detected',
            confidence: 70 + Math.random() * 20, // 70-90% confidence
            result: disease.name,
            description: disease.description,
            recommendations: disease.treatments || [],
            severity: disease.severity || 'medium',
            color: this.getSeverityColor(disease.severity),
            symptoms: disease.symptoms || [],
            prevention: disease.prevention || [],
            backend_used: false
        };
    }

    getSeverityColor(severity) {
        switch (severity) {
            case 'none': return '#4CAF50';
            case 'low': return '#FFC107';
            case 'medium': return '#FF9800';
            case 'high': return '#F44336';
            default: return '#FF9800';
        }
    }

    displayAnalysisResult(result) {
        const resultContainer = document.getElementById('analysis-result');
        const diseaseResultEl = document.getElementById('disease-result');
        const treatmentSuggestionsEl = document.getElementById('treatment-suggestions');

        if (!resultContainer || !diseaseResultEl || !treatmentSuggestionsEl) return;

        // Show the result container
        resultContainer.classList.remove('hidden');

        // Determine if this is a backend result
        const isBackendResult = result.model_info || result.backend_used;
        const confidence = result.confidence || 0;
        const prediction = result.prediction || result.result;
        const description = result.description || this.getDescriptionForPrediction(result.prediction);
        
        // Get color for result
        let resultColor = result.color || this.getSeverityColor(result.severity);
        if (result.prediction === 'healthy' || result.status === 'healthy') {
            resultColor = '#4CAF50';
        }

        // Display main result
        diseaseResultEl.innerHTML = `
            <div class="analysis-main" style="border-left-color: ${resultColor};">
                <div class="result-header">
                    <h4 style="color: ${resultColor};">${prediction}</h4>
                    <span class="confidence">Confidence: ${Math.round(confidence)}%</span>
                </div>
                <p class="result-description">${description}</p>
                ${isBackendResult ? `
                    <div class="model-info">
                        <small><strong>Analysis by:</strong> ${result.model_info?.type || 'AI Model'}</small>
                    </div>
                ` : ''}
                ${result.symptoms && result.symptoms.length > 0 ? `
                    <div class="symptoms-section">
                        <h5>Symptoms:</h5>
                        <ul>
                            ${result.symptoms.map(symptom => `<li>${symptom}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;

        // Display recommendations/suggestions
        this.displaySuggestions(treatmentSuggestionsEl, result);

        // Scroll to result
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    displaySuggestions(container, result) {
        let suggestionsHTML = '';
        
        // Handle backend suggestions format
        if (result.suggestions) {
            const suggestions = result.suggestions;
            
            if (suggestions.immediate_actions && suggestions.immediate_actions.length > 0) {
                suggestionsHTML += `
                    <h4>Immediate Actions:</h4>
                    <div class="recommendations-list">
                        ${suggestions.immediate_actions.map((action, index) => `
                            <div class="recommendation-item urgent">
                                <span class="rec-number">${index + 1}</span>
                                <span class="rec-text">${action}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            if (suggestions.treatment_options && suggestions.treatment_options.length > 0) {
                suggestionsHTML += `
                    <h4>Treatment Options:</h4>
                    <div class="recommendations-list">
                        ${suggestions.treatment_options.map((treatment, index) => `
                            <div class="recommendation-item">
                                <span class="rec-number">${index + 1}</span>
                                <span class="rec-text">${treatment}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            if (suggestions.maintenance_tips && suggestions.maintenance_tips.length > 0) {
                suggestionsHTML += `
                    <h4>Maintenance Tips:</h4>
                    <div class="recommendations-list">
                        ${suggestions.maintenance_tips.map((tip, index) => `
                            <div class="recommendation-item maintenance">
                                <span class="rec-number">${index + 1}</span>
                                <span class="rec-text">${tip}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            if (suggestions.prevention_tips && suggestions.prevention_tips.length > 0) {
                suggestionsHTML += `
                    <div class="prevention-section">
                        <h5>Prevention Tips:</h5>
                        <ul class="prevention-list">
                            ${suggestions.prevention_tips.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
            
            if (suggestions.urgency) {
                suggestionsHTML += `
                    <div class="urgency-notice">
                        <strong>⚠️ Urgency:</strong> ${suggestions.urgency}
                    </div>
                `;
            }
        }
        // Handle local simulation format
        else if (result.recommendations && result.recommendations.length > 0) {
            suggestionsHTML += `
                <h4>Recommendations:</h4>
                <div class="recommendations-list">
                    ${result.recommendations.map((rec, index) => `
                        <div class="recommendation-item">
                            <span class="rec-number">${index + 1}</span>
                            <span class="rec-text">${rec}</span>
                        </div>
                    `).join('')}
                </div>
                ${result.prevention && result.prevention.length > 0 ? `
                    <div class="prevention-section">
                        <h5>Prevention Tips:</h5>
                        <ul class="prevention-list">
                            ${result.prevention.map(tip => `<li>${tip}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
        } else {
            suggestionsHTML = '<p>No specific recommendations needed.</p>';
        }
        
        container.innerHTML = suggestionsHTML;
    }

    getFallbackDiseases() {
        return [
            {
                name: "Leaf Spot Disease",
                description: "Fungal infection causing brown spots on leaves.",
                severity: "medium",
                symptoms: [
                    "Brown or black spots on leaves",
                    "Yellowing around spots",
                    "Leaves may fall prematurely"
                ],
                treatments: [
                    "Remove affected leaves immediately",
                    "Apply copper-based fungicide",
                    "Improve air circulation around plants",
                    "Avoid overhead watering"
                ],
                prevention: [
                    "Water at soil level",
                    "Space plants for good air flow",
                    "Remove plant debris regularly"
                ]
            },
            {
                name: "Powdery Mildew",
                description: "White powdery fungal growth on leaves and stems.",
                severity: "medium",
                symptoms: [
                    "White powdery coating on leaves",
                    "Stunted growth",
                    "Yellowing leaves"
                ],
                treatments: [
                    "Apply neem oil spray",
                    "Use baking soda solution (1 tsp per liter)",
                    "Increase air circulation",
                    "Remove heavily infected parts"
                ],
                prevention: [
                    "Plant in sunny locations",
                    "Avoid overcrowding",
                    "Water early morning"
                ]
            },
            {
                name: "Bacterial Wilt",
                description: "Bacterial infection causing wilting and plant death.",
                severity: "high",
                symptoms: [
                    "Sudden wilting of plants",
                    "Brown streaks in stems",
                    "Plant death within days"
                ],
                treatments: [
                    "Remove infected plants immediately",
                    "Disinfect tools after use",
                    "Apply copper bactericide to healthy plants",
                    "Improve soil drainage"
                ],
                prevention: [
                    "Use disease-resistant varieties",
                    "Rotate crops annually",
                    "Avoid working with wet plants"
                ]
            },
            {
                name: "Aphid Infestation",
                description: "Small insects that suck plant juices and transmit viruses.",
                severity: "low",
                symptoms: [
                    "Small green or black insects on leaves",
                    "Sticky honeydew on leaves",
                    "Curled or yellowing leaves"
                ],
                treatments: [
                    "Spray with insecticidal soap",
                    "Use neem oil",
                    "Introduce beneficial insects",
                    "Rinse with strong water spray"
                ],
                prevention: [
                    "Plant companion crops like marigolds",
                    "Encourage beneficial insects",
                    "Regular monitoring"
                ]
            }
        ];
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Get analysis history
    getAnalysisHistory() {
        return storageManager.getAnalysisHistory();
    }

    // Export analysis data
    exportAnalysisData() {
        const history = this.getAnalysisHistory();
        const dataStr = JSON.stringify(history, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `crop-analysis-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        app.showNotification('Analysis data exported successfully!', 'success');
    }
}

// Add CSS for analysis display
const cropAIStyles = `
    .analysis-main {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin-bottom: 1rem;
    }

    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }

    .result-header h4 {
        margin: 0;
        font-size: 1.3rem;
    }

    .confidence {
        background: rgba(76, 175, 80, 0.1);
        color: #2E7D32;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
    }

    .result-description {
        color: #666;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    .symptoms-section {
        margin-top: 1rem;
    }

    .symptoms-section h5 {
        color: #2E7D32;
        margin-bottom: 0.5rem;
    }

    .symptoms-section ul {
        margin-left: 1rem;
        color: #666;
    }

    .recommendations-list {
        margin: 1rem 0;
    }

    .recommendation-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 0.75rem;
        padding: 0.75rem;
        background: white;
        border-radius: 6px;
        border-left: 3px solid #4CAF50;
    }

    .rec-number {
        background: #4CAF50;
        color: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.75rem;
        flex-shrink: 0;
    }

    .rec-text {
        flex: 1;
        line-height: 1.5;
    }

    .prevention-section {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #e0e0e0;
    }

    .prevention-section h5 {
        color: #2E7D32;
        margin-bottom: 0.5rem;
    }

    .prevention-list {
        margin-left: 1rem;
        color: #666;
    }

    .prevention-list li {
        margin-bottom: 0.25rem;
    }
    
    .model-info {
        margin-top: 1rem;
        padding-top: 0.5rem;
        border-top: 1px solid #e0e0e0;
        color: #666;
        font-size: 0.9rem;
    }
    
    .recommendation-item.urgent {
        border-left-color: #f44336;
        background: #fff3e0;
    }
    
    .recommendation-item.urgent .rec-number {
        background: #f44336;
    }
    
    .recommendation-item.maintenance {
        border-left-color: #4caf50;
        background: #f1f8e9;
    }
    
    .recommendation-item.maintenance .rec-number {
        background: #4caf50;
    }
    
    .urgency-notice {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 6px;
        margin-top: 1rem;
        font-size: 0.9rem;
    }

    @media (max-width: 768px) {
        .result-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }

        .recommendation-item {
            flex-direction: column;
            gap: 0.5rem;
        }

        .rec-number {
            align-self: flex-start;
        }
    }
`;

// Inject crop AI styles
const cropStyleSheet = document.createElement('style');
cropStyleSheet.textContent = cropAIStyles;
document.head.appendChild(cropStyleSheet);

// Initialize crop AI
window.cropAI = new CropAI();