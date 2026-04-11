from django.db import models


class Libro(models.Model):
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=50)
    anio = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "libro"
        verbose_name = "Libro Fiscal"
        verbose_name_plural = "Libros Fiscales"
        constraints = [
            models.UniqueConstraint(fields=["nit", "anio"], name="uniq_libro"),
            models.UniqueConstraint(fields=["nombre", "anio"], name="uniq_libro_nombre_anio"),
        ]
        ordering = ["-anio", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.nit}) - {self.anio}"
