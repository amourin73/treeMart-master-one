from django.urls import path

from . import views
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [

    path('register/', views.register, name='register'),

    path('profile', views.view_profile, name='view_profile'),

    path('', views.edit_profile, name='edit_profile'),
path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

]
