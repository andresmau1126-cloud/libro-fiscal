from django.contrib import admin
from django.utils.html import format_html
from .models import PuntoControl, RegistroRestauracion


@admin.register(PuntoControl)
class PuntoControlAdmin(admin.ModelAdmin):
    list_display = [
        'nombre',
        'tipo_display',
        'estado_display',
        'fecha_creacion',
        'tamano_legible_display',
        'usuario_creador_display',
    ]
    list_filter = ['tipo', 'estado', 'fecha_creacion', 'es_automatico']
    search_fields = ['nombre', 'descripcion', 'usuario_creador__username']
    readonly_fields = [
        'fecha_creacion',
        'fecha_modificacion',
        'usuario_creador',
        'usuario_restaurador',
        'tamano_legible_display',
    ]
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'tipo', 'estado')
        }),
        ('Tipo de Respaldo', {
            'fields': ('es_automatico',)
        }),
        ('Información del Archivo', {
            'fields': ('ruta_archivo', 'tamano_archivo', 'tamano_legible_display')
        }),
        ('Auditoría', {
            'fields': (
                'usuario_creador',
                'fecha_creacion',
                'usuario_restaurador',
                'fecha_restauracion',
                'fecha_modificacion',
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def tipo_display(self, obj):
        return obj.get_tipo_display()
    tipo_display.short_description = 'Tipo'
    
    def estado_display(self, obj):
        colors = {
            'completado': 'green',
            'en_proceso': 'orange',
            'fallido': 'red',
        }
        color = colors.get(obj.estado, 'gray')
        return format_html(
            f'<span style="color: {color}; font-weight: bold;">{obj.get_estado_display()}</span>'
        )
    estado_display.short_description = 'Estado'
    
    def tamano_legible_display(self, obj):
        tamano = obj.tamano_archivo
        for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
            if tamano < 1024.0:
                return f"{tamano:.2f} {unidad}"
            tamano /= 1024.0
        return f"{tamano:.2f} PB"
    tamano_legible_display.short_description = 'Tamaño'
    
    def usuario_creador_display(self, obj):
        if obj.usuario_creador:
            return obj.usuario_creador.get_full_name() or obj.usuario_creador.username
        return '-'
    usuario_creador_display.short_description = 'Creado por'


@admin.register(RegistroRestauracion)
class RegistroRestauracionAdmin(admin.ModelAdmin):
    list_display = [
        'punto_control',
        'usuario_display',
        'fecha',
        'exitoso_display',
        'duracion_display',
    ]
    list_filter = ['exitoso', 'fecha']
    search_fields = ['punto_control__nombre', 'usuario__username']
    readonly_fields = ['fecha']
    
    def usuario_display(self, obj):
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return '-'
    usuario_display.short_description = 'Usuario'
    
    def exitoso_display(self, obj):
        color = 'green' if obj.exitoso else 'red'
        texto = 'Exitoso ✓' if obj.exitoso else 'Fallido ✗'
        return format_html(
            f'<span style="color: {color}; font-weight: bold;">{texto}</span>'
        )
    exitoso_display.short_description = 'Resultado'
    
    def duracion_display(self, obj):
        if obj.duracion_segundos:
            return f"{obj.duracion_segundos:.2f}s"
        return '-'
    duracion_display.short_description = 'Duración'
