from rest_framework import serializers
from .models import Expense, Provider, SellerStats


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["id", "nombre", "activo"]


class ExpenseSerializer(serializers.ModelSerializer):
    provider_nombre = serializers.CharField(source="provider.nombre", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id", "provider", "provider_nombre", "descripcion", "fecha",
            "descripcion_producto", "valor_unitario", "valor_pagado", "cantidad", "libro",
        ]

    def validate(self, attrs):
        for field in ("valor_unitario", "valor_pagado", "cantidad"):
            if attrs.get(field) is not None and attrs[field] <= 0:
                raise serializers.ValidationError({field: "Debe ser mayor que cero."})
        return attrs


class SellerStatsSerializer(serializers.ModelSerializer):
    vendedor_nombre = serializers.CharField(source="vendedor.nombre", read_only=True)

    class Meta:
        model = SellerStats
        fields = ["vendedor_id", "vendedor_nombre", "period", "period_start", "total_vendido", "cantidad_ventas", "ticket_promedio"]
