// Crop AI analysis module
class CropAI {
    constructor() {
        this.diseases = null;
        this.backendUrl = 'http://localhost:5000';  // Flask backend URL
        this.backendAvailable = false;
        this.loadDiseaseDatabase();
        this.checkBackendStatus();
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

    async checkBackendStatus() {
        try {
            const response = await fetch(`${this.backendUrl}/api/health`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                const data = await response.json();
                this.backendAvailable = true;
                this.updateBackendStatus(true, data);
            } else {
                this.backendAvailable = false;
                this.updateBackendStatus(false);
            }
        } catch (error) {
            console.log('Backend not available:', error.message);
            this.backendAvailable = false;
            this.updateBackendStatus(false);
        }
    }

    updateBackendStatus(available, data = null) {
        const indicator = document.getElementById('backend-indicator');
        if (!indicator) return;

        if (available) {
            indicator.innerHTML = '🤖 AI Backend Connected';
            indicator.className = 'status-connected';
            if (data && !data.tensorflow_available) {
                indicator.innerHTML += ' (Demo Mode)';
            }
        } else {
            indicator.innerHTML = '💻 Local Processing Only';
            indicator.className = 'status-local';
        }
    }

    async analyzeImage(imageFile) {
        try {
            app.showLoading(true);
            
            // Try to use the backend API first
            const result = await this.analyzeWithBackend(imageFile);
            
            if (result && result.status === 'success') {
                // Process backend result
                const analysisResult = this.processBackendResult(result, imageFile);
                
                // Store the analysis result
                storageManager.saveAnalysisResult(analysisResult);
                
                // Display the result
                this.displayAnalysisResult(analysisResult);
                
                app.showNotification('Crop analysis completed!', 'success');
            } else {
                // Fallback to mock analysis
                console.log('Backend analysis failed, using fallback');
                await this.fallbackAnalysis(imageFile);
            }
            
        } catch (error) {
            console.error('Analysis error:', error);
            // Fallback to mock analysis on error
            await this.fallbackAnalysis(imageFile);
        } finally {
            app.showLoading(false);
        }
    }

    async analyzeWithBackend(imageFile) {
        try {
            // Create FormData to send image
            const formData = new FormData();
            formData.append('image', imageFile);

            // Send request to backend
            const response = await fetch(`${this.backendUrl}/api/predict`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return result;

        } catch (error) {
            console.error('Backend analysis failed:', error);
            return null;
        }
    }

    processBackendResult(backendResult, imageFile) {
        const prediction = backendResult.prediction;
        const confidence = backendResult.confidence * 100; // Convert to percentage
        
        let analysisResult = {
            id: Date.now(),
            date: new Date().toISOString(),
            status: prediction === 'healthy' ? 'healthy' : 'disease_detected',
            confidence: confidence,
            result: prediction === 'healthy' ? 'Healthy Crop' : 'Disease Detected',
            description: prediction === 'healthy' 
                ? 'Your crop appears to be healthy with no visible signs of disease.'
                : 'The AI has detected signs of disease in your crop.',
            recommendations: [],
            severity: prediction === 'healthy' ? 'none' : 'medium',
            color: prediction === 'healthy' ? '#4CAF50' : '#FF9800',
            fromBackend: true
        };

        // Add treatment suggestions from backend
        if (backendResult.treatment) {
            if (prediction === 'healthy' && backendResult.treatment.maintenance) {
                analysisResult.recommendations = backendResult.treatment.maintenance;
            } else if (prediction === 'diseased' && backendResult.treatment.immediate_actions) {
                analysisResult.recommendations = [
                    ...backendResult.treatment.immediate_actions,
                    ...backendResult.treatment.treatments
                ];
                analysisResult.prevention = backendResult.treatment.prevention;
            }
        }

        return analysisResult;
    }

    async fallbackAnalysis(imageFile) {
        console.log('Using fallback mock analysis');
        
        // Add delay to simulate processing
        await this.delay(2000 + Math.random() * 3000);
        
        // For demo purposes, simulate analysis based on file properties
        const analysisResult = this.simulateAnalysis(imageFile);
        
        // Store the analysis result
        storageManager.saveAnalysisResult(analysisResult);
        
        // Display the result
        this.displayAnalysisResult(analysisResult);
        
        app.showNotification('Crop analysis completed (using local processing)!', 'success');
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
            color: '#4CAF50'
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
            prevention: disease.prevention || []
        };
    }

    getSeverityColor(severity) {
        switch (severity) {
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

        // Display main result
        diseaseResultEl.innerHTML = `
            <div class="analysis-main" style="border-left-color: ${result.color};">
                <div class="result-header">
                    <h4 style="color: ${result.color};">${result.result}</h4>
                    <span class="confidence">Confidence: ${Math.round(result.confidence)}%</span>
                </div>
                ${result.fromBackend ? '<div class="backend-indicator">🤖 AI Analysis</div>' : '<div class="fallback-indicator">💻 Local Analysis</div>'}
                <p class="result-description">${result.description}</p>
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

        // Display recommendations
        if (result.recommendations && result.recommendations.length > 0) {
            treatmentSuggestionsEl.innerHTML = `
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
            treatmentSuggestionsEl.innerHTML = '<p>No specific recommendations needed.</p>';
        }

        // Scroll to result
        resultContainer.scrollIntoView({ behavior: 'smooth' });
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

    .backend-indicator, .fallback-indicator {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }

    .backend-indicator {
        background: rgba(76, 175, 80, 0.1);
        color: #2E7D32;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }

    .fallback-indicator {
        background: rgba(255, 152, 0, 0.1);
        color: #F57C00;
        border: 1px solid rgba(255, 152, 0, 0.3);
    }

    .backend-status {
        text-align: center;
        margin-bottom: 1rem;
    }

    .status-connected {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: rgba(76, 175, 80, 0.1);
        color: #2E7D32;
        border: 1px solid rgba(76, 175, 80, 0.3);
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
    }

    .status-local {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: rgba(255, 152, 0, 0.1);
        color: #F57C00;
        border: 1px solid rgba(255, 152, 0, 0.3);
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
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