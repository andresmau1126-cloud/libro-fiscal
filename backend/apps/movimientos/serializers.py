from rest_framework import serializers


class MovimientoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    fecha = serializers.DateField(format="%Y-%m-%d")
    dia = serializers.SerializerMethodField()
    descripcion = serializers.CharField()
    ingresos = serializers.FloatField()
    egresos = serializers.FloatField()
    saldo = serializers.FloatField()
    sello_digital = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()
    medio_pago = serializers.SerializerMethodField()
    turno = serializers.SerializerMethodField()

    def get_dia(self, obj):
        if hasattr(obj, "fecha"):
            return obj.fecha.day
        return 0

    def get_sello_digital(self, obj):
        return getattr(obj, "sello_digital", "")

    def get_tipo(self, obj):
        if getattr(obj, "venta_id", None):
            return "venta"
        try:
            if getattr(obj, "expense", None) is not None:
                return "egreso"
        except Exception:
            pass
        return "movimiento"

    def get_medio_pago(self, obj):
        if getattr(obj, "venta_id", None) and getattr(obj, "venta", None) is not None:
            return obj.venta.medio_pago
        return None

    def get_turno(self, obj):
        if getattr(obj, "venta_id", None) and getattr(obj, "venta", None) is not None:
            return obj.venta.turno
        return None


class MovimientoCreateSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    descripcion = serializers.CharField(min_length=1, max_length=255)
    ingresos = serializers.DecimalField(max_digits=14, decimal_places=2, default=0)
    egresos = serializers.DecimalField(max_digits=14, decimal_places=2, default=0)
    libro_id = serializers.IntegerField(required=True)

    def validate(self, data):
        ingresos = data.get("ingresos", 0) or 0
        egresos = data.get("egresos", 0) or 0

        if ingresos < 0:
            raise serializers.ValidationError("ingresos no pueden ser negativos")
        if egresos < 0:
            raise serializers.ValidationError("egresos no pueden ser negativos")
        if ingresos == 0 and egresos == 0:
            raise serializers.ValidationError("Debe registrar un monto mayor a 0")
        if ingresos > 0 and egresos > 0:
            raise serializers.ValidationError("Registre ingresos o egresos, no ambos")
        return data


class MovimientoUpdateSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    descripcion = serializers.CharField(min_length=1, max_length=255)
    ingresos = serializers.DecimalField(max_digits=14, decimal_places=2, default=0)
    egresos = serializers.DecimalField(max_digits=14, decimal_places=2, default=0)

    def validate(self, data):
        ingresos = data.get("ingresos", 0) or 0
        egresos = data.get("egresos", 0) or 0

        if ingresos < 0:
            raise serializers.ValidationError("ingresos no pueden ser negativos")
        if egresos < 0:
            raise serializers.ValidationError("egresos no pueden ser negativos")
        if ingresos == 0 and egresos == 0:
            raise serializers.ValidationError("Debe registrar un monto mayor a 0")
        if ingresos > 0 and egresos > 0:
            raise serializers.ValidationError("Registre ingresos o egresos, no ambos")
        return data
