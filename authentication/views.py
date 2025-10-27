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
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import json
from .forms import SignUpForm, LoginForm, ForgotPasswordForm, OTPVerificationForm, ResetPasswordForm
from utils.common import send_email_notification, get_user_display_name


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

        print("User created: {user}")
        
        # Send welcome email using utils function
        email_subject = "Welcome to Our Blog!"
        email_message = f'Hi {full_name},\n\nThank you for signing up! Your account has been created successfully.\n\nYou can now log in with your email: {email}\n\nHappy Blogging!'
        
        send_email_notification(
            subject=email_subject,
            message=email_message,
            recipient_email=email
        )
        
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


# --- Forgot Password Views ---
def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            # Normalize email to avoid case/whitespace mismatches
            email = (form.cleaned_data['email'] or '').strip()
            # Case-insensitive match on email OR username (some users use email as username)
            user = User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).first()
            try:
                if not user:
                    raise User.DoesNotExist
                # Generate 4-digit OTP
                otp = str(random.randint(1000, 9999))
                
                # Store OTP in session with expiration (10 minutes)
                request.session['reset_otp'] = otp
                request.session['reset_email'] = email
                request.session['otp_expires'] = (timezone.now() + timedelta(minutes=10)).isoformat()
                
                # Send OTP email
                try:
                    send_mail(
                        'Password Reset OTP',
                        f'Your password reset code is: {otp}\n\nThis code will expire in 10 minutes.',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    messages.success(request, f'OTP sent to {email}')
                    return redirect('otp_verification')
                except Exception as e:
                    # If email fails, show error and do not redirect
                    print(f"Email sending failed: {e}")
                    print(f"OTP for {email}: {otp}")
                    messages.error(request, 'Could not send email. Please verify email settings and try again.')
                    return render(request, 'authentication/forgot_password.html', {'form': form})
                
            except User.DoesNotExist:
                messages.error(request, 'Email does not exist')
                return render(request, 'authentication/forgot_password.html', {'form': form})
        else:
            messages.error(request, 'Please enter a valid email address')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'authentication/forgot_password.html', {'form': form})


def otp_verification_view(request):
    # Check if user has valid session
    if 'reset_otp' not in request.session or 'reset_email' not in request.session:
        messages.error(request, 'Invalid session. Please start the password reset process again.')
        return redirect('forgot_password')
    
    # Check if OTP has expired
    if 'otp_expires' in request.session:
        try:
            expires_at = timezone.datetime.fromisoformat(request.session['otp_expires'])
            if timezone.now() > expires_at:
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('forgot_password')
        except:
            messages.error(request, 'Invalid session. Please start the password reset process again.')
            return redirect('forgot_password')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            stored_otp = request.session.get('reset_otp')
            
            if entered_otp == stored_otp:
                messages.success(request, 'OTP verified successfully!')
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        else:
            messages.error(request, 'Please enter a valid 4-digit OTP.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'authentication/otp_verification.html', {'form': form})


def resend_otp_view(request):
    if 'reset_email' not in request.session:
        messages.error(request, 'Invalid session. Please start the password reset process again.')
        return redirect('forgot_password')
    
    email = request.session['reset_email']
    try:
        user = User.objects.get(email=email)
        # Generate new 4-digit OTP
        otp = str(random.randint(1000, 9999))
        
        # Update OTP in session with new expiration
        request.session['reset_otp'] = otp
        request.session['otp_expires'] = (timezone.now() + timedelta(minutes=10)).isoformat()
        
        # Send new OTP email
        try:
            send_mail(
                'Password Reset OTP (New)',
                f'Your new password reset code is: {otp}\n\nThis code will expire in 10 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, f'New OTP sent to {email}')
            return redirect('otp_verification')
        except Exception as e:
            print(f"Email sending failed: {e}")
            print(f"New OTP for {email}: {otp}")
            messages.error(request, 'Could not send email. Please verify email settings and try again.')
            return redirect('forgot_password')
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid session. Please start the password reset process again.')
        return redirect('forgot_password')


def reset_password_view(request):
    # Check if user has valid session
    if 'reset_otp' not in request.session or 'reset_email' not in request.session:
        messages.error(request, 'Invalid session. Please start the password reset process again.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            email = request.session['reset_email']
            
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Clear session data
                request.session.pop('reset_otp', None)
                request.session.pop('reset_email', None)
                request.session.pop('otp_expires', None)
                
                messages.success(request, 'Password updated successfully! Please login with your new password.')
                return redirect('login')
                
            except User.DoesNotExist:
                messages.error(request, 'Invalid session. Please start the password reset process again.')
                return redirect('forgot_password')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'authentication/reset_password.html', {'form': form})


    