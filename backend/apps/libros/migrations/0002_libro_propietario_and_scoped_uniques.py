from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0001_initial"),
        ("libros", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="libro",
            name="propietario",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="libros",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RemoveConstraint(
            model_name="libro",
            name="uniq_libro",
        ),
        migrations.RemoveConstraint(
            model_name="libro",
            name="uniq_libro_nombre_anio",
        ),
        migrations.AddConstraint(
            model_name="libro",
            constraint=models.UniqueConstraint(fields=("propietario", "nit", "anio"), name="uniq_libro_owner"),
        ),
        migrations.AddConstraint(
            model_name="libro",
            constraint=models.UniqueConstraint(fields=("propietario", "nombre", "anio"), name="uniq_libro_owner_nombre_anio"),
        ),
    ]
