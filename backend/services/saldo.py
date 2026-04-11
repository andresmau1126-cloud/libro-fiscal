"""
Servicio de recálculo de saldos.
RN-008: saldo acumulado secuencial.
"""
from decimal import Decimal
from apps.movimientos.models import Movimiento


def recompute_saldos(libro_id):
    """
    Recalcula saldos acumulados para todos los movimientos de un libro.
    Orden: fecha ASC, id ASC (RN-016).
    """
    movimientos = list(
        Movimiento.objects
        .filter(libro_id=libro_id)
        .order_by("fecha", "id")
    )

    saldo = Decimal("0")
    updates = []
    for mov in movimientos:
        saldo += mov.ingresos - mov.egresos
        if mov.saldo != saldo:
            mov.saldo = saldo
            updates.append(mov)

    if updates:
        Movimiento.objects.bulk_update(updates, ["saldo"])
