from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.libros.models import Libro
from apps.movimientos.models import Movimiento
from apps.usuarios.models import Usuario


@api_view(["GET"])
def dashboard_stats(request):
    total_libros = Libro.objects.count()
    total_movimientos = Movimiento.objects.count()

    totals = Movimiento.objects.aggregate(
        ingresos=Sum("ingresos"),
        egresos=Sum("egresos"),
    )
    total_ingresos = float(totals["ingresos"] or 0)
    total_egresos = float(totals["egresos"] or 0)

    total_usuarios = Usuario.objects.filter(activo=True).count()

    # Libros por año (últimos 5)
    libros_por_anio = list(
        Libro.objects
        .values("anio")
        .annotate(cantidad=Count("id"))
        .order_by("-anio")[:5]
    )

    # Movimientos recientes
    recientes_qs = (
        Movimiento.objects
        .select_related("libro")
        .order_by("-id")[:10]
    )
    recientes = [
        {
            "id": m.id,
            "fecha": str(m.fecha),
            "descripcion": m.descripcion,
            "ingresos": float(m.ingresos),
            "egresos": float(m.egresos),
            "saldo": float(m.saldo),
            "libro_nombre": m.libro.nombre if m.libro else None,
        }
        for m in recientes_qs
    ]

    # Ingresos vs egresos por mes (año actual)
    current_year = timezone.now().year
    meses_chart = list(
        Movimiento.objects
        .filter(libro__anio=current_year)
        .annotate(mes=ExtractMonth("fecha"))
        .values("mes")
        .annotate(
            ingresos=Sum("ingresos"),
            egresos=Sum("egresos"),
        )
        .order_by("mes")
    )
    meses_chart = [
        {"mes": m["mes"], "ingresos": float(m["ingresos"] or 0), "egresos": float(m["egresos"] or 0)}
        for m in meses_chart
    ]

    return Response({
        "total_libros": total_libros,
        "total_movimientos": total_movimientos,
        "total_ingresos": total_ingresos,
        "total_egresos": total_egresos,
        "saldo_global": total_ingresos - total_egresos,
        "total_usuarios": total_usuarios,
        "libros_por_anio": libros_por_anio,
        "movimientos_recientes": recientes,
        "meses_chart": meses_chart,
    })


@api_view(["GET"])
def resumen_anual(request):
    libro_id = request.query_params.get("libro_id")
    year = request.query_params.get("year")

    if not libro_id:
        return Response({"error": "libro_id requerido"}, status=400)

    try:
        libro_id = int(libro_id)
    except (ValueError, TypeError):
        return Response({"error": "libro_id inválido"}, status=400)

    qs = Movimiento.objects.filter(libro_id=libro_id)
    if year:
        try:
            y = int(year)
            from datetime import date
            qs = qs.filter(fecha__gte=date(y, 1, 1), fecha__lt=date(y + 1, 1, 1))
        except (ValueError, TypeError):
            return Response({"error": "year inválido"}, status=400)

    meses = list(
        qs
        .annotate(mes=ExtractMonth("fecha"))
        .values("mes")
        .annotate(
            ingresos=Sum("ingresos"),
            egresos=Sum("egresos"),
        )
        .order_by("mes")
    )
    meses = [
        {"mes": m["mes"], "ingresos": float(m["ingresos"] or 0), "egresos": float(m["egresos"] or 0)}
        for m in meses
    ]

    total_ing = sum(m["ingresos"] for m in meses)
    total_egr = sum(m["egresos"] for m in meses)

    return Response({
        "meses": meses,
        "totales": {
            "ingresos": total_ing,
            "egresos": total_egr,
            "saldo": total_ing - total_egr,
        },
    })
