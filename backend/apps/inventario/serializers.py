from datetime import date
from decimal import Decimal
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


class VentaDetalleCreateSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField(min_value=1)
    cantidad = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))


class VentaCreateSerializer(serializers.Serializer):
    libro_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    cliente = serializers.CharField(max_length=180, required=False, allow_blank=True, default="")
    medio_pago = serializers.ChoiceField(choices=["efectivo", "transferencia", "tarjeta"], default="efectivo")
    turno = serializers.ChoiceField(choices=["mañana", "tarde", "noche"], default="mañana", required=False)
    detalles = VentaDetalleCreateSerializer(many=True, allow_empty=False)

    def validate_detalles(self, value):
        ids = [item["producto_id"] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("No repita productos; ajuste la cantidad en una sola línea.")
        return value


# ============================================================================
# SERIALIZERS PARA INVENTARIO CENTRALIZADO Y RASTREO
# ============================================================================

class HistorialInventarioSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    producto = serializers.CharField(source="producto.nombre")
    producto_id = serializers.IntegerField(source="producto.id")
    tipo_movimiento = serializers.CharField()
    cantidad_anterior = serializers.FloatField()
    cantidad_movida = serializers.FloatField()
    cantidad_posterior = serializers.FloatField()
    usuario = serializers.CharField(source="usuario.nombre")
    usuario_id = serializers.IntegerField(source="usuario.id")
    vendedor = serializers.SerializerMethodField()
    vendedor_id = serializers.SerializerMethodField()
    razon = serializers.CharField()
    fecha = serializers.DateTimeField()
    
    def get_vendedor(self, obj):
        return obj.vendedor.nombre if obj.vendedor else None
    
    def get_vendedor_id(self, obj):
        return obj.vendedor.id if obj.vendedor else None


class HistorialVentasSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    venta_id = serializers.IntegerField(source="venta.id")
    vendedor = serializers.CharField(source="vendedor.nombre")
    vendedor_id = serializers.IntegerField(source="vendedor.id")
    fecha_venta = serializers.DateTimeField()
    cantidad_productos = serializers.IntegerField()
    cantidad_total_unidades = serializers.FloatField()
    monto_total = serializers.FloatField()
    monto_costo = serializers.FloatField()
    ganancia = serializers.FloatField()
    margen_ganancia = serializers.FloatField()
    cliente = serializers.CharField()
    medio_pago = serializers.CharField()
    dispositivo = serializers.CharField()


class EstadoInventarioCentralizadoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    producto_id = serializers.IntegerField(source="producto.id")
    producto_nombre = serializers.CharField(source="producto.nombre")
    stock_disponible = serializers.FloatField()
    stock_minimo = serializers.FloatField(source="producto.stock_minimo")
    stock_actual = serializers.FloatField(source="producto.stock_actual")
    precio_venta = serializers.FloatField(source="producto.precio_venta")
    costo_unitario = serializers.FloatField(source="producto.costo_unitario")
    categoria = serializers.CharField(source="producto.categoria")
    es_critico = serializers.BooleanField()
    ultima_actualizacion = serializers.DateTimeField()
    usuario_actualizo = serializers.SerializerMethodField()
    version = serializers.IntegerField()
    
    def get_usuario_actualizo(self, obj):
        return obj.usuario_actualizo.nombre if obj.usuario_actualizo else None


class ResumenVentasPorVendedorSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    vendedor = serializers.CharField(source="vendedor.nombre")
    vendedor_id = serializers.IntegerField(source="vendedor.id")
    fecha = serializers.DateField()
    cantidad_ventas = serializers.IntegerField()
    cantidad_unidades = serializers.FloatField()
    monto_total = serializers.FloatField()
    monto_costo = serializers.FloatField()
    ganancia_total = serializers.FloatField()
    margen_promedio = serializers.FloatField()


class EstadisticasVendedorSerializer(serializers.Serializer):
    """Serializer para estadísticas consolidadas de un vendedor"""
    vendedor_id = serializers.IntegerField()
    vendedor_nombre = serializers.CharField()
    cantidad_ventas_hoy = serializers.IntegerField()
    monto_vendido_hoy = serializers.FloatField()
    ganancia_hoy = serializers.FloatField()
    cantidad_ventas_mes = serializers.IntegerField()
    monto_vendido_mes = serializers.FloatField()
    ganancia_mes = serializers.FloatField()
    margen_promedio_mes = serializers.FloatField()
