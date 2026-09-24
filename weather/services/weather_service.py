import os
import requests
from datetime import datetime, timezone
from weather.models import WeatherRecord

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.api_url = os.getenv('WEATHER_API_URL')

    def get_current_weather(self, city: str) -> dict:
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'pt_br',
        }

        response = requests.get(
            self.api_url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    def save_current_weather(self, city: str) -> WeatherRecord:
        data = self.get_current_weather(city)

        return WeatherRecord.objects.create(
            city=data['name'],
            country=data['sys']['country'],
            temperature=data['main']['temp'],
            feels_like=data['main']['feels_like'],
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure'],
            weather=data['weather'][0]['description'],
            collected_at=datetime.fromtimestamp(
                data['dt'],
                tz=timezone.utc,
            ),
    )