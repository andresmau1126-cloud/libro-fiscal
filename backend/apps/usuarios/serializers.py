from rest_framework import serializers
from .models import Usuario, OTP


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "nombre", "email", "rol", "activo", "created_at"]
        read_only_fields = ["id", "created_at"]


class RegisterSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    def validate_email(self, value):
        if Usuario.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Este email ya está registrado")
        return value.lower()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    codigo = serializers.CharField(max_length=6, required=True)


class UsuarioCreateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    rol = serializers.ChoiceField(choices=["admin", "usuario"], required=False)

    def validate_email(self, value):
        if Usuario.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Este email ya está registrado")
        return value.lower()


class UsuarioUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    rol = serializers.ChoiceField(choices=["admin", "usuario"], required=False)
    activo = serializers.BooleanField(required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=6)


class VerifyRegistrationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)


class ResendRegistrationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UsuarioPreferencesUpdateSerializer(serializers.Serializer):
    email_notifications = serializers.BooleanField(required=False)
    currency = serializers.CharField(max_length=3, required=False)
    timezone = serializers.CharField(max_length=10, required=False)
