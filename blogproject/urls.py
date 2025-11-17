"""
URL configuration for blogproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView  
from .openapi_custom import FilteredSchemaView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blogapp.urls')),            # Blog app URLs       
    path('auth/', include('authentication.urls')),  # Authentication app URLs   
    path('api/', include('api.urls')),

]

test_patterns = [
    # Swagger UI for human-friendly docs
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # OpenAPI schema (JSON/YAML) - use filtered view to remove unwanted auth schemes
    path("api/schema/", FilteredSchemaView.as_view(), name="schema"),
    # Redoc UI (optional)
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

urlpatterns += test_patterns

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)