from django.conf import settings
from django.db import models


class Provider(models.Model):
    nombre = models.CharField(max_length=180, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "providers"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Expense(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT, related_name="expenses")
    descripcion = models.CharField(max_length=255)
    fecha = models.DateField()
    descripcion_producto = models.CharField(max_length=255)
    valor_unitario = models.DecimalField(max_digits=14, decimal_places=2)
    valor_pagado = models.DecimalField(max_digits=14, decimal_places=2)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    libro = models.ForeignKey("libros.Libro", on_delete=models.PROTECT, related_name="expenses")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="expenses_created")
    movimiento = models.OneToOneField("movimientos.Movimiento", on_delete=models.PROTECT, related_name="expense", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "expenses"
        ordering = ["-fecha", "-id"]


class SellerStats(models.Model):
    PERIOD_CHOICES = [("daily", "Diario"), ("monthly", "Mensual")]
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="seller_stats")
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    total_vendido = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    cantidad_ventas = models.PositiveIntegerField(default=0)
    ticket_promedio = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "seller_stats"
        constraints = [models.UniqueConstraint(fields=["vendedor", "period", "period_start"], name="uniq_seller_stats_period")]
        indexes = [models.Index(fields=["period", "period_start"])]
