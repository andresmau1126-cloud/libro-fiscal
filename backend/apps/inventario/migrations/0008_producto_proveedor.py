from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("finanzas", "0002_provider_contact"), ("inventario", "0007_venta_libro")]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="proveedor",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.PROTECT, related_name="productos", to="finanzas.provider"),
        ),
    ]