from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventario", "0011_alter_detalleventa_cantidad_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="venta",
            name="cliente_nit",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
    ]