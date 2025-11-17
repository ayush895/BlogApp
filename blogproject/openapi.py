"""OpenAPI helper module.

This file previously contained a schema post-processor which caused
renderer/request negotiation errors when invoked directly. We no longer
use it; keep a minimal placeholder to avoid accidental imports.
"""

def filtered_schema(request, *args, **kwargs):
    # Not used. If you need a custom schema filter, implement a management
    # command or a proper DRF view that constructs a DRF Request object
    # and performs renderer negotiation before returning a Response.
    raise NotImplementedError("filtered_schema is intentionally disabled; use SpectacularAPIView directly.")
