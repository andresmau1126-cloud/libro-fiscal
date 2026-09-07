from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.inventario.models import Venta
from apps.movimientos.models import Movimiento
from apps.usuarios.permissions import SUPERVISOR_ROLES, can_write
from services.saldo import recompute_saldos
from .models import Expense, Provider, SellerStats
from .serializers import ExpenseSerializer, ProviderSerializer, SellerStatsSerializer


def _period_bounds(period, requested):
    today = timezone.localdate()
    if period == "daily":
        start = date.fromisoformat(requested) if requested else today
        return start, start
    if period == "monthly":
        start = date(today.year, today.month, 1) if not requested else date.fromisoformat(f"{requested}-01")
        return start, date(start.year, start.month, monthrange(start.year, start.month)[1])
    raise ValueError("period debe ser daily o monthly")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stats(request):
    if request.user.rol not in SUPERVISOR_ROLES:
        return Response({"error": "Solo los roles de supervisión pueden consultar estadísticas."}, status=status.HTTP_403_FORBIDDEN)
    period = request.query_params.get("period", "daily")
    try:
        start, end = _period_bounds(period, request.query_params.get("date"))
    except (ValueError, TypeError):
        return Response({"error": "Use period=daily|monthly y una fecha válida."}, status=status.HTTP_400_BAD_REQUEST)
    rows = (Venta.objects.filter(fecha__date__gte=start, fecha__date__lte=end, vendedor__rol__in=("vendedor", "vendedor_2"))
            .values("vendedor_id", "vendedor__nombre")
            .annotate(total=Sum("total"), count=Count("id")))
    SellerStats.objects.filter(period=period, period_start=start).delete()
    created = [SellerStats(vendedor_id=row["vendedor_id"], period=period, period_start=start,
                           total_vendido=row["total"] or Decimal("0"), cantidad_ventas=row["count"],
                           ticket_promedio=(row["total"] or Decimal("0")) / row["count"] if row["count"] else 0) for row in rows]
    SellerStats.objects.bulk_create(created)
    data = SellerStatsSerializer(SellerStats.objects.filter(period=period, period_start=start).select_related("vendedor"), many=True).data
    return Response({"period": period, "from": start, "to": end, "results": data})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def expenses(request):
    if request.method == "GET":
        return Response(ExpenseSerializer(Expense.objects.select_related("provider").all()[:200], many=True).data)
    if not can_write(request.user) or request.user.rol == "auditor":
        return Response({"error": "Su rol solo tiene permisos de consulta"}, status=status.HTTP_403_FORBIDDEN)
    serializer = ExpenseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    if data["fecha"].year != data["libro"].anio:
        return Response({"error": "La fecha debe pertenecer al año del libro."}, status=status.HTTP_400_BAD_REQUEST)
    with transaction.atomic():
        movimiento = Movimiento.objects.create(fecha=data["fecha"], descripcion=data["descripcion"], ingresos=0,
                                                egresos=data["valor_pagado"], libro=data["libro"])
        expense = Expense.objects.create(**data, creado_por=request.user, movimiento=movimiento)
        recompute_saldos(data["libro"].id)
    return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def providers(request):
    if request.method == "GET":
        return Response(ProviderSerializer(Provider.objects.filter(activo=True), many=True).data)
    if not can_write(request.user) or request.user.rol == "auditor":
        return Response({"error": "Su rol solo tiene permisos de consulta"}, status=status.HTTP_403_FORBIDDEN)
    serializer = ProviderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(ProviderSerializer(Provider.objects.create(**serializer.validated_data)).data, status=status.HTTP_201_CREATED)
