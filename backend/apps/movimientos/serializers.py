from rest_framework import serializers


class MovimientoSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    fecha = serializers.DateField(format="%Y-%m-%d")
    dia = serializers.SerializerMethodField()
    descripcion = serializers.CharField()
    ingresos = serializers.FloatField()
    egresos = serializers.FloatField()
    saldo = serializers.FloatField()

    def get_dia(self, obj):
        if hasattr(obj, "fecha"):
            return obj.fecha.day
        return 0


class MovimientoCreateSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    descripcion = serializers.CharField(min_length=1, max_length=255)
    ingresos = serializers.DecimalField(max_digits=14, decimal_places=2, default=0)
    egresos = serializers.DecimalField(max_digits=14, decimal_places=2, default=0)
    libro_id = serializers.IntegerField(required=True)

    def validate(self, data):
        ingresos = data.get("ingresos", 0) or 0
        egresos = data.get("egresos", 0) or 0

        if ingresos < 0 or egresos < 0:
            raise serializers.ValidationError("ingresos/egresos no pueden ser negativos")
        if ingresos == 0 and egresos == 0:
            raise serializers.ValidationError("Debe registrar un monto mayor a 0")
        if ingresos > 0 and egresos > 0:
            raise serializers.ValidationError("Solo puede existir ingreso o egreso en un mismo movimiento")
        return data


class MovimientoUpdateSerializer(serializers.Serializer):
    fecha = serializers.DateField()
    descripcion = serializers.CharField(min_length=1, max_length=255)
    ingresos = serializers.DecimalField(max_digits=14, decimal_places=2, default=0)
    egresos = serializers.DecimalField(max_digits=14, decimal_places=2, default=0)

    def validate(self, data):
        ingresos = data.get("ingresos", 0) or 0
        egresos = data.get("egresos", 0) or 0

        if ingresos < 0 or egresos < 0:
            raise serializers.ValidationError("ingresos/egresos no pueden ser negativos")
        if ingresos == 0 and egresos == 0:
            raise serializers.ValidationError("Debe registrar un monto mayor a 0")
        if ingresos > 0 and egresos > 0:
            raise serializers.ValidationError("Solo puede existir ingreso o egreso en un mismo movimiento")
        return data
