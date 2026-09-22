from django.contrib import admin

from .models import Turno


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ("id", "vendedor_nombre", "fecha", "estado", "caja_inicial", "ventas_dia", "total_entregado", "faltante")
    list_filter = ("estado", "fecha")
    search_fields = ("vendedor_nombre",)
