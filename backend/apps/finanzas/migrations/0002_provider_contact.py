from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("finanzas", "0001_initial")]

    operations = [
        migrations.AddField(model_name="provider", name="nit", field=models.CharField(blank=True, default="", max_length=50)),
        migrations.AddField(model_name="provider", name="telefono", field=models.CharField(blank=True, default="", max_length=50)),
        migrations.AddField(model_name="provider", name="direccion", field=models.CharField(blank=True, default="", max_length=255)),
    ]