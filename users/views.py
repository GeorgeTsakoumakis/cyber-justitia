from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

# Create your views here.
def index(request):
    return render(request, 'main/index.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        phone = request.POST['phone']
        user_type = request.POST['user_type']
        flair = request.POST['flair']

        try:
            validate_password(password)
        except Exception as e:
            messages.info(request, 'Password not strong enough')
            return redirect('register')

        if password != password2:
            messages.info(request, 'Password not matching')
            return redirect('register')

        is_professional = False
        if user_type == 'standard':
            is_professional = False
            flair = None
        elif user_type == 'professional':
            is_professional = True

        if CustomUser.objects.filter(username=username).exists():
            messages.info(request, 'Username already exists')
            return redirect('register')
        elif CustomUser.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists')
            return redirect('register')
        else:
            # Save user to database
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, phone=phone, is_professional=is_professional, flair=flair)
            user.save()
            return redirect('login')

    return render(request, 'main/register.html')


def login(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#
#         user = auth.authenticate(username=username, password=password)
#
#         if user is not None:
#             auth.login(request, user)
#             return redirect('/')
#         else:
#             messages.info(request, 'Invalid credentials')
#             return redirect('login')
#
    return render(request, 'main/login.html')


def logout(request):
    # auth.logout(request)
    return redirect('/')