from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.conf import settings

from .models import City

import requests


class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['name', 'favorite']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CityForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        city_name = self.cleaned_data.get('name').capitalize()
        if City.objects.filter(name=city_name, user=self.user).exists():
            raise ValidationError('City already registered')
        url = settings.API_URL
        response = requests.get(url.format(city_name, settings.API_KEY))
        if not response.ok:
            raise ValidationError('City not found')
        return city_name
