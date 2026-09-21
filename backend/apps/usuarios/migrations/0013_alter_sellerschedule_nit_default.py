from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0012_update_company_nit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sellerschedule",
            name="nit",
            field=models.CharField(default="1010085627-1", max_length=20),
        ),
    ]