from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('otp-verification/', views.otp_verification_view, name='otp_verification'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
]
