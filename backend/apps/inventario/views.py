from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse

from .models import Producto
from .serializers import ProductoSerializer, ProductoCreateUpdateSerializer


def _productos_qs_for_user(user):
    if getattr(user, "rol", None) == "admin":
        return Producto.objects.all()
    return Producto.objects.filter(propietario=user)


@api_view(["GET", "POST"])
def productos_list_create(request):
    productos_qs = _productos_qs_for_user(request.user)

    if request.method == "GET":
        query = (request.query_params.get("q") or "").strip()
        low_stock = (request.query_params.get("low_stock") or "").strip() in ("1", "true", "yes")

        if query:
            productos_qs = productos_qs.filter(nombre__icontains=query)
        if low_stock:
            productos_qs = productos_qs.filter(stock_actual__lte=models.F("stock_minimo"))

        return Response(ProductoSerializer(productos_qs.order_by("nombre", "id"), many=True).data)

    serializer = ProductoCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    nombre = data["nombre"].strip()
    if productos_qs.filter(nombre=nombre).exists():
        return Response(
            {"error": f"El producto '{nombre}' ya está registrado."},
            status=status.HTTP_409_CONFLICT,
        )

    producto = Producto.objects.create(
        nombre=nombre,
        categoria=(data.get("categoria") or "").strip(),
        descripcion=(data.get("descripcion") or "").strip(),
        stock_actual=data.get("stock_actual", 0) or 0,
        stock_minimo=data.get("stock_minimo", 0) or 0,
        costo_unitario=data.get("costo_unitario", 0) or 0,
        precio_venta=data.get("precio_venta", 0) or 0,
        fecha_vencimiento=data.get("fecha_vencimiento"),
        dias_alerta=data.get("dias_alerta", 30) or 30,
        propietario=request.user,
    )
    return Response(ProductoSerializer(producto).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def producto_detail(request, producto_id):
    try:
        producto = _productos_qs_for_user(request.user).get(pk=producto_id)
    except Producto.DoesNotExist:
        return Response({"error": "producto no existe"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(ProductoSerializer(producto).data)

    if request.method == "PUT":
        serializer = ProductoCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        nombre = data["nombre"].strip()
        productos_qs = _productos_qs_for_user(request.user)
        if productos_qs.filter(nombre=nombre).exclude(pk=producto_id).exists():
            return Response(
                {"error": f"El producto '{nombre}' ya está registrado."},
                status=status.HTTP_409_CONFLICT,
            )

        producto.nombre = nombre
        producto.categoria = (data.get("categoria") or "").strip()
        producto.descripcion = (data.get("descripcion") or "").strip()
        producto.stock_actual = data.get("stock_actual", 0) or 0
        producto.stock_minimo = data.get("stock_minimo", 0) or 0
        producto.costo_unitario = data.get("costo_unitario", 0) or 0
        producto.precio_venta = data.get("precio_venta", 0) or 0
        producto.fecha_vencimiento = data.get("fecha_vencimiento")
        producto.dias_alerta = data.get("dias_alerta", 30) or 30
        producto.save()

        return Response(ProductoSerializer(producto).data)

    producto.delete()
    return Response({"ok": True})


@api_view(["GET"])
@permission_classes([AllowAny])
def test_mail(request):
    destino = "maurcio1126@gmail.com"
    remitente = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER

    if not remitente or not settings.EMAIL_HOST_PASSWORD:
        return Response(
            {
                "ok": False,
                "error": "Faltan variables EMAIL_HOST_USER o EMAIL_HOST_PASSWORD para Brevo SMTP.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        send_mail(
            subject="Prueba de correo - Libro Fiscal v2",
            message="Este es un correo de prueba enviado desde /api/test-mail usando Brevo SMTP.",
            from_email=remitente,
            recipient_list=[destino],
            fail_silently=False,
        )
    except Exception as exc:
        return Response(
            {"ok": False, "error": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "ok": True,
            "message": "Correo de prueba enviado.",
            "destino": destino,
            "smtp_host": settings.EMAIL_HOST,
        }
    )


def test_mail_page(request):
    destino = "maurcio1126@gmail.com"
    remitente = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER

    if not remitente or not settings.EMAIL_HOST_PASSWORD:
        html = """
        <html><body style='font-family:Arial,sans-serif;padding:24px'>
        <h2 style='color:#b42318'>Error al enviar correo</h2>
        <p>Faltan variables EMAIL_HOST_USER o EMAIL_HOST_PASSWORD.</p>
        <p>Destino esperado: <strong>maurcio1126@gmail.com</strong></p>
        </body></html>
        """
        return HttpResponse(html, status=500)

    try:
        send_mail(
            subject="Prueba de correo - Libro Fiscal v2",
            message="Este es un correo de prueba enviado desde /test-mail usando Brevo SMTP.",
            from_email=remitente,
            recipient_list=[destino],
            fail_silently=False,
        )
    except Exception as exc:
        html = f"""
        <html><body style='font-family:Arial,sans-serif;padding:24px'>
        <h2 style='color:#b42318'>Fallo de envio</h2>
        <p>No se pudo enviar el correo de prueba.</p>
        <p><strong>Error:</strong> {str(exc)}</p>
        <p><strong>SMTP:</strong> {settings.EMAIL_HOST}:{settings.EMAIL_PORT}</p>
        <p><strong>Destino:</strong> {destino}</p>
        </body></html>
        """
        return HttpResponse(html, status=500)

    html = f"""
    <html><body style='font-family:Arial,sans-serif;padding:24px'>
    <h2 style='color:#067647'>Correo enviado correctamente</h2>
    <p>Se envio un correo de prueba exitosamente.</p>
    <p><strong>Destino:</strong> {destino}</p>
    <p><strong>SMTP:</strong> {settings.EMAIL_HOST}:{settings.EMAIL_PORT}</p>
    <p><strong>Remitente:</strong> {remitente}</p>
    </body></html>
    """
    return HttpResponse(html)
