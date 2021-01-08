from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from weather.models import City
from weather.forms import CityForm

from weather_project.settings import API_KEY, API_URL

import requests


@login_required(login_url='rbac/login/')
def favorite(request, city_id):
    city = City.objects.get(id=city_id)
    city.favorite = not city.favorite
    city.save()
    return redirect('/')


@login_required(login_url='rbac/login/')
def index(request):
    if request.method == 'POST':
        form = CityForm(request.POST, user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            form = CityForm(user=request.user)
    else:
        form = CityForm(user=request.user)
    paginator = Paginator(City.objects.filter(user=request.user).order_by('-favorite'), 3)
    cities = paginator.get_page(request.GET.get('page'))
    cities_context = []
    for city in cities:
        city_weather = cache.get(city.name.replace(' ', ''))
        if not city_weather:
            url = API_URL.format(city.name, API_KEY)
            response = requests.get(url)
            city_weather = {
                'temperature': response.json()['main']['temp'],
                'icon': response.json()['weather'][0]['icon']
            }
            cache.set(city.name.replace(" ", ""), city_weather, 300)
        cities_context.append({'city': city, 'weather': city_weather})
    return render(request, 'index.html', {'form': form, 'cities': cities_context, 'paginator': cities,
                                          'pages': range(1, cities.paginator.num_pages+1)})
