from django.db import models
from django.conf import settings
import json
from datetime import datetime


class PuntoControl(models.Model):
    """Modelo para almacenar puntos de control (backups) del sistema"""
    
    ESTADO_CHOICES = [
        ('completado', 'Completado'),
        ('en_proceso', 'En Proceso'),
        ('fallido', 'Fallido'),
    ]
    
    TIPO_CHOICES = [
        ('base_datos', 'Base de Datos'),
        ('configuracion', 'Configuración'),
        ('completo', 'Completo'),
    ]
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=255,
        help_text="Nombre descriptivo del punto de control"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción detallada del punto de control"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='completo',
        help_text="Tipo de respaldo realizado"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='en_proceso',
        help_text="Estado actual del respaldo"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación del respaldo"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        help_text="Última fecha de modificación"
    )
    fecha_restauracion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de la última restauración"
    )
    
    # Información del respaldo
    tamano_archivo = models.BigIntegerField(
        default=0,
        help_text="Tamaño del archivo de respaldo en bytes"
    )
    ruta_archivo = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Ruta del archivo de respaldo"
    )
    
    # Usuario que creó el respaldo
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='respaldos_creados',
        help_text="Usuario que creó el respaldo"
    )
    
    # Usuario que restauró el respaldo
    usuario_restaurador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='respaldos_restaurados',
        help_text="Usuario que restauró el respaldo"
    )
    
    # Información adicional
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Información adicional del respaldo en formato JSON"
    )
    
    es_automatico = models.BooleanField(
        default=False,
        help_text="Indica si el respaldo fue creado automáticamente"
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Punto de Control'
        verbose_name_plural = 'Puntos de Control'
        indexes = [
            models.Index(fields=['-fecha_creacion']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"
    
    @property
    def tamano_legible(self):
        """Retorna el tamaño del archivo en formato legible"""
        for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
            if self.tamano_archivo < 1024.0:
                return f"{self.tamano_archivo:.2f} {unidad}"
            self.tamano_archivo /= 1024.0
        return f"{self.tamano_archivo:.2f} PB"
    
    def marcar_completado(self, tamano=0):
        """Marca el respaldo como completado"""
        self.estado = 'completado'
        self.tamano_archivo = tamano
        self.save()
    
    def marcar_fallido(self):
        """Marca el respaldo como fallido"""
        self.estado = 'fallido'
        self.save()


class RegistroRestauracion(models.Model):
    """Modelo para auditar las restauraciones realizadas"""
    
    punto_control = models.ForeignKey(
        PuntoControl,
        on_delete=models.CASCADE,
        related_name='registros_restauracion',
        help_text="Punto de control que fue restaurado"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Usuario que realizó la restauración"
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la restauración"
    )
    duracion_segundos = models.FloatField(
        null=True,
        blank=True,
        help_text="Duración de la restauración en segundos"
    )
    exitoso = models.BooleanField(
        default=True,
        help_text="Indica si la restauración fue exitosa"
    )
    mensaje_error = models.TextField(
        blank=True,
        null=True,
        help_text="Mensaje de error si la restauración falló"
    )
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas adicionales sobre la restauración"
    )
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Registro de Restauración'
        verbose_name_plural = 'Registros de Restauración'
        indexes = [
            models.Index(fields=['-fecha']),
            models.Index(fields=['punto_control']),
        ]
    
    def __str__(self):
        return f"Restauración de {self.punto_control.nombre} - {self.fecha}"
