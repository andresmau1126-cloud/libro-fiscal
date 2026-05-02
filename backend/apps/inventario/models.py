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
