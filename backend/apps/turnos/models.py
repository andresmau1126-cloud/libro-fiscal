from django.conf import settings
from django.db import models
from django.utils import timezone


class Turno(models.Model):
    ESTADO_CHOICES = [("abierto", "Abierto"), ("cerrado", "Cerrado")]

    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="turnos"
    )
    vendedor_nombre = models.CharField(max_length=150, blank=True, default="")
    fecha = models.DateField()
    # Editable por gerente/admin al forzar apertura o cierre; por defecto usa la hora actual.
    hora_entrada = models.DateTimeField(default=timezone.now)
    hora_salida = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="abierto")
    caja_inicial = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    ventas_dia = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_entregado = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    faltante = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "turnos"
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["vendedor", "fecha"], name="idx_turno_vendedor_fecha"),
            models.Index(fields=["estado"], name="idx_turno_estado"),
        ]

    def save(self, *args, **kwargs):
        # Denormaliza el nombre para reportes rápidos sin joins.
        if self.vendedor_id:
            self.vendedor_nombre = self.vendedor.nombre
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Turno {self.vendedor_nombre} {self.fecha} ({self.estado})"
