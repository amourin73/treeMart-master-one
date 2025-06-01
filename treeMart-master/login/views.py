from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

from django.contrib.auth import logout

from trees.models import Tree
from django.db.models import F, FloatField, ExpressionWrapper

def home(request):
    return render(request, "index.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return redirect('signup')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use. Please choose another.")
            return redirect('signup')

        # Create the user if everything is valid
        myuser = User.objects.create_user(username=username, email=email, password=pass1)
        myuser.save()

        messages.success(request, "Your account has been successfully created.")
        return redirect('login')

    return render(request, "signup.html")
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('login')

    return render(request, "signin.html")
def homepage(request):
    most_rated_trees = Tree.objects.annotate(
        annotated_average_rating=ExpressionWrapper(
            F('total_rating') / F('num_ratings'),
            output_field=FloatField()
        )
    ).filter(num_ratings__gt=0).order_by('-annotated_average_rating')[:6]
    return render(request, 'homepage.html', {'most_rated_trees': most_rated_trees})

def logout_view(request):
    logout(request)
    return redirect('home')

