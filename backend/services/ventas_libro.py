from apps.libros.models import Libro
from apps.movimientos.models import Movimiento
from services.saldo import recompute_saldos


def libro_para_venta(vendedor, anio, libro_id=None):
    libros = Libro.objects.filter(propietario=vendedor, anio=anio)
    if libro_id is not None:
        return libros.filter(pk=libro_id).first()
    if libros.count() == 1:
        return libros.first()
    return None


def sincronizar_venta_con_libro(venta, libro_id=None):
    libro = libro_para_venta(venta.vendedor, venta.fecha.year, libro_id)
    if not libro:
        return None

    if venta.libro_id != libro.id:
        venta.libro = libro
        venta.save(update_fields=["libro"])

    movimiento, _ = Movimiento.objects.update_or_create(
        venta=venta,
        defaults={
            "fecha": venta.fecha.date(),
            "descripcion": f"Venta #{venta.id}",
            "ingresos": venta.total,
            "egresos": 0,
            "libro": libro,
        },
    )
    recompute_saldos(libro.id)
    return movimiento