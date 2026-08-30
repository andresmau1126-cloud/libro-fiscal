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

    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=180, blank=True, default="")
    medio_pago = models.CharField(max_length=20, choices=MEDIOS_PAGO, default="efectivo")
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
