// Weather management module
class WeatherManager {
    constructor() {
        this.apiKey = 'demo'; // In production, use environment variable
        this.baseUrl = 'https://api.openweathermap.org/data/2.5';
        this.cache = new Map();
        this.cacheTimeout = 10 * 60 * 1000; // 10 minutes
    }

    async getWeather(location) {
        try {
            app.showLoading(true);
            
            // Check cache first
            const cached = this.getCachedData(location);
            if (cached) {
                this.displayWeather(cached.current, cached.forecast);
                app.showLoading(false);
                return;
            }

            // For demo purposes, use mock data since we don't have a real API key
            const weatherData = this.getMockWeatherData(location);
            
            // Cache the data
            this.setCachedData(location, weatherData);
            
            this.displayWeather(weatherData.current, weatherData.forecast);
            app.showNotification('Weather data updated successfully!', 'success');
            
        } catch (error) {
            console.error('Weather fetch error:', error);
            app.showNotification('Error fetching weather data. Using sample data.', 'error');
            
            // Show sample data as fallback
            const sampleData = this.getMockWeatherData(location);
            this.displayWeather(sampleData.current, sampleData.forecast);
        } finally {
            app.showLoading(false);
        }
    }

    async getCurrentWeather(location, isDashboard = false) {
        try {
            const cached = this.getCachedData(location);
            let weatherData;
            
            if (cached) {
                weatherData = cached;
            } else {
                weatherData = this.getMockWeatherData(location);
                this.setCachedData(location, weatherData);
            }

            if (isDashboard) {
                this.displayDashboardWeather(weatherData.current);
            } else {
                this.displayWeather(weatherData.current, weatherData.forecast);
            }
            
        } catch (error) {
            console.error('Current weather error:', error);
            if (isDashboard) {
                document.getElementById('current-weather').innerHTML = '<p>Weather data unavailable</p>';
            }
        }
    }

    getMockWeatherData(location) {
        // Generate realistic mock data based on location
        const isKenya = location.toLowerCase().includes('kenya') || location.toLowerCase().includes('nairobi');
        const baseTemp = isKenya ? 25 : 20;
        const variation = Math.random() * 10 - 5;
        
        const conditions = ['sunny', 'partly-cloudy', 'cloudy', 'rainy'];
        const currentCondition = conditions[Math.floor(Math.random() * conditions.length)];
        
        const current = {
            location: location,
            temperature: baseTemp + variation,
            condition: currentCondition,
            humidity: 60 + Math.random() * 30,
            windSpeed: 5 + Math.random() * 15,
            description: this.getWeatherDescription(currentCondition),
            icon: this.getWeatherIcon(currentCondition)
        };

        const forecast = Array.from({length: 5}, (_, i) => ({
            date: new Date(Date.now() + (i + 1) * 24 * 60 * 60 * 1000),
            high: baseTemp + Math.random() * 8,
            low: baseTemp - Math.random() * 8,
            condition: conditions[Math.floor(Math.random() * conditions.length)],
            humidity: 50 + Math.random() * 40
        }));

        return { current, forecast };
    }

    getWeatherDescription(condition) {
        const descriptions = {
            'sunny': 'Clear and sunny',
            'partly-cloudy': 'Partly cloudy',
            'cloudy': 'Overcast',
            'rainy': 'Light rain'
        };
        return descriptions[condition] || 'Mixed conditions';
    }

    getWeatherIcon(condition) {
        const icons = {
            'sunny': '☀️',
            'partly-cloudy': '⛅',
            'cloudy': '☁️',
            'rainy': '🌧️'
        };
        return icons[condition] || '🌤️';
    }

