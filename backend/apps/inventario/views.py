from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.db.models.deletion import ProtectedError

from .models import (
    DetalleVenta, Producto, Venta,
    HistorialInventario, HistorialVentas, EstadoInventarioCentralizado,
    ResumenVentasPorVendedor,
)
from .serializers import (
    ProductoSerializer, ProductoCreateUpdateSerializer, VentaCreateSerializer,
    HistorialInventarioSerializer, HistorialVentasSerializer,
    EstadoInventarioCentralizadoSerializer, ResumenVentasPorVendedorSerializer,
    EstadisticasVendedorSerializer,
)
from .services import InventarioCentralizadoService, VentasService
from apps.usuarios.permissions import SELLER_ROLES, can_delete, can_view_all, can_write
from services.inventario_alertas import enviar_alerta_inventario
from services.scheduler_alertas import (
    iniciar_scheduler,
    detener_scheduler,
    obtener_estado_scheduler,
)


def _productos_qs_for_user(user):
    if can_view_all(user):
        return Producto.objects.filter(activo=True)
    return Producto.objects.filter(activo=True, propietario=user)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def productos_list_create(request):
    if request.method == "POST" and not can_write(request.user):
        return Response({"error": "Su rol solo tiene permisos de consulta"}, status=status.HTTP_403_FORBIDDEN)
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
@permission_classes([IsAuthenticated])
def producto_detail(request, producto_id):
    if request.method == "PUT" and not can_write(request.user):
        return Response({"error": "Su rol solo tiene permisos de consulta"}, status=status.HTTP_403_FORBIDDEN)
    if request.method == "DELETE" and not can_delete(request.user):
        return Response({"error": "Su rol solo tiene permisos de consulta"}, status=status.HTTP_403_FORBIDDEN)
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

    producto.activo = False
    producto.save(update_fields=["activo", "updated_at"])
    return Response({"ok": True})


