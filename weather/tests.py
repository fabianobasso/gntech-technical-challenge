import requests
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import Mock, patch
from weather.services.weather_service import WeatherService
from weather.models import WeatherRecord

class WeatherServiceTest(TestCase):
    @patch('weather.services.weather_service.requests.get')
    def test_get_current_weather(self, mock_get):
        response = Mock()
        response.json.return_value = {
            'name': 'Florianópolis',
            'sys': {
                'country': 'BR',
            },
            'main': {
                'temp': 20.5,
                'feels_like': 20.1,
                'humidity': 75,
                'pressure': 1015,
            },
            'weather': [
                {
                    'description': 'céu limpo',
                }
            ],
            'dt': 1790279483,
        }
        response.raise_for_status.return_value = None

        mock_get.return_value = response

        service = WeatherService()

        data = service.get_current_weather('Florianopolis,BR')

        self.assertEqual(data['name'], 'Florianópolis')
        self.assertEqual(data['sys']['country'], 'BR')
        self.assertEqual(data['main']['temp'], 20.5)

        mock_get.assert_called_once_with(
            service.api_url,
            params={
                'q': 'Florianopolis,BR',
                'appid': service.api_key,
                'units': 'metric',
                'lang': 'pt_br',
            },
            timeout=10,
        )
    
    @patch.object(WeatherService, 'get_current_weather')
    def test_save_current_weather(self, mock_get_current_weather):
        mock_get_current_weather.return_value = {
            'name': 'Florianópolis',
            'sys': {
                'country': 'BR',
            },
            'main': {
                'temp': 20.5,
                'feels_like': 20.1,
                'humidity': 75,
                'pressure': 1015,
            },
            'weather': [
                {
                    'description': 'céu limpo',
                }
            ],
            'dt': 1790279483,
        }

        service = WeatherService()

        record = service.save_current_weather('Florianopolis,BR')

        self.assertEqual(record.city, 'Florianópolis')
        self.assertEqual(record.country, 'BR')
        self.assertEqual(float(record.temperature), 20.5)
        self.assertEqual(float(record.feels_like), 20.1)
        self.assertEqual(record.humidity, 75)
        self.assertEqual(record.pressure, 1015)
        self.assertEqual(record.weather, 'céu limpo')

        self.assertEqual(WeatherRecord.objects.count(), 1)
        saved_record = WeatherRecord.objects.get()
        self.assertEqual(saved_record.city, 'Florianópolis')
        self.assertEqual(saved_record.country, 'BR')
        
        mock_get_current_weather.assert_called_once_with(
            'Florianopolis,BR'
        )

class WeatherApiTest(APITestCase):
    def setUp(self):
        self.weather_data = {
            'name': 'Florianópolis',
            'sys': {
                'country': 'BR',
            },
            'main': {
                'temp': 20.5,
                'feels_like': 20.1,
                'humidity': 75,
                'pressure': 1015,
            },
            'weather': [
                {
                    'description': 'céu limpo',
                }
            ],
            'dt': 1790279483,
        }

    @patch.object(WeatherService, 'get_current_weather')
    def test_fetch_weather(self, mock_get_current_weather):
        mock_get_current_weather.return_value = self.weather_data

        response = self.client.post(
            reverse('weather-fetch'),
            {'city': 'Florianopolis,BR'},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(response.data['city'], 'Florianópolis')
        self.assertEqual(response.data['country'], 'BR')
        self.assertEqual(WeatherRecord.objects.count(), 1)

    def test_fetch_weather_without_city(self):
        response = self.client.post(
            reverse('weather-fetch'),
            {},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn('city', response.data)
        self.assertEqual(WeatherRecord.objects.count(), 0)

    @patch.object(WeatherService, 'get_current_weather')
    def test_list_weather_records(self, mock_get_current_weather):
        mock_get_current_weather.return_value = self.weather_data

        WeatherService().save_current_weather('Florianopolis,BR')

        response = self.client.get(
            reverse('weather-list'),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['city'],
            'Florianópolis',
        )
    
    @patch.object(WeatherService, 'get_current_weather')
    def test_fetch_weather_city_not_found(
        self,
        mock_get_current_weather,
    ):
        response_mock = Mock()
        response_mock.status_code = 404

        error = requests.HTTPError()
        error.response = response_mock

        mock_get_current_weather.side_effect = error

        response = self.client.post(
            reverse('weather-fetch'),
            {
                'city': 'CidadeQueNaoExiste123456789,BR',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            response.data['detail'],
            'Cidade não encontrada.',
        )
        self.assertEqual(
            WeatherRecord.objects.count(),
            0,
        )