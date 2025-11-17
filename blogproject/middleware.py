from django.conf import settings

_cleared = False

class ClearSessionsOnFirstRequestMiddleware:
    """Middleware that clears all sessions once on the first request when DEBUG=True.

    This is used only for development to ensure server restarts don't keep users
    logged in because of stale session rows + cookies in the browser. It avoids
    doing DB queries during app initialization (which raises warnings).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _cleared
        if settings.DEBUG and not _cleared:
            try:
                from django.contrib.sessions.models import Session
                Session.objects.all().delete()
                print('Cleared all sessions on first request (DEBUG).')
            except Exception:
                pass
            _cleared = True
        return self.get_response(request)
