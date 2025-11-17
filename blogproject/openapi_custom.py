from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.generators import SchemaGenerator


class FilteredSchemaView(APIView):
    """Generate OpenAPI schema and strip unwanted auth schemes.

    Using an APIView ensures DRF performs renderer negotiation so the
    Response is returned with accepted_renderer set (avoids earlier
    renderer negotiation errors when trying to call views directly).
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        generator = SchemaGenerator()
        schema = generator.get_schema(request=request, public=True)

        # Defensive update: ensure components/securitySchemes exists
        comps = schema.setdefault('components', {})
        schemes = comps.setdefault('securitySchemes', {})

        # Remove common unwanted schemes
        schemes.pop('basicAuth', None)
        schemes.pop('cookieAuth', None)

        # Ensure Bearer scheme exists
        if 'Bearer' not in schemes:
            schemes['Bearer'] = {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'Enter token like: Bearer <your_token>'
            }

        schema['components'] = comps
        schema['security'] = [{'Bearer': []}]

        # Also sanitize per-operation security entries so they don't reference
        # removed schemes (basicAuth / cookieAuth). Replace remaining
        # security alternatives with Bearer where appropriate.
        paths = schema.get('paths', {})
        for path_item in paths.values():
            for operation in path_item.values():
                if not isinstance(operation, dict):
                    continue
                sec = operation.get('security')
                if sec is None:
                    continue
                new_sec = []
                for item in sec:
                    # preserve explicit Bearer entries
                    if isinstance(item, dict) and 'Bearer' in item:
                        new_sec.append({'Bearer': []})
                        continue
                    # preserve anonymous alternative
                    if item == {}:
                        new_sec.append(item)
                        continue
                    # drop basicAuth / cookieAuth and any unknown entries
                # if nothing left, default to requiring Bearer
                if not new_sec:
                    new_sec = [{'Bearer': []}]
                operation['security'] = new_sec

        return Response(schema)
