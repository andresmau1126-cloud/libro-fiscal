#!/usr/bin/env python
"""
Script de pruebas para verificar el sistema de inventario centralizado.
Ejecutar: python backend/manage.py shell < scripts/test_inventario_centralizado.py
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.inventario.models import (
    Producto, Venta, DetalleVenta, HistorialInventario,
    HistorialVentas, EstadoInventarioCentralizado, ResumenVentasPorVendedor
)
from apps.inventario.services import InventarioCentralizadoService, VentasService

Usuario = get_user_model()


def print_separator(title=""):
    """Imprime un separador visual."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)


def test_modelos_creados():
    """Verifica que todos los modelos estén creados correctamente."""
    print_separator("1. Verificando Modelos Creados")
    
    try:
        # Contar registros
        print(f"✓ Productos: {Producto.objects.count()}")
        print(f"✓ Ventas: {Venta.objects.count()}")
        print(f"✓ HistorialInventario: {HistorialInventario.objects.count()}")
        print(f"✓ HistorialVentas: {HistorialVentas.objects.count()}")
        print(f"✓ EstadoInventarioCentralizado: {EstadoInventarioCentralizado.objects.count()}")
        print(f"✓ ResumenVentasPorVendedor: {ResumenVentasPorVendedor.objects.count()}")
        print("✓ Todos los modelos están funcionando correctamente")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_crear_producto_y_estado_centralizado():
    """Prueba crear un producto y su estado centralizado."""
    print_separator("2. Crear Producto y Estado Centralizado")
    
    try:
        # Crear usuario vendedor
        vendedor, _ = Usuario.objects.get_or_create(
            email="vendedor_prueba@test.com",
            defaults={
                "nombre": "Vendedor Prueba",
                "rol": "vendedor",
                "email_verified": True,
            }
        )
        print(f"✓ Usuario vendedor: {vendedor.nombre}")
        
        # Crear producto
        producto, created = Producto.objects.get_or_create(
            nombre="Arroz Premium",
            propietario=vendedor,
            defaults={
                "categoria": "Alimentos",
                "descripcion": "Arroz de calidad premium",
                "stock_actual": Decimal("100"),
                "stock_minimo": Decimal("10"),
                "costo_unitario": Decimal("1.50"),
                "precio_venta": Decimal("2.50"),
                "dias_alerta": 30,
            }
        )
        print(f"✓ Producto creado: {producto.nombre} (Stock: {producto.stock_actual})")
        
        # Verificar estado centralizado
        estado = EstadoInventarioCentralizado.objects.get(producto=producto)
        print(f"✓ Estado centralizado: Stock disponible = {estado.stock_disponible}")
        print(f"  Última actualización: {estado.ultima_actualizacion}")
        print(f"  Versión: {estado.version}")
        
        return True, vendedor, producto
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None, None


