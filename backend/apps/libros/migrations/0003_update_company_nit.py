from django.db import migrations


def update_company_nit(apps, schema_editor):
    Libro = apps.get_model("libros", "Libro")
    Libro.objects.filter(nit="1020085627-1").update(nit="1010085627-1")


class Migration(migrations.Migration):
    dependencies = [
        ("libros", "0002_libro_propietario_and_scoped_uniques"),
    ]

    operations = [
        migrations.RunPython(update_company_nit, migrations.RunPython.noop),
    ]