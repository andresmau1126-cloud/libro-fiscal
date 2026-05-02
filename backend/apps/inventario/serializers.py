from datetime import date
from rest_framework import serializers


class ProductoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField()
    categoria = serializers.CharField()
    descripcion = serializers.CharField()
    stock_actual = serializers.FloatField()
    stock_minimo = serializers.FloatField()
    costo_unitario = serializers.FloatField()
    precio_venta = serializers.FloatField()
    fecha_vencimiento = serializers.DateField(allow_null=True)
    dias_alerta = serializers.IntegerField()
    stock_bajo = serializers.SerializerMethodField()
    vencido = serializers.SerializerMethodField()
    por_vencer = serializers.SerializerMethodField()
    dias_para_vencer = serializers.SerializerMethodField()

    def get_stock_bajo(self, obj):
        return obj.stock_actual <= obj.stock_minimo

    def get_vencido(self, obj):
        if not obj.fecha_vencimiento:
            return False
        return obj.fecha_vencimiento < date.today()

    def get_por_vencer(self, obj):
        if not obj.fecha_vencimiento:
            return False
        hoy = date.today()
        if obj.fecha_vencimiento < hoy:
            return False
        delta = (obj.fecha_vencimiento - hoy).days
        return delta <= obj.dias_alerta

    def get_dias_para_vencer(self, obj):
        if not obj.fecha_vencimiento:
            return None
        return (obj.fecha_vencimiento - date.today()).days


class ProductoCreateUpdateSerializer(serializers.Serializer):
    nombre = serializers.CharField(min_length=1, max_length=180)
    categoria = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    descripcion = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    stock_actual = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_minimo = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_unitario = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_venta = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_vencimiento = serializers.DateField(required=False, allow_null=True, default=None)
    dias_alerta = serializers.IntegerField(required=False, default=30, min_value=1)

    def validate(self, data):
        for field in ("stock_actual", "stock_minimo", "costo_unitario", "precio_venta"):
            if data.get(field, 0) < 0:
                raise serializers.ValidationError(f"{field} no puede ser negativo")
        return data
