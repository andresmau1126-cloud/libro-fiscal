from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PuntoControl, RegistroRestauracion


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegistroRestauracionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = RegistroRestauracion
        fields = [
            'id',
            'punto_control',
            'usuario',
            'usuario_nombre',
            'fecha',
            'duracion_segundos',
            'exitoso',
            'mensaje_error',
            'notas',
        ]
        read_only_fields = [
            'id',
            'fecha',
            'usuario_nombre',
        ]


class PuntoControlSerializer(serializers.ModelSerializer):
    usuario_creador_nombre = serializers.CharField(
        source='usuario_creador.get_full_name',
        read_only=True
    )
    usuario_restaurador_nombre = serializers.CharField(
        source='usuario_restaurador.get_full_name',
        read_only=True,
        allow_null=True
    )
    registros_restauracion = RegistroRestauracionSerializer(
        many=True,
        read_only=True
    )
    tamano_legible = serializers.SerializerMethodField()
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    tipo_display = serializers.CharField(
        source='get_tipo_display',
        read_only=True
    )
    
    class Meta:
        model = PuntoControl
        fields = [
            'id',
            'nombre',
            'descripcion',
            'tipo',
            'tipo_display',
            'estado',
            'estado_display',
            'fecha_creacion',
            'fecha_modificacion',
            'fecha_restauracion',
            'tamano_archivo',
            'tamano_legible',
            'ruta_archivo',
            'usuario_creador',
            'usuario_creador_nombre',
            'usuario_restaurador',
            'usuario_restaurador_nombre',
            'metadata',
            'es_automatico',
            'registros_restauracion',
        ]
        read_only_fields = [
            'id',
            'fecha_creacion',
            'fecha_modificacion',
            'fecha_restauracion',
            'tamano_archivo',
            'usuario_creador',
            'usuario_restaurador',
            'registros_restauracion',
        ]
    
    def get_tamano_legible(self, obj):
        """Retorna el tamaño del archivo en formato legible"""
        tamano = obj.tamano_archivo
        for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
            if tamano < 1024.0:
                return f"{tamano:.2f} {unidad}"
            tamano /= 1024.0
        return f"{tamano:.2f} PB"
