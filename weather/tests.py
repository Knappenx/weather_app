from django.test import TestCase, Client
from unittest.mock import patch
from urllib.parse import urlencode

from weather_project.settings import API_URL, API_KEY
from .models import City
from django.contrib.auth.models import User


class CityTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user.set_password('123456')
        self.user.save()

    def test_cities_are_identified(self):
        City.objects.create(name="TestCity", user=self.user)
        City.objects.create(name="TestCity2", user=self.user)

        test_city = City.objects.get(name="TestCity", user=self.user)
        test_city_2 = City.objects.get(name="TestCity2", user=self.user)

        self.assertEqual("TestCity - test", str(test_city))
        self.assertEqual("TestCity2 - test", str(test_city_2))

    @patch('weather.views.cache')
    @patch('weather.forms.requests')
    @patch('weather.views.requests')
    def test_valid_request(self, mock_requests, mock_form_requests, mock_cache):
        client = Client()
        client.force_login(self.user)
        mock_cache.get.return_value = None
        mock_form_requests.get.return_value.ok = True
        mock_requests.get.return_value.json.return_value = {
            'main': {'temp': '40'},
            'weather': [{'icon': 'dsd'}]
        }
        response = client.post('/', data=urlencode({"name": "Barcelona"}),
                               content_type="application/x-www-form-urlencoded")
        mock_cache.set.assert_called_once_with("Barcelona", {
            'temperature': '40',
            'icon': 'dsd',
        }, 300)
        self.assertEqual("Barcelona", response.context['cities'][0]['city'].name)

    @patch('weather.forms.requests')
    @patch('weather.views.requests')
    def test_not_exist_city(self, mock_requests, mock_form_requests):
        City.objects.all().delete()
        client = Client()
        mock_form_requests.get.return_value.ok = False
        client.force_login(self.user)
        response = client.post('/', data=urlencode({"name": "non existant city"}),
                               content_type="application/x-www-form-urlencoded")
        mock_requests.get.assert_not_called()
        self.assertEqual("City not found", response.context['form'].errors['name'][0])

    @patch('weather.views.cache')
    @patch('weather.forms.requests')
    @patch('weather.views.requests')
    def test_duplicate_city(self, mock_requests, mock_form_requests, mock_cache):
        City.objects.all().delete()
        city = "Testcity"
        City.objects.create(name=city, user=self.user)
        mock_cache.get.return_value = None
        client = Client()
        client.force_login(self.user)
        response = client.post('/', data=urlencode({"name": city}),
                               content_type="application/x-www-form-urlencoded")
        mock_requests.get.assert_called_with(API_URL.format(city, API_KEY))
        mock_cache.set.assert_called_once()
        self.assertEqual("City already registered", response.context['form'].errors['name'][0])

    @patch('weather.views.cache')
    @patch('weather.forms.requests')
    @patch('weather.views.requests')
    def test_cache_city(self, mock_requests, mock_form_requests, mock_cache):
        City.objects.all().delete()
        City.objects.create(name="Madrid", user=self.user)
        mock_cache.get.return_value = {'city': 'Madrid', "temperature": '30', 'icon': '32'}

        client = Client()
        client.force_login(self.user)
        client.get('/')
        mock_requests.get.assert_not_called()
        mock_cache.set.assert_not_called()

    @patch('weather.views.cache')
    @patch('weather.forms.requests')
    @patch('weather.views.requests')
    def test_not_cache_city(self, mock_requests, mock_form_requests, mock_cache):
        City.objects.all().delete()
        City.objects.create(name="Madrid", user=self.user)
        mock_cache.get.return_value = False

        client = Client()
        client.force_login(self.user)
        client.get('/')

        mock_cache.set.assert_called_once()
        mock_requests.get.assert_called_with(API_URL.format("Madrid", API_KEY))

    def test_favorite_city(self):
        City.objects.all().delete()
        city = City.objects.create(name="London", user=self.user, favorite=False)

        client = Client()
        client.force_login(self.user)

        client.get(f'/favorite/{city.id}/')
        city = City.objects.get(id=city.id)
        self.assertTrue(city.favorite)

        client.get(f'/favorite/{city.id}/')
        city = City.objects.get(id=city.id)
        self.assertFalse(city.favorite)
