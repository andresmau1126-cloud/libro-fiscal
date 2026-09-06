from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.libros.models import Libro
from apps.inventario.models import Venta
from apps.movimientos.models import Movimiento
from apps.usuarios.permissions import SELLER_ROLES
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


def compilar_ventas_diarias(fecha=None, nit=None):
    """Consolida las ventas de vendedores en el libro fiscal compartido."""
    fecha = fecha or timezone.localdate()
    nit = nit or LIBRO_VENTAS_VENDEDORES_NIT

    with transaction.atomic():
        libro = Libro.objects.filter(nit=nit, anio=fecha.year).order_by("id").first()
        if not libro:
            libro = Libro.objects.create(
                nombre=LIBRO_VENTAS_VENDEDORES_NOMBRE,
                nit=nit,
                anio=fecha.year,
            )

        ventas = Venta.objects.filter(
            fecha__date=fecha,
            vendedor__rol__in=SELLER_ROLES,
        )
        ventas.update(libro=libro)
        total = ventas.aggregate(total=Sum("total"))["total"] or Decimal("0")

        Movimiento.objects.filter(
            fecha=fecha,
            libro=libro,
            es_compilacion_ventas=True,
        ).delete()
        Movimiento.objects.create(
            fecha=fecha,
            descripcion=f"Ventas diarias {fecha.isoformat()}",
            ingresos=total,
            egresos=Decimal("0"),
            libro=libro,
            es_compilacion_ventas=True,
        )
        recompute_saldos(libro.id)

    return 1