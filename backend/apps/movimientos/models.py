from django.db import models
from apps.libros.models import Libro


class Movimiento(models.Model):
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    nombre = models.CharField(max_length=200, null=True, blank=True)
    ingresos = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    egresos = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    libro = models.ForeignKey(
        Libro, on_delete=models.CASCADE,
        related_name="movimientos", null=True, blank=True,
    )

    class Meta:
        db_table = "movimientos"
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"
        ordering = ["fecha", "id"]
        indexes = [
            models.Index(fields=["libro"], name="idx_mov_libro"),
            models.Index(fields=["nombre", "fecha"], name="idx_mov_nombre_fecha"),
        ]

    def save(self, *args, **kwargs):
        # Sync nombre from libro (replaces trigger)
        if self.libro_id:
            try:
                self.nombre = self.libro.nombre
            except Libro.DoesNotExist:
                self.nombre = None
        else:
            self.nombre = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} — {self.descripcion} (I:{self.ingresos} E:{self.egresos})"
