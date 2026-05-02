from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Producto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=180)),
                ("categoria", models.CharField(blank=True, default="", max_length=120)),
                ("descripcion", models.CharField(blank=True, default="", max_length=255)),
                ("stock_actual", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("stock_minimo", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("costo_unitario", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("precio_venta", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "propietario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.CASCADE,
                        related_name="productos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Producto",
                "verbose_name_plural": "Productos",
                "db_table": "inventario_producto",
                "ordering": ["nombre", "id"],
            },
        ),
        migrations.AddConstraint(
            model_name="producto",
            constraint=models.UniqueConstraint(fields=("propietario", "nombre"), name="uniq_producto_owner_nombre"),
        ),
    ]
