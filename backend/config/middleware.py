from django.conf import settings


class ProductionHstsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not settings.DEBUG and settings.SECURE_HSTS_SECONDS:
            policy = f"max-age={settings.SECURE_HSTS_SECONDS}"
            if settings.SECURE_HSTS_INCLUDE_SUBDOMAINS:
                policy += "; includeSubDomains"
            if getattr(settings, "SECURE_HSTS_PRELOAD", False):
                policy += "; preload"
            response.setdefault("Strict-Transport-Security", policy)
        return response
