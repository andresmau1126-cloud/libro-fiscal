from django.core.management.base import BaseCommand
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = "Crea usuarios de prueba (admin y usuario normal)"

    def handle(self, *args, **options):
        # Admin
        if not Usuario.objects.filter(email="admin@test.com").exists():
            Usuario.objects.create_user(
                email="admin@test.com",
                nombre="Administrador",
                password="admin123",
                rol="admin",
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS("Usuario admin creado: admin@test.com / admin123"))
        else:
            self.stdout.write(self.style.WARNING("Usuario admin@test.com ya existe"))

        # Usuario normal
        if not Usuario.objects.filter(email="usuario@test.com").exists():
            Usuario.objects.create_user(
                email="usuario@test.com",
                nombre="Usuario Prueba",
                password="usuario123",
                rol="usuario",
            )
            self.stdout.write(self.style.SUCCESS("Usuario normal creado: usuario@test.com / usuario123"))
        else:
            self.stdout.write(self.style.WARNING("Usuario usuario@test.com ya existe"))
