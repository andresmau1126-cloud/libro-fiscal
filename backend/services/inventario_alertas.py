"""
Servicio de alertas de inventario — detecta stock bajo y productos próximos a vencer.
"""
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from apps.inventario.models import Producto


def obtener_productos_stock_bajo():
    """Retorna productos con stock por debajo del mínimo."""
    from django.db import models
    return Producto.objects.filter(
        stock_actual__lte=models.F("stock_minimo")
    ).select_related("propietario").order_by("-stock_actual")


def obtener_productos_proximos_vencer():
    """Retorna productos próximos a vencer (dentro de dias_alerta días)."""
    productos_alertas = []
    hoy = timezone.now().date()
    
    for producto in Producto.objects.filter(fecha_vencimiento__isnull=False):
        if producto.fecha_vencimiento and producto.dias_alerta:
            fecha_alerta = producto.fecha_vencimiento - timedelta(days=producto.dias_alerta)
            if hoy >= fecha_alerta <= producto.fecha_vencimiento:
                productos_alertas.append(producto)
    
    return productos_alertas


def generar_contenido_alerta():
    """Genera el contenido del email de alerta de inventario."""
    stock_bajo = obtener_productos_stock_bajo()
    proximos_vencer = obtener_productos_proximos_vencer()
    
    contenido = "📦 ALERTA DE INVENTARIO - Libro Fiscal v2\n"
    contenido += "=" * 60 + "\n\n"
    
    # Stock bajo
    if stock_bajo.exists():
        contenido += "⚠️  PRODUCTOS CON STOCK BAJO:\n"
        contenido += "-" * 60 + "\n"
        for prod in stock_bajo:
            contenido += f"  • {prod.nombre}\n"
            contenido += f"    Stock actual: {prod.stock_actual} | Mínimo: {prod.stock_minimo}\n"
            contenido += f"    Categoría: {prod.categoria or 'Sin categoría'}\n"
            contenido += f"    Precio unitario: ${prod.costo_unitario}\n\n"
    else:
        contenido += "✓ Todos los productos tienen stock adecuado.\n\n"
    
    # Próximos a vencer
    if proximos_vencer:
        contenido += "\n📅 PRODUCTOS PRÓXIMOS A VENCER:\n"
        contenido += "-" * 60 + "\n"
        for prod in proximos_vencer:
            dias_restantes = (prod.fecha_vencimiento - timezone.now().date()).days
            contenido += f"  • {prod.nombre}\n"
            contenido += f"    Vencimiento: {prod.fecha_vencimiento} ({dias_restantes} días)\n"
            contenido += f"    Stock actual: {prod.stock_actual}\n"
            contenido += f"    Categoría: {prod.categoria or 'Sin categoría'}\n\n"
    else:
        contenido += "\n✓ Ningún producto próximo a vencer.\n"
    
    contenido += "\n" + "=" * 60 + "\n"
    contenido += f"Generado: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return contenido, len(stock_bajo), len(proximos_vencer)


def enviar_alerta_inventario(destino=None, usar_contenido_personalizado=None):
    """
    Envía alerta de inventario por email.
    
    Args:
        destino: Email destino (default: ALERTA_EMAIL_DESTINO de settings)
        usar_contenido_personalizado: Función que retorna (contenido, count_bajo, count_vencer)
    
    Returns:
        dict: {"ok": bool, "error": str (opcional), "stock_bajo": int, "proximos_vencer": int}
    """
    if not destino:
        destino = settings.ALERTA_EMAIL_DESTINO
    
    remitente = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    
    if not remitente or not settings.EMAIL_HOST_PASSWORD:
        return {
            "ok": False,
            "error": "Faltan variables EMAIL_HOST_USER o EMAIL_HOST_PASSWORD para Brevo SMTP.",
        }
    
    # Generar contenido
    if usar_contenido_personalizado and callable(usar_contenido_personalizado):
        contenido, stock_bajo_count, proximos_count = usar_contenido_personalizado()
    else:
        contenido, stock_bajo_count, proximos_count = generar_contenido_alerta()
    
    # Si no hay alertas, retornar sin enviar
    if stock_bajo_count == 0 and proximos_count == 0:
        return {
            "ok": True,
            "mensaje": "Sin alertas de inventario",
            "stock_bajo": 0,
            "proximos_vencer": 0,
        }
    
    try:
        send_mail(
            subject="🚨 Alerta de Inventario - Libro Fiscal v2",
            message=contenido,
            from_email=remitente,
            recipient_list=[destino],
            fail_silently=False,
        )
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "stock_bajo": stock_bajo_count,
            "proximos_vencer": proximos_count,
        }
    
    return {
        "ok": True,
        "mensaje": f"Alerta enviada a {destino}",
        "stock_bajo": stock_bajo_count,
        "proximos_vencer": proximos_count,
    }
