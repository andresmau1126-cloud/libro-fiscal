"""
ASGI config para Libro Fiscal project con Channels para WebSocket.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Inicializar Django ASGI application
django_asgi_app = get_asgi_application()

try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from channels.security.websocket import AllowedHostsOriginValidator
    
    # Importar routing de WebSocket después de inicializar Django
    from apps.inventario.routing import websocket_urlpatterns

    application = ProtocolTypeRouter({
        # Django's ASGI application to handle traditional HTTP requests
        "http": django_asgi_app,
        
        # WebSocket chat handler with channels
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    websocket_urlpatterns
                )
            )
        ),
    })
except ImportError:
    # Fallback a WSGI si channels no está disponible
    application = django_asgi_app
