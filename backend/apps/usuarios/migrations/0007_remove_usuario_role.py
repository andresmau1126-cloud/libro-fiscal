from django.db import migrations, models


def migrate_usuario_role(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    Usuario.objects.filter(rol="usuario").update(rol="vendedor")


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0006_roles"),
    ]

    operations = [
        migrations.RunPython(migrate_usuario_role, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="usuario",
            name="rol",
            field=models.CharField(
                choices=[
                    ("admin", "Administrador"),
                    ("vendedor", "Vendedor"),
                    ("gerente", "Gerente"),
                    ("auditor", "Auditor"),
                ],
                default="vendedor",
                max_length=10,
            ),
        ),
    ]