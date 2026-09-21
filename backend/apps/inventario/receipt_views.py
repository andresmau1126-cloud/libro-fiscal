from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.usuarios.permissions import can_view_all
from .models import Venta


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def venta_receipt(request, venta_id):
    try:
        venta = Venta.objects.select_related("vendedor").prefetch_related("detalles__producto").get(pk=venta_id)
    except Venta.DoesNotExist:
        return Response({"error": "Venta no existe"}, status=status.HTTP_404_NOT_FOUND)

    if not can_view_all(request.user) and venta.vendedor_id != request.user.id:
        return Response({"error": "No tiene permisos para consultar este comprobante."}, status=status.HTTP_403_FORBIDDEN)

    items = [
        {
            "producto_id": detail.producto_id,
            "producto": detail.producto.nombre,
            "cantidad": float(detail.cantidad),
            "precio_unitario": float(detail.precio_unitario),
            "subtotal": float(detail.subtotal),
        }
        for detail in venta.detalles.all()
    ]
    return Response({
        "id": venta.id,
        "numero_comprobante": f"VEN-{venta.id:04d}",
        "nit": "1020085627-1",
        "company": "Multivariedades Ricaurte",
        "fecha": venta.fecha.isoformat(),
        "cliente": venta.cliente,
        "medio_pago": venta.medio_pago,
        "vendedor": venta.vendedor.nombre,
        "vendedor_email": venta.vendedor.email,
        "total": float(venta.total),
        "items": items,
    })
