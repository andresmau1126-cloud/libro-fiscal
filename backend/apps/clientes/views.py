from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cliente
from .serializers import ClienteCreateSerializer, ClienteSerializer
from .utils import normalizar_nit


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def clientes_list_create(request):
    if request.method == "GET":
        query = request.query_params.get("q", "").strip()
        clientes = Cliente.objects.filter(activo=True)
        if query:
            clientes = clientes.filter(nombre__icontains=query) | clientes.filter(nit__icontains=query) | clientes.filter(nit_normalizado=normalizar_nit(query))
        return Response(ClienteSerializer(clientes[:200], many=True).data)

    serializer = ClienteCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        cliente = serializer.save()
    except IntegrityError:
        return Response({"error": "Ya existe un cliente registrado con ese NIT."}, status=status.HTTP_409_CONFLICT)
    return Response(ClienteSerializer(cliente).data, status=status.HTTP_201_CREATED)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def cliente_detail(request, cliente_id):
    try:
        cliente = Cliente.objects.get(pk=cliente_id, activo=True)
    except Cliente.DoesNotExist:
        return Response({"error": "Cliente no existe."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ClienteSerializer(cliente, data=request.data, partial=request.method == "PATCH")
    serializer.is_valid(raise_exception=True)
    try:
        cliente = serializer.save()
    except IntegrityError:
        return Response({"error": "Ya existe un cliente registrado con ese NIT."}, status=status.HTTP_409_CONFLICT)
    return Response(ClienteSerializer(cliente).data)
