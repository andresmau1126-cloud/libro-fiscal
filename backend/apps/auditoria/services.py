"""
Servicio de auditoría — registra acciones de usuarios.
"""
from .models import Auditoria


def audit_log(request, accion, entidad, entidad_id=None, detalle=None):
    """Registra una acción en la tabla de auditoría."""
    usuario = None
    ip = None
    try:
        if request and hasattr(request, "user") and request.user.is_authenticated:
            usuario = request.user
        if request:
            ip = request.META.get("REMOTE_ADDR")
    except Exception:
        pass

    Auditoria.objects.create(
        usuario=usuario,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        detalle=detalle,
        ip=ip,
    )
