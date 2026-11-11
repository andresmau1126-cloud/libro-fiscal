from rest_framework import serializers
from .models import Expense, Provider, SellerStats


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["id", "nombre", "nit", "telefono", "direccion", "activo"]


class ExpenseSerializer(serializers.ModelSerializer):
    provider_nombre = serializers.SerializerMethodField()
    sello_digital = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id", "provider", "provider_nombre", "descripcion", "fecha",
            "descripcion_producto", "valor_unitario", "valor_pagado", "cantidad", "libro",
            "sello_digital", "es_simulado", "es_real_cuaderno", "proveedor_referencia", "folio", "soporte", "justificacion",
        ]

    def get_sello_digital(self, obj):
        return getattr(obj, "sello_digital", "")

    def get_provider_nombre(self, obj):
        return obj.proveedor_referencia or (obj.provider.nombre if obj.provider else "")

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        es_simulado = attrs.get("es_simulado", getattr(instance, "es_simulado", False))
        es_real_cuaderno = attrs.get("es_real_cuaderno", getattr(instance, "es_real_cuaderno", False))
        if es_simulado and es_real_cuaderno:
            raise serializers.ValidationError("Un egreso real de cuaderno no puede ser simulado.")
        if es_simulado and not attrs.get("proveedor_referencia", getattr(instance, "proveedor_referencia", "")):
            raise serializers.ValidationError({"proveedor_referencia": "Indique el proveedor que representa esta simulación."})
        if es_real_cuaderno and not attrs.get("proveedor_referencia", getattr(instance, "proveedor_referencia", "")):
            raise serializers.ValidationError({"proveedor_referencia": "Indique el proveedor de referencia del cuaderno."})
        if not es_simulado and not es_real_cuaderno and not attrs.get("provider", getattr(instance, "provider", None)):
            raise serializers.ValidationError({"provider": "Seleccione un proveedor para un egreso real."})
        for field in ("valor_unitario", "valor_pagado", "cantidad"):
            if attrs.get(field) is not None and attrs[field] <= 0:
                raise serializers.ValidationError({field: "Debe ser mayor que cero."})
        return attrs


class SellerStatsSerializer(serializers.ModelSerializer):
    vendedor_nombre = serializers.CharField(source="vendedor.nombre", read_only=True)

    class Meta:
        model = SellerStats
        fields = ["vendedor_id", "vendedor_nombre", "period", "period_start", "total_vendido", "cantidad_ventas", "ticket_promedio"]
