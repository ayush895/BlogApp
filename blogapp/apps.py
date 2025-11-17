from django.apps import AppConfig


class BlogappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blogapp'
    
    def ready(self):
        # Intentionally left blank; session cleanup is handled by
        # `ClearSessionsOnFirstRequestMiddleware` to avoid DB access during app init.
        return
