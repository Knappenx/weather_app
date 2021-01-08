from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('favorite/<int:city_id>/', views.favorite, name='favorite'),
    path('', views.index, name='index')
]
