from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.urls import reverse

from accounts.forms import UserRegistrationForm

from django.contrib import messages

from django.shortcuts import render, redirect



# Create your views here.



from django.contrib.auth.models import User

from django.contrib.auth import login, authenticate



from .forms import UserRegistrationForm

from .models import Profile

from django import forms

from django.contrib.auth.decorators import login_required

from django.core.exceptions import ObjectDoesNotExist

from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
import json
def api_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'status': 'success',
                'redirect': reverse('homepage'),
                'csrf_token': get_token(request)
            })
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid credentials'
        }, status=401)
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)





def register(request):

    if request.method == 'POST':

        form = UserRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.set_password(form.cleaned_data['password'])

            user.save()  # Save the user first



            # Create a profile for the new user

            Profile.objects.create(user=user, is_normal_user=True)

            login(request, user)  # Log the user in automatically

            return redirect('home')  # Redirect to home page after registration

    else:

        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})



@login_required

def dashboard(request):

    profile = Profile.objects.get(user=request.user)

    if request.user.is_superuser:

        return render(request, 'homepage.html', {

        'profile': profile,

        'user_type': profile.get_user_type_display()  # This will show "Admin", "Seller", or "Buyer"

    })

    else:

        return render(request, 'index.html', {'profile': profile})



@login_required

def view_profile(request):

    try:

        profile = Profile.objects.get(user=request.user)

    except ObjectDoesNotExist:

        profile = None  # In case the profile does not exist yet



    return render(request, 'view_profile.html', {'profile': profile, 'user': request.user})




@login_required
def edit_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=request.user)  # Create a new profile if it doesn't exist

    if request.method == 'POST':
        # Get user fields
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Update user fields
        user = request.user
        if username:
            user.username = username
        if email:
            user.email = email
        user.save()

        # Get profile fields
        bio = request.POST.get('bio')
        location = request.POST.get('location')
        profile_picture = request.FILES.get('profile_picture')

        # Update profile fields
        if bio is not None:
            profile.bio = bio
        if location is not None:
            profile.location = location
        if profile_picture:
            profile.profile_picture = profile_picture
        profile.save()

        messages.success(request, "Your profile has been updated successfully.")
        return redirect('view_profile')  # Redirect to view profile after editing

    return render(request, 'edit_profile.html', {'profile': profile, 'user': request.user})


@login_required

def view_profile(request):

    try:

        profile = Profile.objects.get(user=request.user)

    except ObjectDoesNotExist:

        profile = None  # Handle case where profile does not exist



    return render(request, 'view_profile.html', {'profile': profile, 'user': request.user})