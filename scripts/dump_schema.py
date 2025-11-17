import os
import sys
import django
import json

# Ensure project root is on sys.path so Django can import the project package
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogproject.settings')
try:
	django.setup()
except Exception as exc:
	print('Django setup failed:', exc)
	raise
from django.test import Client

# Delay importing drf-spectacular until after Django settings are configured
from drf_spectacular.generators import SchemaGenerator

# First try: directly generating the schema via the generator (for debugging)
generator = SchemaGenerator()
schema = generator.get_schema(request=None, public=True)

components = schema.get('components', {})
security_schemes = components.get('securitySchemes', {})
print('DIRECT GENERATOR SECURITY_SCHEMES:')
print(json.dumps(security_schemes, indent=2))

print('\n--- Now requesting /api/schema/ via Django test Client (this uses the FilteredSchemaView) ---\n')
client = Client()
resp = client.get('/api/schema/', HTTP_ACCEPT='application/json', HTTP_HOST='localhost')
try:
	body = json.loads(resp.content.decode())
except Exception:
	body = {'error': 'failed to parse response', 'status_code': resp.status_code}

components2 = body.get('components', {})
security_schemes2 = components2.get('securitySchemes', {})
print('CLIENT-REQUESTED SECURITY_SCHEMES:')
print(json.dumps(security_schemes2, indent=2))

print('\nCLIENT TOP-LEVEL SECURITY:')
print(json.dumps(body.get('security', {}), indent=2))

print('\n/api/auth/login/ security (client):')
login_path = body.get('paths', {}).get('/api/auth/login/', {})
print(json.dumps(login_path.get('post', {}).get('security', 'MISSING'), indent=2))

# Optionally: print first 400 chars of full schema
# print('\nFULL SCHEMA SNIPPET:\n')
# print(json.dumps(schema, indent=2)[:400])
