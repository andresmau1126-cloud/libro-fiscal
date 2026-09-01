"""
Utilidades para sincronización de inventario centralizado en tiempo real.
"""

import logging
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

def _get_channel_layer():
    """Obtener channel layer de forma segura"""
    try:
        from channels.layers import get_channel_layer
        return get_channel_layer()
    except (ImportError, RuntimeError):
        return None


def notificar_cambio_inventario(producto_id, stock_anterior, stock_posterior, tipo_movimiento, usuario_nombre):
    """
    Notifica a todos los usuarios conectados sobre un cambio en el inventario.
    
    Args:
        producto_id: ID del producto
        stock_anterior: Stock antes del cambio
        stock_posterior: Stock después del cambio
        tipo_movimiento: Tipo de movimiento
        usuario_nombre: Nombre del usuario que hizo el cambio
    """
    try:
        channel_layer = _get_channel_layer()
        if not channel_layer:
            logger.debug("Channel layer no disponible, omitiendo notificación WebSocket")
            return
        
        async_to_sync(channel_layer.group_send)(
            f"inventario_producto_{producto_id}",
            {
                "type": "inventario_actualizado",
                "data": {
                    "producto_id": producto_id,
                    "stock_anterior": float(stock_anterior),
                    "stock_posterior": float(stock_posterior),
                    "tipo_movimiento": tipo_movimiento,
                    "usuario": usuario_nombre,
                    "timestamp": timezone.now().isoformat(),
                }
            }
        )
        logger.debug(f"Cambio de inventario notificado para producto {producto_id}")
    except Exception as e:
        logger.error(f"Error notificando cambio de inventario: {str(e)}")


def notificar_nueva_venta(venta_data, vendedor_id):
    """
    Notifica sobre una nueva venta registrada.
    
    Args:
        venta_data: Dict con datos de la venta
        vendedor_id: ID del vendedor
    """
    try:
        channel_layer = _get_channel_layer()
        if not channel_layer:
            return
        
        # Notificar al vendedor específico
        async_to_sync(channel_layer.group_send)(
            f"ventas_vendedor_{vendedor_id}",
            {
                "type": "venta_registrada",
                "data": venta_data,
            }
        )
        
        # Notificar a supervisores (para ventas globales)
        async_to_sync(channel_layer.group_send)(
            "ventas_global",
            {
                "type": "venta_registrada",
                "data": venta_data,
            }
        )
        
        logger.info(f"Nueva venta notificada para vendedor {vendedor_id}")
    except Exception as e:
        logger.error(f"Error notificando nueva venta: {str(e)}")


def notificar_stock_critico(producto_id, producto_nombre, stock_actual, stock_minimo):
    """
    Notifica sobre un producto con stock crítico.
    
    Args:
        producto_id: ID del producto
        producto_nombre: Nombre del producto
        stock_actual: Stock actual
        stock_minimo: Stock mínimo
    """
    try:
        channel_layer = _get_channel_layer()
        if not channel_layer:
            return
        
        # Notificar a supervisores
        async_to_sync(channel_layer.group_send)(
            "notificaciones_global",
            {
                "type": "notificacion_stock_bajo",
                "mensaje": f"⚠️ Stock bajo: {producto_nombre} ({stock_actual:.2f} <= {stock_minimo:.2f})",
                "producto": producto_nombre,
                "stock_actual": float(stock_actual),
                "stock_minimo": float(stock_minimo),
            }
        )
        
        logger.warning(f"Stock crítico notificado: {producto_nombre}")
    except Exception as e:
        logger.error(f"Error notificando stock crítico: {str(e)}")


def notificar_vencimiento_proximo(producto_id, producto_nombre, fecha_vencimiento, dias_para_vencer):
    """
    Notifica sobre un producto próximo a vencer.
    
    Args:
        producto_id: ID del producto
        producto_nombre: Nombre del producto
        fecha_vencimiento: Fecha de vencimiento
        dias_para_vencer: Días faltantes para vencer
    """
    try:
        channel_layer = _get_channel_layer()
        if not channel_layer:
            return
        
        # Notificar a supervisores
        async_to_sync(channel_layer.group_send)(
            "notificaciones_global",
            {
                "type": "notificacion_vencimiento",
                "mensaje": f"⏰ Vencimiento próximo: {producto_nombre} ({dias_para_vencer} días)",
                "producto": producto_nombre,
                "fecha_vencimiento": str(fecha_vencimiento),
                "dias_para_vencer": dias_para_vencer,
            }
        )
        
        logger.warning(f"Vencimiento próximo notificado: {producto_nombre}")
    except Exception as e:
        logger.error(f"Error notificando vencimiento próximo: {str(e)}")


def notificar_alerta(titulo, mensaje, nivel="warning", usuario_id=None):
    """
    Envía una notificación de alerta genérica.
    
    Args:
        titulo: Título de la alerta
        mensaje: Mensaje de la alerta
        nivel: Nivel de la alerta (info, warning, error)
        usuario_id: ID del usuario (si None, envía a todos)
    """
    try:
        channel_layer = _get_channel_layer()
        if not channel_layer:
            return
        
        grupo = f"notificaciones_usuario_{usuario_id}" if usuario_id else "notificaciones_global"
        
        async_to_sync(channel_layer.group_send)(
            grupo,
            {
                "type": "notificacion_alerta",
                "titulo": titulo,
                "mensaje": mensaje,
                "nivel": nivel,
            }
        )
        
        logger.info(f"Alerta enviada [{nivel}]: {titulo}")
    except Exception as e:
        logger.error(f"Error enviando alerta: {str(e)}")


def obtener_estado_inventario_json(producto=None):
    """
    Obtiene el estado actual del inventario en formato JSON para WebSocket.
    
    Args:
        producto: Instancia de Producto (si None, retorna todos)
    
    Returns:
        Dict con estado del inventario
    """
    from .models import EstadoInventarioCentralizado
    from .serializers import EstadoInventarioCentralizadoSerializer
    
    if producto:
        try:
            estado = EstadoInventarioCentralizado.objects.select_related(
                "producto", "usuario_actualizo"
            ).get(producto=producto)
            return EstadoInventarioCentralizadoSerializer(estado).data
        except EstadoInventarioCentralizado.DoesNotExist:
            return None
    
    estados = EstadoInventarioCentralizado.objects.select_related(
        "producto", "usuario_actualizo"
    ).order_by("-ultima_actualizacion")
    
    return EstadoInventarioCentralizadoSerializer(estados, many=True).data
