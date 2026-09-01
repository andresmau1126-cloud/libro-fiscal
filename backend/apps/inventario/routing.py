"""
Configuración de rutas para WebSocket de inventario centralizado.
"""

from django.urls import path
from .consumers import InventarioCentralizadoConsumer, NotificacionesInventarioConsumer

websocket_urlpatterns = [
    # WebSocket para inventario centralizado
    path(
        "ws/inventario/",
        InventarioCentralizadoConsumer.as_asgi(),
        name="ws-inventario-centralizado"
    ),
    path(
        "ws/inventario/<int:producto_id>/",
        InventarioCentralizadoConsumer.as_asgi(),
        name="ws-inventario-producto"
    ),
    path(
        "ws/ventas/<int:vendedor_id>/",
        InventarioCentralizadoConsumer.as_asgi(),
        name="ws-ventas-vendedor"
    ),
    
    # WebSocket para notificaciones
    path(
        "ws/notificaciones/",
        NotificacionesInventarioConsumer.as_asgi(),
        name="ws-notificaciones"
    ),
]
