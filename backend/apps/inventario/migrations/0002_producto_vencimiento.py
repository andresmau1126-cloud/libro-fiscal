from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="fecha_vencimiento",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="producto",
            name="dias_alerta",
            field=models.IntegerField(default=30),
        ),
    ]
