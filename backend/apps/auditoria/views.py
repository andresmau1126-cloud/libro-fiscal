from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from apps.usuarios.permissions import IsAdmin
from .models import Auditoria


@api_view(["GET"])
@permission_classes([IsAdmin])
def auditoria_list(request):
    limit = min(int(request.query_params.get("limit", 50)), 200)
    qs = (
        Auditoria.objects
        .select_related("usuario")
        .order_by("-created_at")[:limit]
    )
    result = []
    for r in qs:
        result.append({
            "id": r.id,
            "accion": r.accion,
            "entidad": r.entidad,
            "entidad_id": r.entidad_id,
            "detalle": r.detalle,
            "ip": r.ip,
            "created_at": str(r.created_at),
            "usuario_nombre": r.usuario.nombre if r.usuario else None,
        })
    return Response(result)


@api_view(["DELETE"])
@permission_classes([IsAdmin])
def auditoria_delete(request, pk):
    try:
        registro = Auditoria.objects.get(pk=pk)
    except Auditoria.DoesNotExist:
        return Response({"error": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    registro.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["DELETE"])
@permission_classes([IsAdmin])
def auditoria_clear(request):
    deleted, _ = Auditoria.objects.all().delete()
    return Response({"deleted": deleted})
