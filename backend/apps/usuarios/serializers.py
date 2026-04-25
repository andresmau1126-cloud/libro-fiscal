import re
from rest_framework import serializers
from .models import Usuario

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UsuarioSerializer(serializers.ModelSerializer):
    preferences = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ["id", "nombre", "email", "rol", "activo", "preferences", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_preferences(self, obj):
        return {
            "email_notifications": obj.pref_email_notifications,
            "currency": obj.pref_currency,
            "timezone": obj.pref_timezone,
        }


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


class UsuarioPreferencesUpdateSerializer(serializers.Serializer):
    email_notifications = serializers.BooleanField(required=False)
    currency = serializers.ChoiceField(choices=["GTQ", "USD", "COP"], required=False)
    timezone = serializers.ChoiceField(choices=["GMT-6", "GMT-5", "GMT-4"], required=False)
