from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Libro
from .serializers import LibroSerializer, LibroCreateSerializer
from apps.auditoria.services import audit_log


@api_view(["GET", "POST"])
def libros_list_create(request):
    if request.method == "GET":
        anio = request.query_params.get("anio")
        qs = Libro.objects.all()
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

    # Check NIT + año (RN-001)
    existing = Libro.objects.filter(nit=nit, anio=anio).first()
    if existing:
        if nombre and existing.nombre != nombre:
            return Response(
                {"error": f"Ya existe un libro para NIT {nit} y año {anio} con el nombre '{existing.nombre}'."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(LibroSerializer(existing).data)

    # Check nombre + año (RN-002)
    if Libro.objects.filter(nombre=nombre, anio=anio).exists():
        return Response(
            {"error": f"El nombre '{nombre}' ya está registrado para el año {anio}."},
            status=status.HTTP_409_CONFLICT,
        )

    libro = Libro.objects.create(nombre=nombre, nit=nit, anio=anio)
    return Response(LibroSerializer(libro).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def libro_detail(request, libro_id):
    try:
        libro = Libro.objects.get(pk=libro_id)
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

        # Check NIT + año uniqueness (exclude current)
        dup_nit = Libro.objects.filter(nit=nit, anio=anio).exclude(pk=libro_id).first()
        if dup_nit:
            return Response(
                {"error": f"Ya existe un libro para NIT {nit} y año {anio} con el nombre '{dup_nit.nombre}'."},
                status=status.HTTP_409_CONFLICT,
            )

        # Check nombre + año uniqueness (exclude current)
        if Libro.objects.filter(nombre=nombre, anio=anio).exclude(pk=libro_id).exists():
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
