import os
from django.apps import AppConfig


def _seed_default_users():
    try:
        from .models import Usuario

        default_users = [
            {
                "email": "andresmau1126@gmail.com",
                "nombre": "Andrés Mauricio",
                "password": "admin123",
                "is_superuser": True,
                "is_staff": True,
                "rol": "admin",
            },
            {
                "email": "admin@test.com",
                "nombre": "Administrador",
                "password": "admin123",
                "is_superuser": True,
                "is_staff": True,
                "rol": "admin",
            },
            {
                "email": "usuario@test.com",
                "nombre": "Usuario Prueba",
                "password": "usuario123",
                "rol": "usuario",
            },
        ]

        for user_data in default_users:
            email = user_data["email"].strip().lower()
            try:
                user = Usuario.objects.get(email__iexact=email)
                created = False
            except Usuario.DoesNotExist:
                user = Usuario.objects.create_user(
                    email=email,
                    nombre=user_data["nombre"],
                    password=user_data["password"],
                    rol=user_data.get("rol", "usuario"),
                    is_staff=user_data.get("is_staff", False),
                    is_superuser=user_data.get("is_superuser", False),
                    email_verified=True,
                )
                created = True

            if not created:
                update_fields = []
                if not user.email_verified:
                    user.email_verified = True
                    user.email_verification_code = ""
                    update_fields.extend(["email_verified", "email_verification_code"])
                if user_data.get("is_staff", False) and not user.is_staff:
                    user.is_staff = True
                    update_fields.append("is_staff")
                if user_data.get("is_superuser", False) and not user.is_superuser:
                    user.is_superuser = True
                    update_fields.append("is_superuser")
                if user.rol != user_data.get("rol", "usuario"):
                    user.rol = user_data.get("rol", "usuario")
                    update_fields.append("rol")
                if user.nombre != user_data["nombre"]:
                    user.nombre = user_data["nombre"]
                    update_fields.append("nombre")
                if update_fields:
                    user.save(update_fields=update_fields + ["updated_at"])
    except Exception:
        # Evitar que fallos de la base de datos detengan el arranque
        return


class UsuariosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.usuarios"
    verbose_name = "Usuarios"

    def ready(self):
        if os.getenv("DISABLE_DEFAULT_USER_SEEDING", "").lower() in ("1", "true", "yes"):
            return
        _seed_default_users()