def _venta_data(venta):
    return {
        "id": venta.id,
        "fecha": venta.fecha.isoformat(),
        "cliente": venta.cliente,
        "medio_pago": venta.medio_pago,
        "total": float(venta.total),
        "vendedor": venta.vendedor.nombre,
        "vendedor_email": venta.vendedor.email,
        "vendedor_rol": venta.vendedor.rol,
        "detalles": [
            {
                "producto_id": detalle.producto_id,
                "producto": detalle.producto.nombre,
                "cantidad": float(detalle.cantidad),
                "precio_unitario": float(detalle.precio_unitario),
                "subtotal": float(detalle.subtotal),
            }
            for detalle in venta.detalles.select_related("producto").all()
        ],
    }


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def ventas_list_create(request):
    if request.method == "POST" and not can_write(request.user):
        return Response({"error": "Su rol solo tiene permisos de consulta"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        fecha = request.query_params.get("fecha")
        qs = Venta.objects.select_related("vendedor").prefetch_related("detalles__producto")
        if can_view_all(request.user):
            if fecha:
                qs = qs.filter(fecha__date=fecha)
        else:
            qs = qs.filter(vendedor=request.user)
            if fecha:
                qs = qs.filter(fecha__date=fecha)
        ventas = [_venta_data(venta) for venta in qs[:100]]
        return Response({
            "ventas": ventas,
            "resumen": {
                "cantidad": len(ventas),
                "total": round(sum(item["total"] for item in ventas), 2),
            },
        })

    serializer = VentaCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    with transaction.atomic():
        detalles_data = []
        total = 0
        for item in data["detalles"]:
            try:
                producto = _productos_qs_for_user(request.user).select_for_update().get(
                    pk=item["producto_id"]
                )
            except Producto.DoesNotExist:
                return Response({"error": "Uno de los productos no existe en su inventario."}, status=status.HTTP_404_NOT_FOUND)
            if producto.fecha_vencimiento and producto.fecha_vencimiento < timezone.localdate():
                return Response({"error": f"{producto.nombre} está vencido y no se puede vender."}, status=status.HTTP_400_BAD_REQUEST)
            cantidad = item["cantidad"]
            if producto.stock_actual < cantidad:
                return Response({"error": f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}."}, status=status.HTTP_400_BAD_REQUEST)
            subtotal = cantidad * producto.precio_venta
            detalles_data.append((producto, cantidad, producto.precio_venta, subtotal))
            total += subtotal

        venta = Venta.objects.create(
            cliente=data.get("cliente", "").strip(),
            medio_pago=data["medio_pago"],
            total=total,
            vendedor=request.user,
        )
        venta.refresh_from_db()
        for producto, cantidad, precio, subtotal in detalles_data:
            producto.stock_actual -= cantidad
            producto.save(update_fields=["stock_actual", "updated_at"])
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=subtotal,
            )

    return Response(_venta_data(venta), status=status.HTTP_201_CREATED)


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


@api_view(["GET"])
@permission_classes([AllowAny])
def enviar_alertas_inventario_manual(request):
    """
    Dispara manualmente el envío de alertas de inventario.
    Detecta:
    - Productos con stock por debajo del mínimo
    - Productos próximos a vencer
    
    Query params:
    - email: email destino (default: ALERTA_EMAIL_DESTINO)
    """
    email = request.query_params.get("email") or settings.ALERTA_EMAIL_DESTINO
    resultado = enviar_alerta_inventario(destino=email)
    
    return Response(resultado, status=status.HTTP_200_OK if resultado["ok"] else status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def scheduler_alertas_start(request):
    """
    Inicia el scheduler automático de alertas de inventario.
    
    Body (JSON):
    {
      "hora": 7,      # 0-23 (default: 7 = 7 AM)
      "minuto": 0     # 0-59 (default: 0)
    }
    """
    try:
        data = request.data or {}
        hora = data.get("hora", 7)
        minuto = data.get("minuto", 0)
        
        if not isinstance(hora, int) or not (0 <= hora <= 23):
            return Response(
                {"ok": False, "error": "Hora debe ser un entero entre 0-23"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(minuto, int) or not (0 <= minuto <= 59):
            return Response(
                {"ok": False, "error": "Minuto debe ser un entero entre 0-59"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        iniciar_scheduler(hora=hora, minuto=minuto)
        estado = obtener_estado_scheduler()
        
        return Response(
            {
                "ok": True,
                "mensaje": f"Scheduler iniciado. Alertas programadas para las {hora:02d}:{minuto:02d} diariamente",
                "estado": estado,
            },
            status=status.HTTP_200_OK,
        )
    
    except Exception as e:
        return Response(
            {"ok": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def scheduler_alertas_status(request):
    """
    Obtiene el estado actual del scheduler de alertas.
    
    Respuesta:
    {
      "activo": bool,
      "proximo_disparo": datetime | null,
      "timestamp": ISO datetime
    }
    """
    estado = obtener_estado_scheduler()
    return Response({"ok": True, "estado": estado}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def scheduler_alertas_stop(request):
    """
    Detiene el scheduler automático de alertas de inventario.
    """
    try:
        detener_scheduler()
        estado = obtener_estado_scheduler()
        
        return Response(
            {
                "ok": True,
                "mensaje": "Scheduler detenido",
                "estado": estado,
            },
            status=status.HTTP_200_OK,
        )
    
    except Exception as e:
        return Response(
            {"ok": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ============================================================================
# ENDPOINTS PARA INVENTARIO CENTRALIZADO Y RASTREO EN TIEMPO REAL
# ============================================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inventario_centralizado_list(request):
    """
    Obtiene el estado centralizado del inventario compartido en tiempo real.
    
    Query params:
    - critico: "1" o "true" para filtrar solo productos con stock crítico
    - categoria: filtrar por categoría
    """
    critico = request.query_params.get("critico", "").strip() in ("1", "true")
    categoria = request.query_params.get("categoria", "").strip()
    
    inventario = InventarioCentralizadoService.obtener_inventario_centralizado(
        filtro_critico=critico
    )
    
    if categoria:
        inventario = inventario.filter(producto__categoria__icontains=categoria)
    
    serializer = EstadoInventarioCentralizadoSerializer(inventario, many=True)
    return Response({
        "inventario": serializer.data,
        "total_items": inventario.count(),
        "timestamp": timezone.now().isoformat(),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historial_inventario_producto(request, producto_id):
    """
    Obtiene el historial de movimientos de inventario de un producto.
    
    Query params:
    - dias: últimos N días a buscar (default: 30)
    """
    dias = int(request.query_params.get("dias", 30))
    
    try:
        producto = _productos_qs_for_user(request.user).get(pk=producto_id)
    except Producto.DoesNotExist:
        return Response(
            {"error": "Producto no existe"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    historial = InventarioCentralizadoService.obtener_historial_inventario_por_producto(
        producto_id, dias=dias
    )
    
    serializer = HistorialInventarioSerializer(historial, many=True)
    return Response({
        "producto_id": producto_id,
        "producto_nombre": producto.nombre,
        "historial": serializer.data,
        "total_movimientos": historial.count(),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historial_ventas_vendedor(request):
    """
    Obtiene el historial de ventas de un vendedor.
    
    Query params:
    - vendedor_id: ID del vendedor (si no se proporciona, usa el usuario actual)
    - dias: últimos N días (default: 30)
    
    Nota: Solo gerentes, administradores y auditores pueden ver vendedor_id diferentes
    """
    vendedor_id = request.query_params.get("vendedor_id")
    dias = int(request.query_params.get("dias", 30))
    
    # Validar permisos
    if vendedor_id:
        vendedor_id = int(vendedor_id)
        if not can_view_all(request.user) and vendedor_id != request.user.id:
            return Response(
                {"error": "No tiene permisos para ver historial de otro vendedor"},
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        vendedor_id = request.user.id
    
    historial = InventarioCentralizadoService.obtener_historial_ventas_vendedor(
        vendedor_id, dias=dias
    )
    
    serializer = HistorialVentasSerializer(historial, many=True)
    return Response({
        "vendedor_id": vendedor_id,
        "historial": serializer.data,
        "total_ventas": historial.count(),
        "timestamp": timezone.now().isoformat(),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def estadisticas_vendedor(request):
    """
    Obtiene estadísticas completas de un vendedor.
    
    Query params:
    - vendedor_id: ID del vendedor (si no se proporciona, usa el usuario actual)
    """
    vendedor_id = request.query_params.get("vendedor_id")
    
    if vendedor_id:
        vendedor_id = int(vendedor_id)
        if not can_view_all(request.user) and vendedor_id != request.user.id:
            return Response(
                {"error": "No tiene permisos para ver estadísticas de otro vendedor"},
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        vendedor_id = request.user.id
    
    estadisticas = InventarioCentralizadoService.obtener_estadisticas_vendedor(
        vendedor_id
    )
    
    serializer = EstadisticasVendedorSerializer(estadisticas)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumen_ventas_diarias(request):
    """
    Obtiene el resumen de ventas diarias.
    
    Query params:
    - vendedor_id: ID del vendedor (si no se proporciona, muestra todos)
    - fecha: fecha específica (YYYY-MM-DD)
    """
    vendedor_id = request.query_params.get("vendedor_id")
    fecha = request.query_params.get("fecha")
    
    resumen = ResumenVentasPorVendedor.objects.select_related("vendedor")
    
    if vendedor_id:
        if not can_view_all(request.user) and int(vendedor_id) != request.user.id:
            return Response(
                {"error": "No tiene permisos"},
                status=status.HTTP_403_FORBIDDEN
            )
        resumen = resumen.filter(vendedor_id=vendedor_id)
    elif not can_view_all(request.user):
        resumen = resumen.filter(vendedor=request.user)
    
    if fecha:
        resumen = resumen.filter(fecha=fecha)
    
    serializer = ResumenVentasPorVendedorSerializer(resumen, many=True)
    return Response({
        "resumen": serializer.data,
        "total_registros": resumen.count(),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def resumen_inventario_actual(request):
    """
    Obtiene un resumen general del estado actual del inventario.
    
    Solo disponible para gerentes, administradores y auditores.
    """
    if not can_view_all(request.user):
        return Response(
            {"error": "Acceso solo para gerentes, administradores y auditores"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    resumen = InventarioCentralizadoService.obtener_resumen_inventario_hoy()
    return Response(resumen)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def productos_criticos(request):
    """
    Obtiene la lista de productos con stock crítico (por debajo del mínimo).
    
    Solo disponible para gerentes, administradores y auditores.
    """
    if not can_view_all(request.user):
        return Response(
            {"error": "Acceso solo para gerentes, administradores y auditores"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    criticos = InventarioCentralizadoService.obtener_inventario_centralizado(
        filtro_critico=True
    )
    
    serializer = EstadoInventarioCentralizadoSerializer(criticos, many=True)
    return Response({
        "productos_criticos": serializer.data,
        "total": criticos.count(),
        "timestamp": timezone.now().isoformat(),
    })
