from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone

from .models import Libro
from .serializers import LibroSerializer, LibroCreateSerializer
from apps.auditoria.services import audit_log
from apps.usuarios.permissions import can_delete, can_view_all, can_write


def _libros_qs_for_user(user):
    if can_view_all(user):
        return Libro.objects.all()
    return Libro.objects.filter(propietario=user)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fiscal_books(request):
    """Devuelve el consolidado fiscal diario visible para cada rol."""
    fecha = request.query_params.get("date") or timezone.localdate().isoformat()
    try:
        date_value = timezone.datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "date debe tener formato YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

    libros = _libros_qs_for_user(request.user)
    if request.user.rol in {"admin", "gerente", "auditor"}:
        libros = Libro.objects.filter(nit="1010085627", anio=date_value.year)
    rows = []
    for libro in libros.order_by("-anio", "nombre"):
        sales_total = libro.ventas.filter(fecha__date=date_value).aggregate(total=Sum("total"))["total"] or 0
        expenses_total = libro.expenses.filter(fecha=date_value).aggregate(total=Sum("valor_pagado"))["total"] or 0
        rows.append({
            "id": libro.id,
            "nombre": libro.nombre,
            "nit": libro.nit,
            "anio": libro.anio,
            "fecha": fecha,
            "total_ventas_dia": sales_total,
            "total_egresos_dia": expenses_total,
            "saldo_dia": sales_total - expenses_total,
        })
    return Response(rows)


@api_view(["GET", "POST"])
def libros_list_create(request):
    if request.method == "POST" and request.user.rol not in {"admin", "vendedor", "vendedor_2"}:
        return Response({"error": "Su rol solo tiene permisos de consulta"}, status=status.HTTP_403_FORBIDDEN)
    if request.method == "GET":
        anio = request.query_params.get("anio")
        qs = _libros_qs_for_user(request.user)
        if anio:
            try:
                qs = qs.filter(anio=int(anio))
            except (ValueError, TypeError):
                return Response({"error": "anio inválido"}, status=status.HTTP_400_BAD_REQUEST)
            qs = qs.order_by("nombre")
        else:
            qs = qs.order_by("-anio", "nombre")
        return Response(LibroSerializer(qs, many=True).data)

    # POST
    serializer = LibroCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    nombre = data["nombre"].strip()
    nit = data["nit"].strip()
    anio = data["anio"]
    libros_qs = _libros_qs_for_user(request.user)

    # Check NIT + año (RN-001)
    existing = libros_qs.filter(nit=nit, anio=anio).first()
    if existing:
        if nombre and existing.nombre != nombre:
            return Response(
                {"error": f"Ya existe un libro para NIT {nit} y año {anio} con el nombre '{existing.nombre}'."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(LibroSerializer(existing).data)

    # Check nombre + año (RN-002)
    if libros_qs.filter(nombre=nombre, anio=anio).exists():
        return Response(
            {"error": f"El nombre '{nombre}' ya está registrado para el año {anio}."},
            status=status.HTTP_409_CONFLICT,
        )

    libro = Libro.objects.create(nombre=nombre, nit=nit, anio=anio, propietario=request.user)
    return Response(LibroSerializer(libro).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def libro_detail(request, libro_id):
    if request.method == "PUT" and request.user.rol not in {"admin", "vendedor", "vendedor_2"}:
        return Response({"error": "Su rol solo tiene permisos de consulta"}, status=status.HTTP_403_FORBIDDEN)
    if request.method == "DELETE" and request.user.rol not in {"admin", "vendedor", "vendedor_2"}:
        return Response({"error": "Su rol solo tiene permisos de consulta"}, status=status.HTTP_403_FORBIDDEN)
    try:
        libro = _libros_qs_for_user(request.user).get(pk=libro_id)
    except Libro.DoesNotExist:
        return Response({"error": "libro no existe"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(LibroSerializer(libro).data)

    if request.method == "PUT":
        serializer = LibroCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        nombre = data["nombre"].strip()
        nit = data["nit"].strip()
        anio = data["anio"]
        libros_qs = _libros_qs_for_user(request.user)

        # Check NIT + año uniqueness (exclude current)
        dup_nit = libros_qs.filter(nit=nit, anio=anio).exclude(pk=libro_id).first()
        if dup_nit:
            return Response(
                {"error": f"Ya existe un libro para NIT {nit} y año {anio} con el nombre '{dup_nit.nombre}'."},
                status=status.HTTP_409_CONFLICT,
            )

        # Check nombre + año uniqueness (exclude current)
        if libros_qs.filter(nombre=nombre, anio=anio).exclude(pk=libro_id).exists():
            return Response(
                {"error": f"El nombre '{nombre}' ya está registrado para el año {anio}."},
                status=status.HTTP_409_CONFLICT,
            )

        libro.nombre = nombre
        libro.nit = nit
        libro.anio = anio
        libro.save()
        audit_log(request, "editar", "libro", libro.id)
        return Response(LibroSerializer(libro).data)

    # DELETE — cascade handled by Django FK
    audit_log(request, "eliminar", "libro", libro.id)
    libro.delete()
    return Response({"ok": True})
