from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password   
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import IntegrityError
from .forms import SignUpForm,LoginForm
import json


# def signup_view(request):
#     print("Signup view accessed")
#     if request.method == 'POST':
#         # form=SignUpForm(request.POST)
#         # if form.is_valid():
#             # fullname=form.cleaned_data['firstname']
#             # email= form.cleaned_data['email']
#             # password=form.cleaned_data['password']
#             # print(fullname,email,password)

#             firstname=request.POST.get('firstname')
#             email=request.POST.get('email')
#             password=request.POST.get('password')

#             #creating the user
#             user=User.objects.create_user(first_name=firstname,username=email,email=email,password=password)
            
#             print(f"User created: {user}")
#             messages.success(request, "Account created successfully! Please login.")
#             return redirect('login')
    
#         # else:
#         #     print(form.errors)
#         #     messages.error(request, "Please correct the errors below.")
#     else:
#         form=SignUpForm()   
#     return render(request, 'authentication/signup.html', {'form': form})

def signup_view(request):
    print("Signup view accessed")
    if request.method == 'POST':
        # Read values from the form (keeping current template field names)
        full_name = request.POST.get('full_name', '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password')

        # Basic validation
        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'authentication/signup.html', {'form': SignUpForm(request.POST)})

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'authentication/signup.html', {'form': SignUpForm(request.POST)})

        # Duplicate email/username check (we use email as username)
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. Please log in or use another email.")
            return render(request, 'authentication/signup.html', {'form': SignUpForm(request.POST)})

        try:
            user = User.objects.create_user(
                first_name=full_name,
                username=email,  # enforce uniqueness via username field
                email=email,
                password=password,
            )
        except IntegrityError:
            # In case of a race between the exists() check and create_user()
            messages.error(request, "An account with this email already exists. Please log in.")
            return render(request, 'authentication/signup.html', {'form': SignUpForm(request.POST)})

        print(f"User created: {user}")
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form=LoginForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']

            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "No account found with this email.")
                return render(request, 'authentication/login.html', {'form': form})

            # Authenticate
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid password.")
                return render(request, 'authentication/login.html', {'form': form})

        else:
            messages.error(request, "Please fill in both email and password.")
            return render(request, 'authentication/login.html', {'form': form})

    return render(request, 'authentication/login.html')

# --- Logout View ---
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')


    