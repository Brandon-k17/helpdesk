import logging

from django.conf import settings
from django.core.cache import cache

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""

    def __init__(self):
        self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', '8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city="Paris"):
        """Get current weather for a city. Returns weather data or None if error."""
        if not REQUESTS_AVAILABLE:
            logger.warning("Requests library not available. Install with: pip install requests")
            return None

        cache_key = f"weather_{city.lower()}"

        # Clear cached demo data when using a real API key
        if not self.api_key.startswith('8c8c8c8c'):
            cache.delete(cache_key)

        cached_data = cache.get(cache_key)
        if cached_data and not cached_data.get('demo'):
            return cached_data

        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'fr'
            }

            response = requests.get(self.base_url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'temperature': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'].title(),
                    'icon': data['weather'][0]['icon'],
                    'wind_speed': data['wind']['speed'],
                    'pressure': data['main']['pressure']
                }
                cache.set(cache_key, weather_data, 600)
                return weather_data

            elif response.status_code == 401:
                logger.warning("Invalid API key for weather service")
                return {
                    'city': city,
                    'country': 'FR',
                    'temperature': 18,
                    'feels_like': 20,
                    'humidity': 65,
                    'description': 'Nuageux (Clé API en attente)',
                    'icon': '04d',
                    'wind_speed': 3.2,
                    'pressure': 1013,
                    'demo': True,
                    'api_pending': True
                }

            else:
                logger.error(f"Weather API error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Weather API request failed: {e}")
            return None

    def get_weather_icon_url(self, icon_code):
        """Get the full URL for weather icon"""
        return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