def test_registrar_movimiento_inventario(producto, vendedor):
    """Prueba registrar movimientos de inventario."""
    print_separator("3. Registrar Movimientos de Inventario")
    
    try:
        # Registrar entrada
        historial = InventarioCentralizadoService.registrar_movimiento_inventario(
            producto=producto,
            tipo_movimiento="entrada",
            cantidad_movida=Decimal("50"),
            usuario=vendedor,
            razon="Compra a proveedor"
        )
        print(f"✓ Entrada registrada: +{historial.cantidad_movida}")
        print(f"  Stock anterior: {historial.cantidad_anterior}")
        print(f"  Stock posterior: {historial.cantidad_posterior}")
        
        # Actualizar producto para próxima prueba
        producto.refresh_from_db()
        
        # Verificar estado centralizado actualizado
        estado = EstadoInventarioCentralizado.objects.get(producto=producto)
        print(f"✓ Estado centralizado actualizado: {estado.stock_disponible}")
        print(f"  Versión: {estado.version}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_crear_venta(producto, vendedor):
    """Prueba crear una venta con historial."""
    print_separator("4. Crear Venta con Historial")
    
    try:
        # Crear venta
        venta = VentasService.crear_venta_con_historial(
            cliente="Cliente Prueba",
            medio_pago="efectivo",
            detalles_venta=[
                {"producto_id": producto.id, "cantidad": Decimal("5")}
            ],
            vendedor=vendedor,
            dispositivo="Test Script"
        )
        print(f"✓ Venta creada: #{venta.id}")
        print(f"  Cliente: {venta.cliente}")
        print(f"  Total: ${venta.total}")
        print(f"  Vendedor: {venta.vendedor.nombre}")
        
        # Verificar historial de venta
        historial_venta = HistorialVentas.objects.get(venta=venta)
        print(f"✓ Historial de venta registrado:")
        print(f"  Cantidad de productos: {historial_venta.cantidad_productos}")
        print(f"  Cantidad de unidades: {historial_venta.cantidad_total_unidades}")
        print(f"  Monto total: ${historial_venta.monto_total}")
        print(f"  Ganancia: ${historial_venta.ganancia}")
        print(f"  Margen: {historial_venta.margen_ganancia}%")
        
        # Verificar stock actualizado
        producto.refresh_from_db()
        print(f"✓ Stock actualizado: {producto.stock_actual}")
        
        # Verificar historial de inventario
        historial_inv = HistorialInventario.objects.filter(venta=venta)
        print(f"✓ Historial de inventario registrado: {historial_inv.count()} movimiento(s)")
        
        return True, venta
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_estadisticas_vendedor(vendedor):
    """Prueba obtener estadísticas de un vendedor."""
    print_separator("5. Estadísticas de Vendedor")
    
    try:
        estadisticas = InventarioCentralizadoService.obtener_estadisticas_vendedor(vendedor.id)
        print(f"✓ Estadísticas para: {estadisticas['vendedor_nombre']}")
        print(f"  Ventas hoy: {estadisticas['cantidad_ventas_hoy']}")
        print(f"  Monto vendido hoy: ${estadisticas['monto_vendido_hoy']:.2f}")
        print(f"  Ganancia hoy: ${estadisticas['ganancia_hoy']:.2f}")
        print(f"  Ventas este mes: {estadisticas['cantidad_ventas_mes']}")
        print(f"  Monto vendido este mes: ${estadisticas['monto_vendido_mes']:.2f}")
        print(f"  Ganancia este mes: ${estadisticas['ganancia_mes']:.2f}")
        print(f"  Margen promedio (mes): {estadisticas['margen_promedio_mes']:.2f}%")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_historial_inventario(producto):
    """Prueba obtener historial de inventario."""
    print_separator("6. Historial de Inventario")
    
    try:
        historial = InventarioCentralizadoService.obtener_historial_inventario_por_producto(
            producto.id, dias=30
        )
        print(f"✓ Historial de {producto.nombre}:")
        print(f"  Total de movimientos: {historial.count()}")
        
        for i, mov in enumerate(historial[:5], 1):  # Mostrar últimos 5
            print(f"  {i}. {mov.get_tipo_movimiento_display()}: {mov.cantidad_movida}")
            print(f"     Usuario: {mov.usuario.nombre}")
            print(f"     Fecha: {mov.fecha.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_resumen_diario(vendedor):
    """Prueba obtener resumen de ventas diarias."""
    print_separator("7. Resumen de Ventas Diarias")
    
    try:
        hoy = timezone.now().date()
        resumen, _ = ResumenVentasPorVendedor.objects.get_or_create(
            vendedor=vendedor,
            fecha=hoy,
        )
        print(f"✓ Resumen para {vendedor.nombre} ({hoy}):")
        print(f"  Cantidad de ventas: {resumen.cantidad_ventas}")
        print(f"  Cantidad de unidades: {resumen.cantidad_unidades}")
        print(f"  Monto total: ${resumen.monto_total}")
        print(f"  Monto costo: ${resumen.monto_costo}")
        print(f"  Ganancia total: ${resumen.ganancia_total}")
        print(f"  Margen promedio: {resumen.margen_promedio}%")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_inventario_centralizado():
    """Prueba obtener inventario centralizado."""
    print_separator("8. Inventario Centralizado Actual")
    
    try:
        inventario = InventarioCentralizadoService.obtener_inventario_centralizado()
        print(f"✓ Inventario centralizado:")
        print(f"  Total de productos: {inventario.count()}")
        
        criticos = inventario.filter(es_critico=True)
        print(f"  Productos críticos: {criticos.count()}")
        
        for estado in inventario[:3]:  # Mostrar primeros 3
            print(f"  - {estado.producto.nombre}: {estado.stock_disponible} unidades")
            if estado.es_critico:
                print(f"    ⚠️ CRÍTICO (mínimo: {estado.producto.stock_minimo})")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_resumen_inventario():
    """Prueba obtener resumen general del inventario."""
    print_separator("9. Resumen General del Inventario")
    
    try:
        resumen = InventarioCentralizadoService.obtener_resumen_inventario_hoy()
        print(f"✓ Resumen del inventario:")
        print(f"  Total de productos: {resumen['total_productos']}")
        print(f"  Stock total: {resumen['total_stock']:.2f} unidades")
        print(f"  Valor total: ${resumen['valor_total']:.2f}")
        print(f"  Productos críticos: {resumen['productos_criticos']}")
        print(f"  Timestamp: {resumen['timestamp']}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print_separator("PRUEBAS DEL SISTEMA DE INVENTARIO CENTRALIZADO")
    
    results = []
    
    # Prueba 1: Verificar modelos
    results.append(("Modelos creados", test_modelos_creados()))
    
    # Prueba 2: Crear producto
    success, vendedor, producto = test_crear_producto_y_estado_centralizado()
    results.append(("Crear producto", success))
    
    if vendedor and producto:
        # Prueba 3: Registrar movimientos
        results.append(("Movimientos inventario", test_registrar_movimiento_inventario(producto, vendedor)))
        
        # Prueba 4: Crear venta
        success, venta = test_crear_venta(producto, vendedor)
        results.append(("Crear venta", success))
        
        # Prueba 5: Estadísticas
        results.append(("Estadísticas vendedor", test_estadisticas_vendedor(vendedor)))
        
        # Prueba 6: Historial
        results.append(("Historial inventario", test_historial_inventario(producto)))
        
        # Prueba 7: Resumen diario
        results.append(("Resumen diario", test_resumen_diario(vendedor)))
    
    # Prueba 8: Inventario centralizado
    results.append(("Inventario centralizado", test_inventario_centralizado()))
    
    # Prueba 9: Resumen general
    results.append(("Resumen inventario", test_resumen_inventario()))
    
    # Resumen final
    print_separator("RESUMEN DE PRUEBAS")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n✓ ¡TODOS LOS TESTS PASARON CORRECTAMENTE!")
        print("El sistema de inventario centralizado está funcionando correctamente.")
    else:
        print(f"\n✗ {total - passed} pruebas fallaron")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
