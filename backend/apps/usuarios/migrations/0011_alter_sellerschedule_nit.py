from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0010_seed_seller_schedules"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sellerschedule",
            name="nit",
            field=models.CharField(default="1020085627-1", max_length=20),
        ),
    ]