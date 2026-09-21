from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0008_alter_usuario_rol"),
    ]

    operations = [
        migrations.CreateModel(
            name="SellerSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("start_time", models.TimeField(default="08:00:00")),
                ("end_time", models.TimeField(default="19:00:00")),
                ("is_active", models.BooleanField(default=True)),
                ("nit", models.CharField(default="1020085627-1", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="seller_schedules", to="usuarios.usuario")),
            ],
            options={
                "db_table": "seller_schedules",
                "verbose_name": "Horario vendedor",
                "verbose_name_plural": "Horarios vendedores",
            },
        ),
    ]
