import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogproject.settings')
import django
django.setup()
from django.urls import get_resolver
patterns = get_resolver().url_patterns
for pat in patterns:
    p = pat.pattern
    route = getattr(p, '_route', None)
    if route is None and hasattr(p, 'regex'):
        route = p.regex.pattern
    print(route, ' name=', getattr(pat, 'name', None), ' repr=', repr(pat))
