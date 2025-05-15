from django.urls import path
from . import views

from .views import seasonal_recommendations

urlpatterns = [


    path('plant-guide/', views.plant_guide, name='plant_guide'),

    path('select-season/', views.select_season, name='select_season'),
    path('plants-by-season/<season>/', views.plants_by_season, name='plants_by_season'),
    path('weather/', views.weather_check, name='weather'),
path('api/weather', views.weather_api, name='weather_api'),
    path('api/recommend-trees', views.recommend_trees, name='recommend_trees'),
path('api/products/seasonal/<str:season>/', seasonal_recommendations, name='seasonal_recommendations'),


]