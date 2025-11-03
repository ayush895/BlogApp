from django.urls import path
from .views import *

app_name='api'
urlpatterns = [
    path('register/', Registeruser.as_view(), name='register_user'),
    # path('login/', login_user.as_views(), name='login_user'),
]