    displayWeather(current, forecast) {
        // Display current weather
        const currentWeatherEl = document.getElementById('current-weather-detail');
        if (currentWeatherEl) {
            currentWeatherEl.innerHTML = `
                <div class="current-weather">
                    <div class="weather-main">
                        <span class="weather-icon">${current.icon}</span>
                        <div class="weather-info">
                            <h3>${current.location}</h3>
                            <div class="temperature">${formatTemperature(current.temperature)}</div>
                            <div class="condition">${current.description}</div>
                        </div>
                    </div>
                    <div class="weather-details">
                        <div class="detail-item">
                            <span>💧 Humidity:</span>
                            <span>${Math.round(current.humidity)}%</span>
                        </div>
                        <div class="detail-item">
                            <span>💨 Wind:</span>
                            <span>${Math.round(current.windSpeed)} km/h</span>
                        </div>
                    </div>
                </div>
            `;
        }

        // Display forecast
        const forecastEl = document.getElementById('forecast-display');
        if (forecastEl && forecast) {
            forecastEl.innerHTML = `
                <div class="forecast-grid">
                    ${forecast.map(day => `
                        <div class="forecast-day">
                            <div class="forecast-date">${formatDate(day.date)}</div>
                            <div class="forecast-icon">${this.getWeatherIcon(day.condition)}</div>
                            <div class="forecast-temps">
                                <span class="high">${formatTemperature(day.high)}</span>
                                <span class="low">${formatTemperature(day.low)}</span>
                            </div>
                            <div class="forecast-humidity">💧 ${Math.round(day.humidity)}%</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    }

    displayDashboardWeather(current) {
        const dashboardWeatherEl = document.getElementById('current-weather');
        if (dashboardWeatherEl) {
            dashboardWeatherEl.innerHTML = `
                <div class="dashboard-weather">
                    <div class="weather-summary">
                        <span class="weather-icon">${current.icon}</span>
                        <div>
                            <div class="temp">${formatTemperature(current.temperature)}</div>
                            <div class="location">${current.location}</div>
                        </div>
                    </div>
                    <div class="weather-condition">${current.description}</div>
                </div>
            `;
        }
    }

    getCachedData(location) {
        const cached = this.cache.get(location);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        return null;
    }

    setCachedData(location, data) {
        this.cache.set(location, {
            data: data,
            timestamp: Date.now()
        });
    }

    getFarmingAdvice(weather) {
        const advice = [];
        
        if (weather.condition === 'rainy') {
            advice.push('Good time for planting rain-fed crops');
            advice.push('Ensure proper drainage in fields');
            advice.push('Monitor for fungal diseases');
        } else if (weather.condition === 'sunny') {
            advice.push('Perfect for harvesting and drying crops');
            advice.push('Ensure adequate irrigation for young plants');
            advice.push('Apply mulch to retain soil moisture');
        } else if (weather.condition === 'cloudy') {
            advice.push('Good conditions for transplanting seedlings');
            advice.push('Monitor soil moisture levels');
        }

        if (weather.humidity > 80) {
            advice.push('High humidity - watch for plant diseases');
        } else if (weather.humidity < 40) {
            advice.push('Low humidity - increase irrigation frequency');
        }

        if (weather.windSpeed > 20) {
            advice.push('Strong winds - protect young plants and check supports');
        }

        return advice;
    }
}

// Add CSS for weather display
const weatherStyles = `
    .current-weather {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .weather-main {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .weather-icon {
        font-size: 3rem;
    }

    .weather-info h3 {
        margin: 0;
        color: #2E7D32;
    }

    .temperature {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
    }

    .condition {
        color: #666;
        font-style: italic;
    }

    .weather-details {
        display: flex;
        gap: 2rem;
        flex-wrap: wrap;
    }

    .detail-item {
        display: flex;
        justify-content: space-between;
        min-width: 120px;
    }

    .forecast-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
    }

    .forecast-day {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }

    .forecast-date {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
    }

    .forecast-icon {
        font-size: 2rem;
        margin: 0.5rem 0;
    }

    .forecast-temps {
        display: flex;
        justify-content: space-between;
        margin: 0.5rem 0;
    }

    .forecast-temps .high {
        font-weight: bold;
        color: #f44336;
    }

    .forecast-temps .low {
        color: #2196F3;
    }

    .forecast-humidity {
        font-size: 0.8rem;
        color: #666;
    }

    .dashboard-weather {
        text-align: center;
    }

    .weather-summary {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }

    .dashboard-weather .temp {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4CAF50;
    }

    .dashboard-weather .location {
        font-size: 0.9rem;
        color: #666;
    }

    .weather-condition {
        color: #666;
        font-style: italic;
    }

    @media (max-width: 768px) {
        .weather-main {
            flex-direction: column;
            text-align: center;
        }

        .weather-details {
            justify-content: center;
        }

        .forecast-grid {
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        }
    }
`;

// Inject weather styles
const styleSheet = document.createElement('style');
styleSheet.textContent = weatherStyles;
document.head.appendChild(styleSheet);

// Initialize weather manager
window.weatherManager = new WeatherManager();