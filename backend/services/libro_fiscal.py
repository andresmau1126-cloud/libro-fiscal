from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

from apps.finanzas.models import Expense
from apps.inventario.models import Venta
from apps.movimientos.models import Movimiento


LIBRO_FOLIO_0011_NIT = "1010085627-1"
LIBRO_FOLIO_0011_YEAR = 2026
LIBRO_FOLIO_0011_MONTH = 11


def is_folio_0011_view(libro, year, month):
    return (
        libro.nit == LIBRO_FOLIO_0011_NIT
        and libro.anio == LIBRO_FOLIO_0011_YEAR
        and year == LIBRO_FOLIO_0011_YEAR
        and month == LIBRO_FOLIO_0011_MONTH
    )


def build_folio_0011_rows(libro, year, month):
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])

    sales = (
        Venta.objects.filter(
            libro=libro,
            fecha__date__gte=start,
            fecha__date__lte=end,
            es_simulado=False,
        )
        .annotate(dia_fecha=TruncDate("fecha"))
        .values("dia_fecha")
        .annotate(total=Sum("total"), cantidad=Count("id"))
    )
    expenses = (
        Expense.objects.filter(
            libro=libro,
            fecha__gte=start,
            fecha__lte=end,
            es_simulado=False,
        )
        .values("fecha")
        .annotate(total=Sum("valor_pagado"), cantidad=Count("id"))
    )

    by_day = {}
    for row in sales:
        by_day[row["dia_fecha"]] = {
            "ingresos": row["total"] or Decimal("0"),
            "egresos": Decimal("0"),
            "ventas": row["cantidad"],
            "compras": 0,
        }
    for row in expenses:
        day = by_day.setdefault(
            row["fecha"],
            {
                "ingresos": Decimal("0"),
                "egresos": Decimal("0"),
                "ventas": 0,
                "compras": 0,
            },
        )
        day["egresos"] = row["total"] or Decimal("0")
        day["compras"] = row["cantidad"]

    opening = Movimiento.objects.filter(
        libro=libro,
        fecha__lt=start,
    ).aggregate(ingresos=Sum("ingresos"), egresos=Sum("egresos"))
    saldo = (opening["ingresos"] or Decimal("0")) - (opening["egresos"] or Decimal("0"))
    total_ingresos = Decimal("0")
    total_egresos = Decimal("0")
    rows = []

    for day, amounts in sorted(by_day.items()):
        ingresos = amounts["ingresos"]
        egresos = amounts["egresos"]
        saldo += ingresos - egresos
        total_ingresos += ingresos
        total_egresos += egresos
        descripcion = "Ventas del día" if amounts["ventas"] else ""
        if amounts["compras"]:
            descripcion = f"{descripcion} · Compras del día" if descripcion else "Compras del día"
        rows.append({
            "id": f"folio-0011-{day.isoformat()}",
            "fecha": day.isoformat(),
            "dia": day.day,
            "descripcion": descripcion,
            "ingresos": float(ingresos),
            "egresos": float(egresos),
            "saldo": float(saldo),
            "sello_digital": "",
            "tipo": "resumen_diario",
            "medio_pago": None,
            "turno": None,
        })

    return {
        "rows": rows,
        "totals": {
            "ingresos": float(total_ingresos),
            "egresos": float(total_egresos),
            "saldo": float(saldo),
        },
    }
