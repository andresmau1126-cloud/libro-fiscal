"""
Señales para sincronización automática del inventario centralizado.
Se ejecutan automáticamente cuando se crean, actualizan o venden productos.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import Producto, Venta, EstadoInventarioCentralizado, HistorialInventario
from .services import InventarioCentralizadoService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Producto)
def actualizar_estado_centralizado_producto(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza un producto, actualizar su estado centralizado.
    """
    try:
        if created:
            # Crear estado centralizado para nuevo producto
            EstadoInventarioCentralizado.objects.get_or_create(
                producto=instance,
                defaults={
                    "stock_disponible": instance.stock_actual,
                    "es_critico": instance.stock_actual <= instance.stock_minimo,
                }
            )
        else:
            # Actualizar estado si el producto fue modificado
            InventarioCentralizadoService.actualizar_estado_centralizado(instance)
        
        logger.info(f"Estado centralizado actualizado para producto: {instance.nombre}")
    except Exception as e:
        logger.error(f"Error actualizando estado centralizado: {str(e)}")


@receiver(post_save, sender=Venta)
def procesar_venta_historial(sender, instance, created, **kwargs):
    """
    Cuando se crea una venta, registrar su historial automáticamente.
    """
    try:
        if created:
            from .models import HistorialVentas
            
            # Verificar que no haya sido registrada ya
            if not HistorialVentas.objects.filter(venta=instance).exists():
                InventarioCentralizadoService.registrar_venta_historial(
                    venta=instance,
                    vendedor=instance.vendedor,
                )
                logger.info(f"Venta #{instance.id} registrada en historial")
    except Exception as e:
        logger.error(f"Error registrando venta en historial: {str(e)}")


@receiver(post_save, sender=HistorialInventario)
def notificar_cambio_inventario(sender, instance, created, **kwargs):
    """
    Cuando se registra un movimiento de inventario, enviar notificaciones.
    """
    if not created:
        return
    
    try:
        # Notificar a gerentes, admins y auditores sobre cambios en inventario
        if instance.producto.stock_actual <= instance.producto.stock_minimo:
            # Usar función de utilidad segura
            from .websocket_utils import notificar_stock_critico
            
            notificar_stock_critico(
                instance.producto.id,
                instance.producto.nombre,
                instance.producto.stock_actual,
                instance.producto.stock_minimo
            )
            
            logger.warning(
                f"Stock bajo notificado para {instance.producto.nombre}: "
                f"{instance.producto.stock_actual} <= {instance.producto.stock_minimo}"
            )
        
        # Notificar cambio en producto específico
        from .websocket_utils import notificar_cambio_inventario as notif_cambio
        
        notif_cambio(
            instance.producto.id,
            instance.cantidad_anterior,
            instance.cantidad_posterior,
            instance.tipo_movimiento,
            instance.usuario.nombre if instance.usuario else "Sistema"
        )
        
    except Exception as e:
        logger.error(f"Error notificando cambio de inventario: {str(e)}")
