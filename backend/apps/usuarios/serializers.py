import re
from rest_framework import serializers
from .models import Usuario

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "nombre", "email", "rol", "activo", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UsuarioCreateSerializer(serializers.Serializer):
    nombre = serializers.CharField(min_length=2, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    rol = serializers.ChoiceField(choices=["admin", "usuario"], default="usuario")

    def validate_email(self, value):
        value = value.strip().lower()
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está registrado")
        return value


class UsuarioUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(min_length=2, max_length=150, required=False)
    email = serializers.EmailField(required=False)
    rol = serializers.ChoiceField(choices=["admin", "usuario"], required=False)
    activo = serializers.BooleanField(required=False)
    password = serializers.CharField(min_length=6, required=False, write_only=True)


class RegisterSerializer(serializers.Serializer):
    nombre = serializers.CharField(min_length=2, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("El email ya está registrado")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
