from django.db import models
from django.conf import settings


class Libro(models.Model):
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=50)
    anio = models.IntegerField()
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="libros",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "libro"
        verbose_name = "Libro Fiscal"
        verbose_name_plural = "Libros Fiscales"
        constraints = [
            models.UniqueConstraint(fields=["propietario", "nit", "anio"], name="uniq_libro_owner"),
            models.UniqueConstraint(fields=["propietario", "nombre", "anio"], name="uniq_libro_owner_nombre_anio"),
        ]
        ordering = ["-anio", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.nit}) - {self.anio}"
