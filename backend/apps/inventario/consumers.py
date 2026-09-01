"""
WebSocket consumers para sincronización del inventario centralizado en tiempo real.
Permite que múltiples usuarios (vendedores, gerente, admin) reciban actualizaciones del inventario instantáneamente.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from decimal import Decimal

logger = logging.getLogger(__name__)


class InventarioCentralizadoConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer para sincronización del inventario centralizado en tiempo real.
    
    Grupos:
    - "inventario_global": Recibe actualizaciones de todo el inventario
    - "inventario_producto_{producto_id}": Recibe actualizaciones de un producto específico
    - "ventas_vendedor_{vendedor_id}": Recibe notificaciones de ventas de un vendedor
    - "ventas_global": Recibe notificaciones de todas las ventas
    """

    async def connect(self):
        """Se ejecuta cuando se conecta el cliente WebSocket."""
        self.user = self.scope["user"]
        self.producto_id = self.scope["url_route"].get("producto_id")
        self.vendedor_id = self.scope["url_route"].get("vendedor_id")

        if not self.user.is_authenticated:
            await self.close()
            return

        # Agregar usuario a grupos según su rol y parámetros
        # Todos ven el inventario centralizado global
        await self.channel_layer.group_add("inventario_global", self.channel_name)

        # Si es un producto específico
        if self.producto_id:
            grupo = f"inventario_producto_{self.producto_id}"
            await self.channel_layer.group_add(grupo, self.channel_name)

        # Si es un vendedor específico
        if self.vendedor_id:
            grupo = f"ventas_vendedor_{self.vendedor_id}"
            await self.channel_layer.group_add(grupo, self.channel_name)

        # Gerentes, admins y auditores ven todas las ventas
        if self.user.rol in {"admin", "gerente", "auditor"}:
            await self.channel_layer.group_add("ventas_global", self.channel_name)

        await self.accept()
        logger.info(
            f"Usuario {self.user.email} ({self.user.rol}) conectado a inventario centralizado"
        )

        # Enviar estado inicial
        await self.enviar_estado_inicial()

    async def disconnect(self, close_code):
        """Se ejecuta cuando se desconecta el cliente WebSocket."""
        # Remover de todos los grupos
        await self.channel_layer.group_discard("inventario_global", self.channel_name)

        if self.producto_id:
            grupo = f"inventario_producto_{self.producto_id}"
            await self.channel_layer.group_discard(grupo, self.channel_name)

        if self.vendedor_id:
            grupo = f"ventas_vendedor_{self.vendedor_id}"
            await self.channel_layer.group_discard(grupo, self.channel_name)

        if self.user.rol in {"admin", "gerente", "auditor"}:
            await self.channel_layer.group_discard("ventas_global", self.channel_name)

        logger.info(f"Usuario {self.user.email} desconectado de inventario centralizado")

    async def receive(self, text_data):
        """Se ejecuta cuando recibe un mensaje del cliente."""
        try:
            data = json.loads(text_data)
            tipo = data.get("tipo")

            if tipo == "request_estado":
                await self.enviar_estado_inicial()
            elif tipo == "ping":
                await self.send_json({"tipo": "pong", "timestamp": timezone.now().isoformat()})
            else:
                logger.warning(f"Tipo de mensaje desconocido: {tipo}")
        except json.JSONDecodeError:
            logger.error(f"Error decodificando JSON: {text_data}")

    # Métodos para recibir eventos del servidor
    async def inventario_actualizado(self, event):
        """Recibe actualización de inventario centralizado."""
        await self.send_json({
            "tipo": "inventario_actualizado",
            "data": event["data"],
            "timestamp": timezone.now().isoformat(),
        })

    async def venta_registrada(self, event):
        """Recibe notificación de una nueva venta."""
        await self.send_json({
            "tipo": "venta_registrada",
            "data": event["data"],
            "timestamp": timezone.now().isoformat(),
        })

    async def producto_critico(self, event):
        """Recibe alerta de producto con stock crítico."""
        await self.send_json({
            "tipo": "producto_critico",
            "data": event["data"],
            "timestamp": timezone.now().isoformat(),
        })

    async def notificacion(self, event):
        """Recibe notificación genérica."""
        await self.send_json({
            "tipo": "notificacion",
            "mensaje": event.get("mensaje"),
            "nivel": event.get("nivel", "info"),
            "timestamp": timezone.now().isoformat(),
        })

    # Métodos auxiliares
    async def send_json(self, content):
        """Envía datos JSON al cliente."""
        await self.send(text_data=json.dumps(content))

    async def enviar_estado_inicial(self):
        """Envía el estado inicial del inventario al conectarse."""
        estado = await self.obtener_estado_inventario()
        await self.send_json({
            "tipo": "estado_inicial",
            "data": estado,
            "timestamp": timezone.now().isoformat(),
        })

    @database_sync_to_async
    def obtener_estado_inventario(self):
        """Obtiene el estado actual del inventario."""
        from .models import EstadoInventarioCentralizado
        from .serializers import EstadoInventarioCentralizadoSerializer

        # Si es un producto específico, retorna solo ese
        if self.producto_id:
            try:
                estado = EstadoInventarioCentralizado.objects.select_related(
                    "producto", "usuario_actualizo"
                ).get(producto_id=self.producto_id)
                return EstadoInventarioCentralizadoSerializer(estado).data
            except EstadoInventarioCentralizado.DoesNotExist:
                return None

        # Si no, retorna todos los productos (con filtro según permisos)
        estados = EstadoInventarioCentralizado.objects.select_related(
            "producto", "usuario_actualizo"
        ).order_by("-ultima_actualizacion")[:50]

        return EstadoInventarioCentralizadoSerializer(estados, many=True).data


class NotificacionesInventarioConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer para notificaciones de inventario.
    Notifica sobre productos con stock bajo, próximos a vencer, etc.
    """

    async def connect(self):
        """Se ejecuta cuando se conecta el cliente WebSocket."""
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Grupo para notificaciones del usuario actual
        self.grupo_usuario = f"notificaciones_usuario_{self.user.id}"
        await self.channel_layer.group_add(self.grupo_usuario, self.channel_name)

        # Gerentes, admins y auditores reciben notificaciones globales
        if self.user.rol in {"admin", "gerente", "auditor"}:
            await self.channel_layer.group_add("notificaciones_global", self.channel_name)

        await self.accept()
        logger.info(f"Usuario {self.user.email} conectado a notificaciones de inventario")

    async def disconnect(self, close_code):
        """Se ejecuta cuando se desconecta el cliente WebSocket."""
        await self.channel_layer.group_discard(self.grupo_usuario, self.channel_name)

        if self.user.rol in {"admin", "gerente", "auditor"}:
            await self.channel_layer.group_discard("notificaciones_global", self.channel_name)

        logger.info(f"Usuario {self.user.email} desconectado de notificaciones")

    async def receive(self, text_data):
        """Se ejecuta cuando recibe un mensaje del cliente."""
        try:
            data = json.loads(text_data)
            tipo = data.get("tipo")

            if tipo == "ping":
                await self.send_json({"tipo": "pong"})
            else:
                logger.warning(f"Tipo de mensaje desconocido: {tipo}")
        except json.JSONDecodeError:
            logger.error(f"Error decodificando JSON: {text_data}")

    # Métodos para recibir eventos
    async def notificacion_stock_bajo(self, event):
        """Recibe notificación de stock bajo."""
        await self.send_json({
            "tipo": "stock_bajo",
            "titulo": "Stock Bajo",
            "mensaje": event.get("mensaje"),
            "producto": event.get("producto"),
            "stock_actual": event.get("stock_actual"),
            "stock_minimo": event.get("stock_minimo"),
            "timestamp": timezone.now().isoformat(),
        })

    async def notificacion_vencimiento(self, event):
        """Recibe notificación de próximo vencimiento."""
        await self.send_json({
            "tipo": "vencimiento_proximo",
            "titulo": "Producto Próximo a Vencer",
            "mensaje": event.get("mensaje"),
            "producto": event.get("producto"),
            "fecha_vencimiento": event.get("fecha_vencimiento"),
            "dias_para_vencer": event.get("dias_para_vencer"),
            "timestamp": timezone.now().isoformat(),
        })

    async def notificacion_alerta(self, event):
        """Recibe alerta genérica."""
        await self.send_json({
            "tipo": "alerta",
            "nivel": event.get("nivel", "warning"),
            "titulo": event.get("titulo"),
            "mensaje": event.get("mensaje"),
            "timestamp": timezone.now().isoformat(),
        })

    async def send_json(self, content):
        """Envía datos JSON al cliente."""
        await self.send(text_data=json.dumps(content))
