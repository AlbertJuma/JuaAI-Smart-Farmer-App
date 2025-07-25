// Local storage management module
class StorageManager {
    constructor() {
        this.storageKeys = {
            ANALYSIS_HISTORY: 'juaai_analysis_history',
            USER_PREFERENCES: 'juaai_user_preferences',
            CACHE: 'juaai_cache'
        };
        this.maxHistoryItems = 50;
        this.init();
    }

    init() {
        // Initialize storage if not exists
        if (!this.getItem(this.storageKeys.ANALYSIS_HISTORY)) {
            this.setItem(this.storageKeys.ANALYSIS_HISTORY, []);
        }
        if (!this.getItem(this.storageKeys.USER_PREFERENCES)) {
            this.setItem(this.storageKeys.USER_PREFERENCES, {
                language: 'en',
                location: 'Nairobi, Kenya',
                notifications: true
            });
        }
    }

    // Generic storage methods
    setItem(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Storage error:', error);
            return false;
        }
    }

    getItem(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Storage retrieval error:', error);
            return null;
        }
    }

    removeItem(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Storage removal error:', error);
            return false;
        }
    }

    // Analysis history methods
    saveAnalysisResult(result) {
        const history = this.getAnalysisHistory();
        
        // Add timestamp if not present
        if (!result.timestamp) {
            result.timestamp = Date.now();
        }
        
        // Add to beginning of array
        history.unshift(result);
        
        // Keep only the most recent items
        if (history.length > this.maxHistoryItems) {
            history.splice(this.maxHistoryItems);
        }
        
        return this.setItem(this.storageKeys.ANALYSIS_HISTORY, history);
    }

    getAnalysisHistory() {
        return this.getItem(this.storageKeys.ANALYSIS_HISTORY) || [];
    }

    getRecentScans(limit = 5) {
        const history = this.getAnalysisHistory();
        return history.slice(0, limit).map(item => ({
            id: item.id,
            date: item.date || new Date(item.timestamp).toISOString(),
            result: item.result,
            status: item.status,
            confidence: item.confidence
        }));
    }

    deleteAnalysisItem(id) {
        const history = this.getAnalysisHistory();
        const filteredHistory = history.filter(item => item.id !== id);
        return this.setItem(this.storageKeys.ANALYSIS_HISTORY, filteredHistory);
    }

    clearAnalysisHistory() {
        return this.setItem(this.storageKeys.ANALYSIS_HISTORY, []);
    }

    // User preferences methods
    getUserPreferences() {
        return this.getItem(this.storageKeys.USER_PREFERENCES) || {
            language: 'en',
            location: 'Nairobi, Kenya',
            notifications: true
        };
    }

    setUserPreference(key, value) {
        const preferences = this.getUserPreferences();
        preferences[key] = value;
        return this.setItem(this.storageKeys.USER_PREFERENCES, preferences);
    }

    // Data file methods (simulating external JSON files)
    async getDiseases() {
        // Try to get from cache first
        const cached = this.getCachedData('diseases');
        if (cached) {
            return cached;
        }

        // In a real app, this would fetch from diseases.json
        // For now, return mock data
        const diseases = [
            {
                id: 1,
                name: "Tomato Late Blight",
                description: "A devastating disease that affects tomatoes and potatoes, caused by the pathogen Phytophthora infestans.",
                severity: "high",
                symptoms: [
                    "Dark brown or black lesions on leaves",
                    "White fuzzy growth on leaf undersides",
                    "Brown spots on fruits",
                    "Rapid plant death in humid conditions"
                ],
                treatments: [
                    "Apply copper-based fungicide immediately",
                    "Remove and destroy infected plants",
                    "Improve air circulation",
                    "Avoid overhead watering",
                    "Apply preventive fungicide sprays"
                ],
                prevention: [
                    "Choose resistant varieties",
                    "Ensure proper spacing for air circulation",
                    "Water at soil level only",
                    "Remove plant debris after harvest",
                    "Rotate crops with non-susceptible plants"
                ],
                crops: ["tomato", "potato"]
            },
            {
                id: 2,
                name: "Maize Streak Virus",
                description: "A viral disease affecting maize crops, transmitted by leafhoppers.",
                severity: "medium",
                symptoms: [
                    "Yellow streaks parallel to leaf veins",
                    "Stunted plant growth",
                    "Reduced kernel formation",
                    "Chlorotic streaking patterns"
                ],
                treatments: [
                    "Control leafhopper vectors with insecticides",
                    "Remove infected plants early",
                    "Use resistant maize varieties",
                    "Apply reflective mulch to deter vectors"
                ],
                prevention: [
                    "Plant resistant varieties",
                    "Early planting to avoid peak vector activity",
                    "Remove volunteer maize plants",
                    "Monitor and control leafhoppers"
                ],
                crops: ["maize", "corn"]
            },
            {
                id: 3,
                name: "Coffee Berry Disease",
                description: "Fungal disease affecting coffee plants, particularly the berries.",
                severity: "high",
                symptoms: [
                    "Dark sunken lesions on berries",
                    "Premature berry drop",
                    "Black spots on leaves and stems",
                    "Reduced coffee quality"
                ],
                treatments: [
                    "Apply copper-based fungicides",
                    "Prune affected branches",
                    "Improve plantation hygiene",
                    "Time fungicide applications with rainfall"
                ],
                prevention: [
                    "Plant resistant coffee varieties",
                    "Maintain proper spacing",
                    "Regular pruning for air circulation",
                    "Remove fallen berries and leaves"
                ],
                crops: ["coffee"]
            },
            {
                id: 4,
                name: "Bean Common Mosaic Virus",
                description: "Viral disease affecting bean plants, causing mosaic patterns on leaves.",
                severity: "medium",
                symptoms: [
                    "Mosaic patterns on leaves",
                    "Leaf curling and distortion",
                    "Stunted plant growth",
                    "Reduced pod formation"
                ],
                treatments: [
                    "Remove infected plants immediately",
                    "Control aphid vectors",
                    "Use virus-free seeds",
                    "Apply insecticides for aphid control"
                ],
                prevention: [
                    "Use certified virus-free seeds",
                    "Plant resistant varieties",
                    "Control aphid populations",
                    "Avoid working with wet plants"
                ],
                crops: ["beans", "common bean"]
            }
        ];

        // Cache the data
        this.setCachedData('diseases', diseases);
        return diseases;
    }

    async getLocalTips(language = 'en') {
        const cacheKey = `tips_${language}`;
        const cached = this.getCachedData(cacheKey);
        if (cached) {
            return cached;
        }

        // Mock tips data
        const tipsData = {
            en: [
                {
                    id: 1,
                    title: "Soil Preparation",
                    description: "Test soil pH before planting. Most crops prefer pH between 6.0-7.0. Add lime to raise pH or sulfur to lower it.",
                    category: "Soil Management"
                },
                {
                    id: 2,
                    title: "Water Management",
                    description: "Water plants early morning or late evening to reduce evaporation. Use drip irrigation for efficient water use.",
                    category: "Irrigation"
                },
                {
                    id: 3,
                    title: "Pest Control",
                    description: "Implement integrated pest management. Use beneficial insects, crop rotation, and organic pesticides when necessary.",
                    category: "Pest Management"
                },
                {
                    id: 4,
                    title: "Crop Rotation",
                    description: "Rotate crops annually to prevent soil depletion and reduce pest buildup. Follow legumes with nitrogen-demanding crops.",
                    category: "Crop Planning"
                },
                {
                    id: 5,
                    title: "Fertilizer Application",
                    description: "Apply organic matter regularly. Use compost, manure, or green manure to improve soil structure and fertility.",
                    category: "Nutrition"
                },
                {
                    id: 6,
                    title: "Harvest Timing",
                    description: "Harvest at the right time for best quality. Most vegetables are best harvested in cool morning hours.",
                    category: "Harvesting"
                }
            ],
            sw: [
                {
                    id: 1,
                    title: "Kutayarisha Udongo",
                    description: "Pima asidi ya udongo kabla ya kupanda. Mazao mengi yanapenda pH kati ya 6.0-7.0. Ongeza chokaa kuongeza pH au sulfuri kupunguza.",
                    category: "Usimamizi wa Udongo"
                },
                {
                    id: 2,
                    title: "Usimamizi wa Maji",
                    description: "Mwagilia mimea asubuhi mapema au jioni ili kupunguza mvukizo. Tumia umwagiliaji wa tone kwa matumizi makuufu ya maji.",
                    category: "Umwagiliaji"
                },
                {
                    id: 3,
                    title: "Kudhibiti Wadudu",
                    description: "Tekeleza usimamizi wa wadudu ulio kamili. Tumia wadudu wazuri, mzunguko wa mazao, na dawa za wadudu za asili.",
                    category: "Usimamizi wa Wadudu"
                },
                {
                    id: 4,
                    title: "Mzunguko wa Mazao",
                    description: "Zungushia mazao kila mwaka ili kuzuia uharibifu wa udongo na kupunguza kuongezeka kwa wadudu.",
                    category: "Mpango wa Mazao"
                },
                {
                    id: 5,
                    title: "Kutumia Mbolea",
                    description: "Tumia vitu vya kikaboni mara kwa mara. Tumia mbolea mbichi, kinyesi, au mbolea ya kijani kuboresha muundo wa udongo.",
                    category: "Lishe"
                },
                {
                    id: 6,
                    title: "Wakati wa Kuvuna",
                    description: "Vuna kwa wakati muafaka kwa ubora bora. Mboga nyingi ni bora kuvunwa wakati wa asubuhi baridi.",
                    category: "Kuvuna"
                }
            ]
        };

        const tips = tipsData[language] || tipsData.en;
        this.setCachedData(cacheKey, tips);
        return tips;
    }

    async getTranslations(language = 'sw') {
        const cacheKey = `translations_${language}`;
        const cached = this.getCachedData(cacheKey);
        if (cached) {
            return cached;
        }

        // Mock translation data
        const translations = {
            dashboard: "Dashibodi",
            weather: "Hali ya Anga",
            crops: "Mazao",
            tips: "Mapendekezo",
            healthy: "Mzuri",
            disease_detected: "Ugonjwa Umegunduliwa",
            analyze: "Changanua",
            loading: "Inapakia...",
            recommendations: "Mapendekezo",
            prevention: "Kinga",
            treatments: "Matibabu"
        };

        this.setCachedData(cacheKey, translations);
        return translations;
    }

    // Cache management
    setCachedData(key, data, expireInMinutes = 60) {
        const cacheData = {
            data: data,
            timestamp: Date.now(),
            expiry: Date.now() + (expireInMinutes * 60 * 1000)
        };
        
        const cache = this.getItem(this.storageKeys.CACHE) || {};
        cache[key] = cacheData;
        return this.setItem(this.storageKeys.CACHE, cache);
    }

    getCachedData(key) {
        const cache = this.getItem(this.storageKeys.CACHE) || {};
        const cacheItem = cache[key];
        
        if (!cacheItem) {
            return null;
        }
        
        // Check if cache has expired
        if (Date.now() > cacheItem.expiry) {
            // Remove expired cache
            delete cache[key];
            this.setItem(this.storageKeys.CACHE, cache);
            return null;
        }
        
        return cacheItem.data;
    }

    clearCache() {
        return this.setItem(this.storageKeys.CACHE, {});
    }

    // Statistics and reporting
    getAnalysisStatistics() {
        const history = this.getAnalysisHistory();
        
        const stats = {
            total: history.length,
            healthy: 0,
            diseased: 0,
            lastAnalysis: null,
            mostCommonDisease: null,
            averageConfidence: 0
        };

        if (history.length === 0) {
            return stats;
        }

        const diseaseCount = {};
        let totalConfidence = 0;

        history.forEach(item => {
            if (item.status === 'healthy') {
                stats.healthy++;
            } else {
                stats.diseased++;
                if (item.result && item.result !== 'Healthy Crop') {
                    diseaseCount[item.result] = (diseaseCount[item.result] || 0) + 1;
                }
            }
            totalConfidence += item.confidence || 0;
        });

        stats.averageConfidence = totalConfidence / history.length;
        stats.lastAnalysis = history[0]?.date || history[0]?.timestamp;

        // Find most common disease
        const diseases = Object.keys(diseaseCount);
        if (diseases.length > 0) {
            stats.mostCommonDisease = diseases.reduce((a, b) => 
                diseaseCount[a] > diseaseCount[b] ? a : b
            );
        }

        return stats;
    }

    // Export/Import functionality
    exportData() {
        const data = {
            analysisHistory: this.getAnalysisHistory(),
            userPreferences: this.getUserPreferences(),
            exportDate: new Date().toISOString(),
            version: '1.0'
        };
        
        return JSON.stringify(data, null, 2);
    }

    importData(jsonData) {
        try {
            const data = JSON.parse(jsonData);
            
            if (data.analysisHistory) {
                this.setItem(this.storageKeys.ANALYSIS_HISTORY, data.analysisHistory);
            }
            
            if (data.userPreferences) {
                this.setItem(this.storageKeys.USER_PREFERENCES, data.userPreferences);
            }
            
            return true;
        } catch (error) {
            console.error('Import error:', error);
            return false;
        }
    }

    // Storage size management
    getStorageUsage() {
        let totalSize = 0;
        
        for (const key in localStorage) {
            if (localStorage.hasOwnProperty(key) && key.startsWith('juaai_')) {
                totalSize += localStorage[key].length;
            }
        }
        
        return {
            used: totalSize,
            usedMB: (totalSize / 1024 / 1024).toFixed(2),
            available: (5 * 1024 * 1024) - totalSize, // Assuming 5MB limit
            availableMB: ((5 * 1024 * 1024 - totalSize) / 1024 / 1024).toFixed(2)
        };
    }

    cleanupOldData(daysToKeep = 30) {
        const cutoffDate = Date.now() - (daysToKeep * 24 * 60 * 60 * 1000);
        const history = this.getAnalysisHistory();
        
        const filteredHistory = history.filter(item => {
            const itemDate = new Date(item.date || item.timestamp).getTime();
            return itemDate > cutoffDate;
        });
        
        return this.setItem(this.storageKeys.ANALYSIS_HISTORY, filteredHistory);
    }
}

// Initialize storage manager
window.storageManager = new StorageManager();