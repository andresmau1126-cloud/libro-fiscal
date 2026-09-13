from django.db import migrations


DEMO_PRODUCT_NAMES = {
    "Gas refrigerante R410A", "Gas refrigerante R22", "Gas refrigerante R134A",
    "Filtro secador 1/4", "Filtro secador 3/8", "Termostato universal",
    "Capacitor 35uf", "Capacitor 45uf", "Relay de arranque", "Tubo capilar",
    "Vaso desechable 9 oz", "Vaso desechable 12 oz", "Plato desechable 9 pulgadas",
    "Plato desechable 6 pulgadas", "Cubiertos desechables", "Servilletas paquete",
    "Bolsas plasticas medianas", "Pitillos paquete", "Contenedor comida 500ml",
    "Contenedor comida 1000ml", "Jabon liquido", "Desinfectante galon", "Cloro galon",
    "Desengrasante", "Limpiavidrios", "Esponja abrasiva", "Guantes de caucho",
    "Toalla absorbente", "Escoba", "Trapeador", "Arroz 1 kg", "Cafe 500 g",
    "Azucar 1 kg", "Harina de trigo", "Aceite vegetal 1L", "Sal 500 g",
    "Galletas surtidas", "Papas fritas paquete", "Gaseosa 1.5L", "Agua botella 600ml",
    "Jugo caja", "Bebida energetica",
}


def remove_demo_seed_data(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    Producto = apps.get_model("inventario", "Producto")
    Venta = apps.get_model("inventario", "Venta")
    DetalleVenta = apps.get_model("inventario", "DetalleVenta")
    HistorialInventario = apps.get_model("inventario", "HistorialInventario")
    HistorialVentas = apps.get_model("inventario", "HistorialVentas")
    EstadoInventario = apps.get_model("inventario", "EstadoInventarioCentralizado")
    Expense = apps.get_model("finanzas", "Expense")
    Movimiento = apps.get_model("movimientos", "Movimiento")

    demo_admin = Usuario.objects.filter(email="admin@sustentacion.local").first()
    if not demo_admin:
        return

    demo_sales = Venta.objects.filter(cliente__startswith="SUSTENTACION-")
    demo_sale_ids = list(demo_sales.values_list("id", flat=True))
    if demo_sale_ids:
        HistorialVentas.objects.filter(venta_id__in=demo_sale_ids).delete()
        HistorialInventario.objects.filter(venta_id__in=demo_sale_ids).delete()
        DetalleVenta.objects.filter(venta_id__in=demo_sale_ids).delete()
        demo_sales.delete()

    demo_expenses = Expense.objects.filter(descripcion__startswith="SUSTENTACION-")
    movement_ids = list(demo_expenses.values_list("movimiento_id", flat=True))
    demo_expenses.delete()
    Movimiento.objects.filter(id__in=[value for value in movement_ids if value]).delete()

    demo_products = Producto.objects.filter(propietario_id=demo_admin.id, nombre__in=DEMO_PRODUCT_NAMES)
    product_ids = list(demo_products.values_list("id", flat=True))
    if product_ids:
        EstadoInventario.objects.filter(producto_id__in=product_ids).delete()
        HistorialInventario.objects.filter(producto_id__in=product_ids).delete()
        demo_products.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("inventario", "0008_producto_proveedor"),
        ("finanzas", "0002_provider_contact"),
    ]

    operations = [migrations.RunPython(remove_demo_seed_data, migrations.RunPython.noop)]
