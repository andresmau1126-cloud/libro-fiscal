from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "telefono", "activo")
    search_fields = ("nombre", "nit")
