"""
Servicios para gestionar inventario centralizado en tiempo real y rastreo de historial.
Proporciona funciones para actualizar inventario, registrar cambios y calcular estadísticas.
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from django.db.models import F, Sum, Q
from django.contrib.auth import get_user_model

from .models import (
    HistorialInventario,
    HistorialVentas,
    EstadoInventarioCentralizado,
    ResumenVentasPorVendedor,
    Producto,
    Venta,
    DetalleVenta,
)

Usuario = get_user_model()


class InventarioCentralizadoService:
    """
    Servicio para gestionar inventario centralizado en tiempo real.
    Mantiene sincronización entre todos los usuarios.
    """

    @staticmethod
    @transaction.atomic
    def registrar_movimiento_inventario(
        producto,
        tipo_movimiento,
        cantidad_movida,
        usuario,
        venta=None,
        vendedor=None,
        razon="",
        ip_usuario=None
    ):
        """
        Registra un movimiento de inventario en el historial.
        
        Args:
            producto: Instancia de Producto
            tipo_movimiento: Tipo de movimiento (entrada, venta, ajuste, devolucion, perdida)
            cantidad_movida: Cantidad del movimiento
            usuario: Usuario que realiza la acción
            venta: Venta asociada (si aplica)
            vendedor: Vendedor (si es una venta)
            razon: Razón del movimiento
            ip_usuario: IP del usuario
        
        Returns:
            HistorialInventario instance
        """
        cantidad_anterior = producto.stock_actual
        cantidad_posterior = cantidad_anterior + cantidad_movida

        historial = HistorialInventario.objects.create(
            producto=producto,
            tipo_movimiento=tipo_movimiento,
            cantidad_anterior=cantidad_anterior,
            cantidad_movida=cantidad_movida,
            cantidad_posterior=cantidad_posterior,
            usuario=usuario,
            vendedor=vendedor,
            venta=venta,
            razon=razon,
            ip_usuario=ip_usuario,
        )

        # Actualizar estado centralizado
        InventarioCentralizadoService.actualizar_estado_centralizado(
            producto, usuario
        )

        return historial

    @staticmethod
    @transaction.atomic
    def actualizar_estado_centralizado(producto, usuario=None):
        """
        Actualiza el estado centralizado del inventario.
        
        Args:
            producto: Instancia de Producto
            usuario: Usuario que actualiza (opcional)
        """
        try:
            estado = EstadoInventarioCentralizado.objects.select_for_update().get(
                producto=producto
            )
        except EstadoInventarioCentralizado.DoesNotExist:
            estado = EstadoInventarioCentralizado.objects.create(
                producto=producto,
                stock_disponible=producto.stock_actual,
                usuario_actualizo=usuario,
            )
            return estado

        # Usar versión para control de concurrencia optimista
        estado.stock_disponible = producto.stock_actual
        estado.usuario_actualizo = usuario
        estado.version = F("version") + 1
        estado.es_critico = producto.stock_actual <= producto.stock_minimo
        estado.ultima_actualizacion = timezone.now()
        estado.save(update_fields=[
            "stock_disponible",
            "usuario_actualizo",
            "version",
            "es_critico",
            "ultima_actualizacion",
        ])

        # Refresh para obtener versión actualizada
        estado.refresh_from_db()
        return estado

    @staticmethod
    @transaction.atomic
    def registrar_venta_historial(venta, vendedor, ip_usuario=None, dispositivo=""):
        """
        Registra una venta en el historial de ventas con todas las métricas.
        
        Args:
            venta: Instancia de Venta
            vendedor: Usuario vendedor
            ip_usuario: IP del cliente
            dispositivo: Información del dispositivo
        
        Returns:
            HistorialVentas instance
        """
        detalles = venta.detalles.select_related("producto").all()

        cantidad_productos = detalles.count()
        cantidad_total_unidades = Decimal(0)
        monto_costo = Decimal(0)

        for detalle in detalles:
            cantidad_total_unidades += detalle.cantidad
            monto_costo += detalle.cantidad * detalle.producto.costo_unitario

        ganancia = venta.total - monto_costo
        margen_ganancia = (
            ((ganancia / venta.total) * 100) if venta.total > 0 else Decimal(0)
        )

        # Usar get_or_create para evitar duplicados si el signal ya lo creó
        historial, created = HistorialVentas.objects.get_or_create(
            venta=venta,
            defaults={
                "vendedor": vendedor,
                "cantidad_productos": cantidad_productos,
                "cantidad_total_unidades": cantidad_total_unidades,
                "monto_total": venta.total,
                "monto_costo": monto_costo,
                "ganancia": ganancia,
                "margen_ganancia": margen_ganancia,
                "cliente": venta.cliente,
                "medio_pago": venta.medio_pago,
                "ip_usuario": ip_usuario,
                "dispositivo": dispositivo,
            }
        )
        
        # Si ya existía, actualizar datos
        if not created:
            historial.cantidad_productos = cantidad_productos
            historial.cantidad_total_unidades = cantidad_total_unidades
            historial.monto_costo = monto_costo
            historial.ganancia = ganancia
            historial.margen_ganancia = margen_ganancia
            historial.save(update_fields=[
                "cantidad_productos",
                "cantidad_total_unidades",
                "monto_costo",
                "ganancia",
                "margen_ganancia"
            ])

        # Actualizar resumen diario
        InventarioCentralizadoService.actualizar_resumen_diario(vendedor)

        return historial

    @staticmethod
    @transaction.atomic
    def actualizar_resumen_diario(vendedor):
        """
        Actualiza el resumen de ventas diarias del vendedor.
        
        Args:
            vendedor: Usuario vendedor
        """
        hoy = timezone.now().date()

        resumen, created = ResumenVentasPorVendedor.objects.select_for_update().get_or_create(
            vendedor=vendedor,
            fecha=hoy,
        )

        # Calcular métricas del día
        historial_hoy = HistorialVentas.objects.filter(
            vendedor=vendedor,
            fecha_venta__date=hoy,
        )

        resumen.cantidad_ventas = historial_hoy.count()
        resumen.cantidad_unidades = (
            historial_hoy.aggregate(Sum("cantidad_total_unidades"))[
                "cantidad_total_unidades__sum"
            ] or Decimal(0)
        )
        resumen.monto_total = (
            historial_hoy.aggregate(Sum("monto_total"))["monto_total__sum"] or Decimal(0)
        )
        resumen.monto_costo = (
            historial_hoy.aggregate(Sum("monto_costo"))["monto_costo__sum"] or Decimal(0)
        )
        resumen.ganancia_total = resumen.monto_total - resumen.monto_costo
        resumen.margen_promedio = (
            ((resumen.ganancia_total / resumen.monto_total) * 100)
            if resumen.monto_total > 0
            else Decimal(0)
        )

        resumen.save()
        return resumen

    @staticmethod
    def obtener_inventario_centralizado(filtro_critico=False):
        """
        Obtiene el estado centralizado del inventario.
        
        Args:
            filtro_critico: Si es True, retorna solo productos con stock crítico
        
        Returns:
            QuerySet de EstadoInventarioCentralizado
        """
        qs = EstadoInventarioCentralizado.objects.select_related(
            "producto", "usuario_actualizo"
        )

        if filtro_critico:
            qs = qs.filter(es_critico=True)

        return qs.order_by("-ultima_actualizacion")

    @staticmethod
    def obtener_historial_inventario_por_producto(producto_id, dias=30):
        """
        Obtiene el historial de movimientos de un producto.
        
        Args:
            producto_id: ID del producto
            dias: Últimos N días a buscar
        
        Returns:
            QuerySet de HistorialInventario
        """
        fecha_inicio = timezone.now() - timedelta(days=dias)

        return HistorialInventario.objects.filter(
            producto_id=producto_id,
            fecha__gte=fecha_inicio,
        ).select_related("producto", "usuario", "vendedor").order_by("-fecha")

    @staticmethod
    def obtener_historial_ventas_vendedor(vendedor_id, dias=30):
        """
        Obtiene el historial de ventas de un vendedor.
        
        Args:
            vendedor_id: ID del vendedor
            dias: Últimos N días a buscar
        
        Returns:
            QuerySet de HistorialVentas
        """
        fecha_inicio = timezone.now() - timedelta(days=dias)

        return HistorialVentas.objects.filter(
            vendedor_id=vendedor_id,
            fecha_venta__gte=fecha_inicio,
        ).select_related("vendedor", "venta").order_by("-fecha_venta")

    @staticmethod
    def obtener_estadisticas_vendedor(vendedor_id):
        """
        Obtiene estadísticas completas de un vendedor.
        
        Args:
            vendedor_id: ID del vendedor
        
        Returns:
            Dict con estadísticas del vendedor
        """
        hoy = timezone.now().date()
        inicio_mes = hoy.replace(day=1)

        historial_hoy = HistorialVentas.objects.filter(
            vendedor_id=vendedor_id,
            fecha_venta__date=hoy,
        )

        historial_mes = HistorialVentas.objects.filter(
            vendedor_id=vendedor_id,
            fecha_venta__date__gte=inicio_mes,
        )

        estadisticas = {
            "vendedor_id": vendedor_id,
            "cantidad_ventas_hoy": historial_hoy.count(),
            "monto_vendido_hoy": float(
                historial_hoy.aggregate(Sum("monto_total"))["monto_total__sum"] or Decimal(0)
            ),
            "ganancia_hoy": float(
                historial_hoy.aggregate(Sum("ganancia"))["ganancia__sum"] or Decimal(0)
            ),
            "cantidad_ventas_mes": historial_mes.count(),
            "monto_vendido_mes": float(
                historial_mes.aggregate(Sum("monto_total"))["monto_total__sum"] or Decimal(0)
            ),
            "ganancia_mes": float(
                historial_mes.aggregate(Sum("ganancia"))["ganancia__sum"] or Decimal(0)
            ),
            "margen_promedio_mes": float(
                historial_mes.aggregate(Sum("margen_ganancia")) [
                    "margen_ganancia__sum"
                ] or Decimal(0) / max(historial_mes.count(), 1)
            ),
        }

        try:
            vendedor = Usuario.objects.get(id=vendedor_id)
            estadisticas["vendedor_nombre"] = vendedor.nombre
        except Usuario.DoesNotExist:
            estadisticas["vendedor_nombre"] = "Desconocido"

        return estadisticas

    @staticmethod
    def obtener_resumen_inventario_hoy():
        """
        Obtiene un resumen del estado actual del inventario.
        
        Returns:
            Dict con métricas agregadas
        """
        from django.db.models import DecimalField, Sum, F
        
        productos = Producto.objects.filter(activo=True)

        total_productos = productos.count()
        total_stock = productos.aggregate(Sum("stock_actual"))["stock_actual__sum"] or Decimal(0)
        total_valor = (
            productos.aggregate(
                valor=Sum(F("stock_actual") * F("precio_venta"), output_field=DecimalField())
            )["valor"] or Decimal(0)
        )
        
        productos_criticos = EstadoInventarioCentralizado.objects.filter(
            es_critico=True
        ).count()

        return {
            "total_productos": total_productos,
            "total_stock": float(total_stock),
            "valor_total": float(total_valor),
            "productos_criticos": productos_criticos,
            "timestamp": timezone.now().isoformat(),
        }


class VentasService:
    """Servicio para gestionar ventas y su registro en historial."""

    @staticmethod
    @transaction.atomic
    def crear_venta_con_historial(
        cliente,
        medio_pago,
        detalles_venta,
        vendedor,
        ip_usuario=None,
        dispositivo="",
    ):
        """
        Crea una venta y registra su historial automáticamente.
        
        Args:
            cliente: Nombre del cliente
            medio_pago: Método de pago
            detalles_venta: Lista de dict con {producto_id, cantidad}
            vendedor: Usuario vendedor
            ip_usuario: IP del usuario
            dispositivo: Información del dispositivo
        
        Returns:
            Venta instance
        
        Raises:
            ValueError: Si hay stock insuficiente o producto vencido
        """
        total = Decimal(0)
        detalles_data = []

        for item in detalles_venta:
            try:
                producto = Producto.objects.select_for_update().get(
                    pk=item["producto_id"], activo=True
                )
            except Producto.DoesNotExist:
                raise ValueError(f"Producto con ID {item['producto_id']} no existe")

            if producto.fecha_vencimiento and producto.fecha_vencimiento < timezone.localdate():
                raise ValueError(f"El producto {producto.nombre} está vencido")

            cantidad = Decimal(str(item["cantidad"]))
            if producto.stock_actual < cantidad:
                raise ValueError(
                    f"Stock insuficiente para {producto.nombre}. "
                    f"Disponible: {producto.stock_actual}"
                )

            subtotal = cantidad * producto.precio_venta
            detalles_data.append(
                (producto, cantidad, producto.precio_venta, subtotal)
            )
            total += subtotal

        # Crear venta
        venta = Venta.objects.create(
            cliente=cliente,
            medio_pago=medio_pago,
            total=total,
            vendedor=vendedor,
        )

        # Actualizar productos y crear detalles
        for producto, cantidad, precio, subtotal in detalles_data:
            producto.stock_actual -= cantidad
            producto.save(update_fields=["stock_actual", "updated_at"])

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=subtotal,
            )

            # Registrar en historial
            InventarioCentralizadoService.registrar_movimiento_inventario(
                producto=producto,
                tipo_movimiento="venta",
                cantidad_movida=-cantidad,
                usuario=vendedor,
                venta=venta,
                vendedor=vendedor,
                razon=f"Venta a {cliente}",
                ip_usuario=ip_usuario,
            )

        # Registrar en historial de ventas
        InventarioCentralizadoService.registrar_venta_historial(
            venta=venta,
            vendedor=vendedor,
            ip_usuario=ip_usuario,
            dispositivo=dispositivo,
        )

        return venta
