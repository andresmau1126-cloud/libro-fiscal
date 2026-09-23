from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=180)
    nit = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=40, blank=True, default="")
    direccion = models.CharField(max_length=255, blank=True, default="")
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clientes"
        ordering = ["nombre", "id"]

    def __str__(self):
        return f"{self.nombre} ({self.nit})"
