from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

app_name='api'
router = routers.DefaultRouter()

urlpatterns = [
    # auth
    path('auth/register/', views.Registeruser.as_view(), name='api-register'),
    path('auth/login/', views.LoginUser.as_view(), name='api-login'),

    # blogs
    path('blogs/', views.BlogList.as_view(), name='api-blogs-list'),
    path('blogs/<int:id>/', views.BlogDetail.as_view(), name='api-blog-detail'),
    path('blogs/<int:id>/publish/', views.BlogPublish.as_view(), name='api-blog-publish'),
    path('blogs/<int:id>/draft/', views.BlogSaveDraft.as_view(), name='api-blog-draft'),
    path('blogs/create/', views.BlogCreate.as_view(), name='api-blog-create'),

    # comments
    path('blogs/<int:id>/comments/', views.CommentsList.as_view(), name='api-comments-list'),

    # include router urls if any viewsets are added later
    path('', include(router.urls)),
    # JWT token refresh
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]