// Main application logic
class JuaAIApp {
    constructor() {
        this.currentTab = 'dashboard';
        this.init();
    }

    init() {
        this.setupTabNavigation();
        this.setupEventListeners();
        this.loadDashboard();
        this.loadTips();
    }

    setupTabNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        navButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.getAttribute('data-tab');
                
                // Remove active class from all buttons and tabs
                navButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(tab => tab.classList.remove('active'));
                
                // Add active class to clicked button and corresponding tab
                button.classList.add('active');
                document.getElementById(tabId).classList.add('active');
                
                this.currentTab = tabId;
                
                // Load tab-specific data
                this.loadTabData(tabId);
            });
        });
    }

    setupEventListeners() {
        // Weather button
        const getWeatherBtn = document.getElementById('get-weather');
        if (getWeatherBtn) {
            getWeatherBtn.addEventListener('click', () => {
                const location = document.getElementById('location').value;
                if (location.trim()) {
                    weatherManager.getWeather(location);
                }
            });
        }

        // Crop analysis
        const cropImageInput = document.getElementById('crop-image');
        const analyzeCropBtn = document.getElementById('analyze-crop');
        
        if (cropImageInput) {
            cropImageInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    analyzeCropBtn.disabled = false;
                    this.previewImage(e.target.files[0]);
                }
            });
        }

        if (analyzeCropBtn) {
            analyzeCropBtn.addEventListener('click', () => {
                const file = cropImageInput.files[0];
                if (file) {
                    cropAI.analyzeImage(file);
                }
            });
        }

        // Language selector
        const languageSelect = document.getElementById('language');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.loadTips(e.target.value);
            });
        }

        // Drag and drop for image upload
        this.setupDragAndDrop();
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('crop-image');

        if (uploadArea && fileInput) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, this.preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.style.backgroundColor = 'rgba(76, 175, 80, 0.1)';
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.style.backgroundColor = '';
                }, false);
            });

            uploadArea.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0 && files[0].type.startsWith('image/')) {
                    fileInput.files = files;
                    document.getElementById('analyze-crop').disabled = false;
                    this.previewImage(files[0]);
                }
            }, false);
        }
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    previewImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const uploadContent = document.querySelector('.upload-content');
            uploadContent.innerHTML = `
                <img src="${e.target.result}" alt="Crop preview" style="max-width: 200px; max-height: 200px; border-radius: 8px;">
                <p>Image ready for analysis</p>
            `;
        };
        reader.readAsDataURL(file);
    }

    loadTabData(tabId) {
        switch(tabId) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'weather':
                // Weather data is loaded on button click
                break;
            case 'crops':
                // Crop analysis is triggered by image upload
                break;
            case 'tips':
                this.loadTips();
                break;
        }
    }

    loadDashboard() {
        // Load current weather for dashboard
        weatherManager.getCurrentWeather('Nairobi, Kenya', true);
        
        // Load recent scans from storage
        const recentScans = storageManager.getRecentScans();
        const recentScansEl = document.getElementById('recent-scans');
        
        if (recentScans.length === 0) {
            recentScansEl.innerHTML = '<p>No recent crop scans</p>';
        } else {
            recentScansEl.innerHTML = recentScans.slice(0, 3).map(scan => `
                <div class="scan-item">
                    <small>${new Date(scan.date).toLocaleDateString()}</small>
                    <p><strong>${scan.result}</strong></p>
                </div>
            `).join('');
        }

        // Load quick tips
        this.loadQuickTips();
    }

    async loadQuickTips() {
        try {
            const tips = await storageManager.getLocalTips();
            const quickTipsEl = document.getElementById('quick-tips');
            
            if (tips && tips.length > 0) {
                const randomTip = tips[Math.floor(Math.random() * tips.length)];
                quickTipsEl.innerHTML = `
                    <h4>${randomTip.title}</h4>
                    <p>${randomTip.description}</p>
                `;
            }
        } catch (error) {
            console.error('Error loading quick tips:', error);
        }
    }

    async loadTips(language = 'en') {
        try {
            this.showLoading(true);
            const tips = await storageManager.getLocalTips(language);
            const tipsGrid = document.getElementById('tips-grid');
            
            if (tips && tips.length > 0) {
                tipsGrid.innerHTML = tips.map(tip => `
                    <div class="tip-card">
                        <h4>${tip.title}</h4>
                        <p>${tip.description}</p>
                        <small><strong>Category:</strong> ${tip.category}</small>
                    </div>
                `).join('');
            } else {
                tipsGrid.innerHTML = '<p>No tips available for selected language.</p>';
            }
        } catch (error) {
            console.error('Error loading tips:', error);
            document.getElementById('tips-grid').innerHTML = '<p>Error loading tips. Please try again.</p>';
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(show) {
        const loadingEl = document.getElementById('loading');
        if (show) {
            loadingEl.classList.remove('hidden');
        } else {
            loadingEl.classList.add('hidden');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4CAF50' : '#2196F3'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1001;
            max-width: 300px;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;

        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);

        document.body.appendChild(notification);

        // Remove notification after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTemperature(temp, unit = 'C') {
    return `${Math.round(temp)}°${unit}`;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new JuaAIApp();
});