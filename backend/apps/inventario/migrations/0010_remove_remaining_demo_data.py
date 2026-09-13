from django.db import migrations


DEMO_USER_EMAILS = {
    "admin@sustentacion.local",
    "gerente@sustentacion.local",
    "vendedor@sustentacion.local",
    "auditor@sustentacion.local",
}

DEMO_PROVIDER_NAMES = {
    "Frio Tecnico SAS", "Refrigeracion Central", "Empaques del Norte",
    "Desechables La 14", "Aseo Profesional", "Limpieza Total",
    "Abarrotes El Punto", "Distribuciones La Central", "Bebidas del Valle",
    "Refrescos y Jugos SAS",
}


def remove_remaining_demo_data(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    Producto = apps.get_model("inventario", "Producto")
    Venta = apps.get_model("inventario", "Venta")
    DetalleVenta = apps.get_model("inventario", "DetalleVenta")
    HistorialInventario = apps.get_model("inventario", "HistorialInventario")
    HistorialVentas = apps.get_model("inventario", "HistorialVentas")
    EstadoInventario = apps.get_model("inventario", "EstadoInventarioCentralizado")
    Provider = apps.get_model("finanzas", "Provider")
    Expense = apps.get_model("finanzas", "Expense")
    SellerStats = apps.get_model("finanzas", "SellerStats")
    Movimiento = apps.get_model("movimientos", "Movimiento")
    Libro = apps.get_model("libros", "Libro")

    demo_users = Usuario.objects.filter(email__in=DEMO_USER_EMAILS)
    demo_user_ids = list(demo_users.values_list("id", flat=True))
    if not demo_user_ids:
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

    demo_products = Producto.objects.filter(propietario_id__in=demo_user_ids)
    product_ids = list(demo_products.values_list("id", flat=True))
    if product_ids:
        EstadoInventario.objects.filter(producto_id__in=product_ids).delete()
        HistorialInventario.objects.filter(producto_id__in=product_ids).delete()
        demo_products.delete()

    Libro.objects.filter(propietario_id__in=demo_user_ids, nit="1010085627").delete()
    SellerStats.objects.filter(vendedor_id__in=demo_user_ids).delete()
    for provider in Provider.objects.filter(nombre__in=DEMO_PROVIDER_NAMES):
        if not provider.productos.exists() and not provider.expenses.exists():
            provider.delete()

    demo_users.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("inventario", "0009_remove_demo_seed_data"),
    ]

    operations = [migrations.RunPython(remove_remaining_demo_data, migrations.RunPython.noop)]