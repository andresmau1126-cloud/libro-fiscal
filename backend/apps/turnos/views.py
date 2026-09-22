from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.inventario.models import Venta
from apps.usuarios.models import Usuario
from apps.usuarios.permissions import SELLER_ROLES
from services.ventas_libro import compilar_ventas_diarias
from .models import Turno
from .serializers import TurnoAbrirSerializer, TurnoCerrarSerializer, TurnoHorasSerializer, TurnoSerializer

# Solo gerente y admin administran/consultan los turnos de todos los vendedores.
TURNOS_SUPERVISOR_ROLES = {"admin", "gerente"}


def _ventas_dia(vendedor, fecha):
    total = Venta.objects.filter(vendedor=vendedor, fecha__date=fecha).aggregate(total=Sum("total"))["total"]
    return total or Decimal("0")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def turnos_vendedores(request):
    if request.user.rol not in TURNOS_SUPERVISOR_ROLES:
        return Response(
            {"error": "Solo gerente o admin pueden consultar vendedores."},
            status=status.HTTP_403_FORBIDDEN,
        )
    vendedores = Usuario.objects.filter(rol__in=SELLER_ROLES, activo=True).order_by("nombre")
    return Response([{"id": v.id, "nombre": v.nombre} for v in vendedores])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def abrir_turno(request):
    serializer = TurnoAbrirSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if request.user.rol in SELLER_ROLES:
        vendedor_id = request.user.id
    elif request.user.rol in TURNOS_SUPERVISOR_ROLES:
        vendedor_id = data.get("vendedor_id") or request.user.id
    else:
        return Response({"error": "Su rol no tiene permiso para abrir turnos."}, status=status.HTTP_403_FORBIDDEN)

    try:
        vendedor = Usuario.objects.get(pk=vendedor_id)
    except Usuario.DoesNotExist:
        return Response({"error": "El vendedor no existe."}, status=status.HTTP_404_NOT_FOUND)

    hoy = timezone.localdate()
    if Turno.objects.filter(vendedor=vendedor, fecha=hoy, estado="abierto").exists():
        return Response({"error": "Ya existe un turno abierto hoy para este vendedor."}, status=status.HTTP_409_CONFLICT)

    turno = Turno(
        vendedor=vendedor,
        fecha=hoy,
        caja_inicial=data["caja_inicial"],
        estado="abierto",
    )
    # Solo gerente/admin pueden fijar manualmente la hora de entrada.
    if request.user.rol in TURNOS_SUPERVISOR_ROLES and data.get("hora_entrada"):
        turno.hora_entrada = data["hora_entrada"]
    turno.save()
    return Response(TurnoSerializer(turno).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cerrar_turno(request):
    serializer = TurnoCerrarSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        turno = Turno.objects.select_related("vendedor").get(pk=data["turno_id"])
    except Turno.DoesNotExist:
        return Response({"error": "El turno no existe."}, status=status.HTTP_404_NOT_FOUND)

    is_owner = turno.vendedor_id == request.user.id
    is_supervisor = request.user.rol in TURNOS_SUPERVISOR_ROLES
    if not (is_owner or is_supervisor):
        return Response({"error": "No tiene permiso para cerrar este turno."}, status=status.HTTP_403_FORBIDDEN)

    if turno.estado == "cerrado":
        return Response({"error": "El turno ya está cerrado."}, status=status.HTTP_400_BAD_REQUEST)

    ventas_dia = _ventas_dia(turno.vendedor, turno.fecha)
    total_entregado = data["total_entregado"]
    faltante = (ventas_dia + turno.caja_inicial) - total_entregado

    turno.ventas_dia = ventas_dia
    turno.total_entregado = total_entregado
    turno.faltante = faltante
    turno.estado = "cerrado"
    # Solo gerente/admin pueden fijar manualmente la hora de salida.
    if is_supervisor and data.get("hora_salida"):
        turno.hora_salida = data["hora_salida"]
    else:
        turno.hora_salida = timezone.now()
    turno.save()

    # Consolida el total final de ventas del día (todos los vendedores) en el libro fiscal.
    compilar_ventas_diarias(fecha=turno.fecha)

    return Response(TurnoSerializer(turno).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def editar_horas_turno(request, turno_id):
    if request.user.rol not in TURNOS_SUPERVISOR_ROLES:
        return Response(
            {"error": "Solo gerente o admin pueden editar la hora de entrada/salida."},
            status=status.HTTP_403_FORBIDDEN,
        )
    try:
        turno = Turno.objects.get(pk=turno_id)
    except Turno.DoesNotExist:
        return Response({"error": "El turno no existe."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TurnoHorasSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    update_fields = []
    if "hora_entrada" in data:
        turno.hora_entrada = data["hora_entrada"]
        update_fields.append("hora_entrada")
    if "hora_salida" in data:
        turno.hora_salida = data["hora_salida"]
        update_fields.append("hora_salida")
    turno.save(update_fields=update_fields)

    return Response(TurnoSerializer(turno).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def turnos_list(request):
    qs = Turno.objects.select_related("vendedor")

    if request.user.rol in TURNOS_SUPERVISOR_ROLES:
        vendedor_id = request.query_params.get("vendedor_id")
        vendedor_nombre = request.query_params.get("vendedor")
        fecha = request.query_params.get("fecha")
        estado = request.query_params.get("estado")
        if vendedor_id:
            qs = qs.filter(vendedor_id=vendedor_id)
        if vendedor_nombre:
            qs = qs.filter(vendedor_nombre__icontains=vendedor_nombre)
        if fecha:
            qs = qs.filter(fecha=fecha)
        if estado:
            qs = qs.filter(estado=estado)
    else:
        qs = qs.filter(vendedor=request.user)
        fecha = request.query_params.get("fecha")
        if fecha:
            qs = qs.filter(fecha=fecha)

    return Response(TurnoSerializer(qs[:200], many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def turnos_reporte(request):
    if request.user.rol not in TURNOS_SUPERVISOR_ROLES:
        return Response(
            {"error": "Solo gerente o admin pueden ver el reporte de cierre."},
            status=status.HTTP_403_FORBIDDEN,
        )

    fecha = request.query_params.get("fecha") or timezone.localdate().isoformat()
    qs = Turno.objects.select_related("vendedor").filter(fecha=fecha)
    rows = TurnoSerializer(qs, many=True).data

    vendedores_activos = Usuario.objects.filter(rol__in=SELLER_ROLES, activo=True)
    ids_con_turno = set(qs.values_list("vendedor_id", flat=True))
    ausentes = [
        {"id": v.id, "nombre": v.nombre}
        for v in vendedores_activos
        if v.id not in ids_con_turno
    ]

    resumen = {
        "fecha": fecha,
        "total_turnos": qs.count(),
        "abiertos": qs.filter(estado="abierto").count(),
        "cerrados": qs.filter(estado="cerrado").count(),
        "total_ventas": float(sum(t.ventas_dia for t in qs)),
        "total_entregado": float(sum(t.total_entregado or 0 for t in qs)),
        "total_faltante": float(sum(t.faltante or 0 for t in qs)),
        "ausentes": ausentes,
    }

    return Response({"fecha": fecha, "turnos": rows, "resumen": resumen})
