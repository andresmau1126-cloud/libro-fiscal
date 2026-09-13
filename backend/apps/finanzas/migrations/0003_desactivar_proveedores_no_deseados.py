from django.db import migrations


def desactivar_proveedores(apps, schema_editor):
    Provider = apps.get_model("finanzas", "Provider")
    Provider.objects.filter(
        nombre__in=["Aseo Integral Ltda", "Proveedor Refrigeracion SAS"]
    ).update(activo=False)


def reactivar_proveedores(apps, schema_editor):
    Provider = apps.get_model("finanzas", "Provider")
    Provider.objects.filter(
        nombre__in=["Aseo Integral Ltda", "Proveedor Refrigeracion SAS"]
    ).update(activo=True)


class Migration(migrations.Migration):
    dependencies = [
        ("finanzas", "0002_provider_contact"),
    ]

    operations = [
        migrations.RunPython(desactivar_proveedores, reactivar_proveedores),
    ]