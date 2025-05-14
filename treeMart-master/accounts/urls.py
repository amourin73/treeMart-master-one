from django.urls import path

from . import views



urlpatterns = [

    path('register/', views.register, name='register'),

    path('profile', views.view_profile, name='view_profile'),

    path('', views.edit_profile, name='edit_profile'),

]
