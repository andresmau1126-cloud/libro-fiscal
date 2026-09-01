from django.conf import settings
from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=180)
    categoria = models.CharField(max_length=120, blank=True, default="")
    descripcion = models.CharField(max_length=255, blank=True, default="")
    stock_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    dias_alerta = models.IntegerField(default=30)
    activo = models.BooleanField(default=True)
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="productos",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventario_producto"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre", "id"]
        constraints = [
            models.UniqueConstraint(fields=["propietario", "nombre"], name="uniq_producto_owner_nombre"),
        ]

    def __str__(self):
        return self.nombre

    def delete(self, using=None, keep_parents=False):
        if self.activo:
            self.activo = False
            self.save(update_fields=["activo", "updated_at"])
            return (1, {self.__class__: 1})
        return (0, {self.__class__: 0})


class Venta(models.Model):
    MEDIOS_PAGO = [
        ("efectivo", "Efectivo"),
        ("transferencia", "Transferencia"),
        ("tarjeta", "Tarjeta"),
    ]
    TURNOS = [
        ("mañana", "Mañana (06:00 - 14:00)"),
        ("tarde", "Tarde (14:00 - 22:00)"),
        ("noche", "Noche (22:00 - 06:00)"),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=180, blank=True, default="")
    medio_pago = models.CharField(max_length=20, choices=MEDIOS_PAGO, default="efectivo")
    turno = models.CharField(max_length=10, choices=TURNOS, default="mañana")
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ventas",
    )

    class Meta:
        db_table = "inventario_venta"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"Venta #{self.id} - {self.total}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="detalles_venta")
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        db_table = "inventario_detalle_venta"
        ordering = ["id"]

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"


# ============================================================================
# MODELOS PARA INVENTARIO CENTRALIZADO EN TIEMPO REAL Y RASTREO DE HISTORIAL
# ============================================================================

class HistorialInventario(models.Model):
    """
    Registra cada cambio en el inventario (entradas, salidas, ajustes).
    Proporciona auditoría completa de movimientos de stock.
    """
    TIPO_MOVIMIENTO = [
        ("entrada", "Entrada de Stock"),
        ("venta", "Venta"),
        ("ajuste", "Ajuste Manual"),
        ("devolucion", "Devolución"),
        ("perdida", "Pérdida/Daño"),
    ]

    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="historial_inventario"
    )
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad_movida = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad_posterior = models.DecimalField(max_digits=12, decimal_places=2)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="historial_movimientos"
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ventas_realizadas_historial",
        help_text="Si el movimiento es una venta, aquí se registra el vendedor"
    )
    venta = models.ForeignKey(
        Venta, on_delete=models.SET_NULL, null=True, blank=True, related_name="historial_movimientos"
    )
    razon = models.CharField(
        max_length=255, blank=True, default="", help_text="Razón del movimiento"
    )
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_usuario = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = "inventario_historial_inventario"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["-fecha", "producto"]),
            models.Index(fields=["usuario", "-fecha"]),
            models.Index(fields=["tipo_movimiento", "-fecha"]),
        ]

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.producto.nombre} ({self.cantidad_movida}) - {self.fecha.strftime('%Y-%m-%d %H:%M')}"


class HistorialVentas(models.Model):
    """
    Historial detallado de ventas por vendedor.
    Permite rastrear todas las transacciones de cada vendedor.
    """
    venta = models.OneToOneField(
        Venta, on_delete=models.CASCADE, related_name="historial_venta"
    )
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="historial_ventas_detallado"
    )
    fecha_venta = models.DateTimeField(auto_now_add=True, db_index=True)
    cantidad_productos = models.IntegerField(default=0)
    cantidad_total_unidades = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    monto_costo = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, help_text="Costo total de productos vendidos"
    )
    ganancia = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, help_text="Monto de ganancia (total - costo)"
    )
    margen_ganancia = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Porcentaje de ganancia"
    )
    cliente = models.CharField(max_length=180, blank=True, default="")
    medio_pago = models.CharField(max_length=20, blank=True, default="")
    ip_usuario = models.GenericIPAddressField(null=True, blank=True)
    dispositivo = models.CharField(max_length=255, blank=True, default="")
    
    class Meta:
        db_table = "inventario_historial_ventas"
        ordering = ["-fecha_venta", "-id"]
        indexes = [
            models.Index(fields=["vendedor", "-fecha_venta"]),
            models.Index(fields=["-fecha_venta"]),
        ]

    def __str__(self):
        return f"Venta #{self.venta.id} - {self.vendedor.nombre} - ${self.monto_total}"


class EstadoInventarioCentralizado(models.Model):
    """
    Estado centralizado del inventario compartido en tiempo real.
    Permite a todos los usuarios (vendedores, gerente, admin) ver el mismo inventario actualizado.
    """
    producto = models.OneToOneField(
        Producto, on_delete=models.CASCADE, related_name="estado_centralizado"
    )
    stock_disponible = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True, db_index=True)
    usuario_actualizo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actualizaciones_inventario"
    )
    es_critico = models.BooleanField(
        default=False, help_text="Indica si el stock está por debajo del mínimo"
    )
    notificacion_enviada = models.BooleanField(
        default=False, help_text="Si ya se envió notificación por stock bajo"
    )
    version = models.BigIntegerField(
        default=0, help_text="Versión para control de concurrencia optimista"
    )
    
    class Meta:
        db_table = "inventario_estado_centralizado"
        verbose_name = "Estado Centralizado"
        verbose_name_plural = "Estados Centralizados"

    def __str__(self):
        return f"{self.producto.nombre} - Stock: {self.stock_disponible}"


class ResumenVentasPorVendedor(models.Model):
    """
    Resumen diario de ventas por vendedor.
    Permite seguimiento rápido del desempeño.
    """
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumen_ventas_diarias"
    )
    fecha = models.DateField(auto_now_add=True, db_index=True)
    cantidad_ventas = models.IntegerField(default=0)
    cantidad_unidades = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    monto_costo = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    ganancia_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    margen_promedio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        db_table = "inventario_resumen_ventas_vendedor"
        ordering = ["-fecha", "vendedor"]
        constraints = [
            models.UniqueConstraint(
                fields=["vendedor", "fecha"], name="uniq_resumen_vendedor_fecha"
            )
        ]
        indexes = [
            models.Index(fields=["vendedor", "-fecha"]),
            models.Index(fields=["-fecha"]),
        ]

    def __str__(self):
        return f"{self.vendedor.nombre} - {self.fecha}: ${self.monto_total}"
