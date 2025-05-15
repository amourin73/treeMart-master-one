from django.shortcuts import render

from trees.models import Tree
import requests
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Tree
import datetime


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seasonal_recommendations(request, season):
    """
    Get tree recommendations based on season
    """
    month = timezone.now().month

    # For Bangladesh's six seasons
    season_mapping = {
        'winter': {'months': [11, 12, 1, 2], 'tags': ['winter-hardy', 'evergreen']},
        'spring': {'months': [3, 4], 'tags': ['flowering', 'fruit']},
        'summer': {'months': [5, 6, 7], 'tags': ['drought-tolerant', 'heat-resistant']},
        'monsoon': {'months': [7, 8], 'tags': ['water-loving', 'fast-growing']},
        'autumn': {'months': [9, 10], 'tags': ['ornamental', 'colorful-foliage']},
        'late-autumn': {'months': [10, 11], 'tags': ['fruit', 'nut']}
    }

    # Get tags for current season
    tags = season_mapping.get(season.lower(), {}).get('tags', [])

    # Get recommended trees
    trees = Tree.objects.filter(tags__name__in=tags).distinct()[:8]

    # If not enough, fallback to seasonal_suitability field
    if trees.count() < 4:
        trees = Tree.objects.filter(seasonal_suitability__contains=season.capitalize())[:8]

    # Serialize the data
    from .serializers import TreeSerializer
    serializer = TreeSerializer(trees, many=True, context={'request': request})

    return Response({
        'season': season.capitalize(),
        'recommendations': serializer.data
    })

def weather_api(request):
    print("Weather API endpoint hit!")  # Debugging
    city = request.GET.get('city', '')
    print(f"City requested: {city}")  # Debugging
    api_key = "YOUR_WEATHER_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({
            'city': city,
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'condition': data['weather'][0]['main'],
            'icon': f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
        })
    else:
        return JsonResponse({'error': 'Could not fetch weather data'}, status=400)


@csrf_exempt
def recommend_trees(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            temperature = data.get('temperature')
            humidity = data.get('humidity')
            condition = data.get('condition')

            # Your logic to determine recommended trees based on weather
            # This could query your database or call another API
            recommended_trees = get_recommended_trees(temperature, humidity, condition)

            return JsonResponse({
                'trees': recommended_trees,
                'tips': get_planting_tips(temperature, humidity, condition)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_recommended_trees(temp, humidity, condition):
    # Example logic - replace with your actual implementation
    trees = []
    if temp < 5:
        trees = [
            {'name': 'Blue Spruce', 'reason': 'Thrives in cold temperatures'},
            {'name': 'Paper Birch', 'reason': 'Cold-hardy tree that adapts well to winter conditions'}
        ]
    elif temp < 20:
        trees = [
            {'name': 'Red Maple', 'reason': 'Does well in moderate temperatures'},
            {'name': 'White Oak', 'reason': 'Adaptable to various conditions including moderate climates'}
        ]
    else:
        trees = [
            {'name': 'Palm Tree', 'reason': 'Loves warm weather and sunshine'},
            {'name': 'Olive Tree', 'reason': 'Thrives in warm, dry conditions'}
        ]

    # Adjust based on humidity
    if humidity > 70:
        trees.append({'name': 'Willow', 'reason': 'Loves moist environments'})

    return trees


def get_planting_tips(temp, humidity, condition):
    tips = []
    if temp < 5:
        tips.append("Plant in early spring after the last frost.")
    elif temp > 25:
        tips.append("Water deeply in the early morning to prevent evaporation.")

    if humidity > 70:
        tips.append("Ensure proper drainage to prevent root rot.")

    if 'rain' in condition.lower():
        tips.append("Take advantage of rainy days to plant new trees.")

    return tips
# Create your views here.
def plant_guide(request):
    return render(request, 'select_season.html')


def select_season(request):
    # Display a form or page for selecting a season
    return render(request, 'select_season.html')


def plants_by_season(request, season):
    # Fetch trees (plants) suitable for the selected season
    trees = Tree.objects.filter(season=season)

    # Pass the trees and the selected season to the template
    return render(request, 'plants_by_season.html', {'trees': trees, 'season': season})




#

def weather_check(request):
    weather_data = None
    tree_recommendation = None

    if request.method == "POST":
        city = request.POST.get('city')
        api_key = '81f59dee117443268c250122251804'
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and 'error' not in data:
            weather_data = {
                'city': data['location']['name'],
                'region': data['location']['region'],
                'country': data['location']['country'],
                'temperature': data['current']['temp_c'],
                'condition': data['current']['condition']['text'],
                'icon': data['current']['condition']['icon'],
            }

            # tree recommendation
            tree_recommendation = recommend_tree(data['current']['condition']['text'])
        else:
            weather_data = {'error': 'City not found'}

    return render(request, 'weather.html', {
        'weather': weather_data,
        'tree': tree_recommendation
    })


def recommend_tree(condition):
    condition = condition.lower()
    if 'rain' in condition or 'storm' in condition:
        return "Coconut Tree 🌴 (suitable for humid and coastal areas)"
    elif 'clear' in condition or 'sunny' in condition:
        return "Neem Tree 🌳 (great for sunny, dry climates)"
    elif 'Partly Cloudy' in condition:
        return "Mango Tree 🥭 (good in mild cloudy weather)"
    elif 'snow' in condition:
        return "Pine Tree 🌲 (ideal for cold, snowy climates)"
    else:
        return "Banyan Tree 🌳 (suitable for most weather types)"
