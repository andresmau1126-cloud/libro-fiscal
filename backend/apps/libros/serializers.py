from rest_framework import serializers
from .models import Libro


class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = ["id", "nombre", "nit", "anio"]
        read_only_fields = ["id"]


class LibroCreateSerializer(serializers.Serializer):
    nombre = serializers.CharField(min_length=1, max_length=200)
    nit = serializers.CharField(min_length=1, max_length=50)
    anio = serializers.IntegerField(min_value=2000, max_value=2099)
