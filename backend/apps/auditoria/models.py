from django.db import models
from apps.usuarios.models import Usuario


class Auditoria(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="auditorias",
    )
    accion = models.CharField(max_length=50)
    entidad = models.CharField(max_length=50)
    entidad_id = models.BigIntegerField(null=True, blank=True)
    detalle = models.JSONField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auditoria"
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.accion} {self.entidad} #{self.entidad_id} — {self.created_at}"
