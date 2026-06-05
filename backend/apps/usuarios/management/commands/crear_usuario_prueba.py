from django.core.management.base import BaseCommand
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = "Crea usuarios de prueba (admin y usuario normal)"

    def handle(self, *args, **options):
        # Admin
        admin_email = "admin@test.com"
        admin_user, created = Usuario.objects.get_or_create(
            email=admin_email,
            defaults={
                "nombre": "Administrador",
                "password": "admin123",
                "rol": "admin",
                "is_staff": True,
                "is_superuser": True,
                "email_verified": True,
                "email_verification_code": "",
            },
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS("Usuario admin creado: admin@test.com / admin123"))
        else:
            updated = False
            if not admin_user.email_verified:
                admin_user.email_verified = True
                admin_user.email_verification_code = ""
                updated = True
            if not admin_user.is_staff:
                admin_user.is_staff = True
                updated = True
            if not admin_user.is_superuser:
                admin_user.is_superuser = True
                updated = True
            if updated:
                admin_user.save(update_fields=["email_verified", "email_verification_code", "is_staff", "is_superuser"])
                self.stdout.write(self.style.WARNING("Usuario admin@test.com ya existía, se marcó como verificado y actualizado"))
            else:
                self.stdout.write(self.style.WARNING("Usuario admin@test.com ya existe"))

        # Usuario admin principal
        principal_email = "andresmau1126@gmail.com"
        principal_user, created = Usuario.objects.get_or_create(
            email=principal_email,
            defaults={
                "nombre": "Andrés Mauricio",
                "password": "admin123",
                "rol": "admin",
                "is_staff": True,
                "is_superuser": True,
                "email_verified": True,
                "email_verification_code": "",
            },
        )
        if created:
            principal_user.set_password("admin123")
            principal_user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS("Usuario admin creado: andresmau1126@gmail.com / admin123"))
        else:
            updated = False
            if not principal_user.email_verified:
                principal_user.email_verified = True
                principal_user.email_verification_code = ""
                updated = True
            if not principal_user.is_staff:
                principal_user.is_staff = True
                updated = True
            if not principal_user.is_superuser:
                principal_user.is_superuser = True
                updated = True
            if updated:
                principal_user.save(update_fields=["email_verified", "email_verification_code", "is_staff", "is_superuser"])
                self.stdout.write(self.style.WARNING("Usuario andresmau1126@gmail.com ya existía, se marcó como verificado y actualizado"))
            else:
                self.stdout.write(self.style.WARNING("Usuario andresmau1126@gmail.com ya existe"))

        # Usuario normal
        normal_email = "usuario@test.com"
        normal_user, created = Usuario.objects.get_or_create(
            email=normal_email,
            defaults={
                "nombre": "Usuario Prueba",
                "password": "usuario123",
                "rol": "usuario",
                "email_verified": True,
                "email_verification_code": "",
            },
        )
        if created:
            normal_user.set_password("usuario123")
            normal_user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS("Usuario normal creado: usuario@test.com / usuario123"))
        else:
            if not normal_user.email_verified:
                normal_user.email_verified = True
                normal_user.email_verification_code = ""
                normal_user.save(update_fields=["email_verified", "email_verification_code"])
                self.stdout.write(self.style.WARNING("Usuario usuario@test.com ya existía, se marcó como verificado"))
            else:
                self.stdout.write(self.style.WARNING("Usuario usuario@test.com ya existe"))
