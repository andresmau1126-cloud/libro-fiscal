from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.libros.models import Libro
from apps.inventario.models import Venta
from apps.movimientos.models import Movimiento
from services.saldo import recompute_saldos
from apps.movimientos.models import Movimiento
from services.saldo import recompute_saldos

LIBRO_VENTAS_VENDEDORES_NIT = "1010085627"
LIBRO_VENTAS_VENDEDORES_NOMBRE = "Andres"


def libro_para_venta(vendedor, anio, libro_id=None):
    if vendedor.rol in ("vendedor", "vendedor_2"):
        libro_ventas_vendedores = Libro.objects.filter(
            nit=LIBRO_VENTAS_VENDEDORES_NIT,
            anio=anio,
        ).order_by("id").first()
        if not libro_ventas_vendedores:
            libro_ventas_vendedores = Libro.objects.create(
                nombre=LIBRO_VENTAS_VENDEDORES_NOMBRE,
                nit=LIBRO_VENTAS_VENDEDORES_NIT,
                anio=anio,
            )
        return libro_ventas_vendedores

    libros = Libro.objects.filter(propietario=vendedor, anio=anio)
    if libro_id is not None:
        return libros.filter(pk=libro_id).first()
    if libros.count() == 1:
        return libros.first()
    return None


def asignar_libro_a_venta(venta, libro_id=None):
    libro = libro_para_venta(venta.vendedor, venta.fecha.year, libro_id)
    if not libro:
        return None

    if venta.libro_id != libro.id:
        venta.libro = libro
        venta.save(update_fields=["libro"])

    return libro


def compilar_ventas_diarias(fecha=None):
    fecha = fecha or timezone.localdate() - timedelta(days=1)
    ventas = Venta.objects.filter(fecha__date=fecha, libro__isnull=False)
    totales = ventas.values("libro_id").annotate(total=Sum("total"))
    libros_actualizados = []

    with transaction.atomic():
        Movimiento.objects.filter(
            fecha=fecha,
            es_compilacion_ventas=True,
        ).delete()
        for total in totales:
            movimiento = Movimiento.objects.create(
                fecha=fecha,
                descripcion=f"Ventas diarias {fecha.isoformat()}",
                ingresos=total["total"] or Decimal("0"),
                egresos=Decimal("0"),
                libro_id=total["libro_id"],
                es_compilacion_ventas=True,
            )
            libros_actualizados.append(movimiento.libro_id)

        for libro_id in libros_actualizados:
            recompute_saldos(libro_id)

    return len(libros_actualizados)