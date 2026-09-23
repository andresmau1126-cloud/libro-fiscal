from rest_framework import serializers

from .models import Cliente
from .utils import normalizar_nit


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nombre", "nit", "telefono", "direccion", "activo"]

    def validate_nit(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El NIT es obligatorio.")
        return value

    def validate(self, attrs):
        nit_normalizado = normalizar_nit(attrs.get("nit", getattr(self.instance, "nit", "")))
        query = Cliente.objects.filter(nit_normalizado=nit_normalizado)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError({"nit": "Ya existe un cliente con ese NIT, aunque esté escrito con otro formato."})
        return attrs


class ClienteCreateSerializer(ClienteSerializer):
    class Meta(ClienteSerializer.Meta):
        read_only_fields = ["id", "activo"]
