from django.db import migrations


def update_company_nit(apps, schema_editor):
    SellerSchedule = apps.get_model("usuarios", "SellerSchedule")
    SellerSchedule.objects.filter(nit="1020085627-1").update(nit="1010085627-1")


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0011_alter_sellerschedule_nit"),
    ]

    operations = [
        migrations.RunPython(update_company_nit, migrations.RunPython.noop),
    ]