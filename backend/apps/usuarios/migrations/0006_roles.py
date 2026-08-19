from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0005_rename_otps_usuario_codigo_tipo_idx_otps_usuario_2f7071_idx"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usuario",
            name="rol",
            field=models.CharField(
                choices=[
                    ("admin", "Administrador"),
                    ("vendedor", "Vendedor"),
                    ("gerente", "Gerente"),
                    ("auditor", "Auditor"),
                    ("usuario", "Usuario"),
                ],
                default="usuario",
                max_length=10,
            ),
        ),
    ]