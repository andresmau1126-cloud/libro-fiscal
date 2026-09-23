from rest_framework import serializers

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nombre", "nit", "telefono", "direccion", "activo"]

    def validate_nit(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El NIT es obligatorio.")
        return value


class ClienteCreateSerializer(ClienteSerializer):
    class Meta(ClienteSerializer.Meta):
        read_only_fields = ["id", "activo"]
