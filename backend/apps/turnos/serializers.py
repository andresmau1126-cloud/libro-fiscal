from rest_framework import serializers

from .models import Turno


class TurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = [
            "id", "vendedor", "vendedor_nombre", "fecha", "hora_entrada", "hora_salida",
            "estado", "caja_inicial", "ventas_dia", "total_entregado", "faltante",
        ]
        read_only_fields = fields


class TurnoAbrirSerializer(serializers.Serializer):
    vendedor_id = serializers.IntegerField(required=False)
    caja_inicial = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0)
    hora_entrada = serializers.DateTimeField(required=False)


class TurnoCerrarSerializer(serializers.Serializer):
    turno_id = serializers.IntegerField()
    total_entregado = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0)
    hora_salida = serializers.DateTimeField(required=False)
