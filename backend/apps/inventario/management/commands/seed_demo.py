from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.finanzas.models import Provider
from apps.inventario.models import Producto
from apps.libros.models import Libro
from apps.usuarios.models import Usuario


USERS = [
    ("admin@sustentacion.local", "Administrador", "admin", "Admin12345!"),
    ("gerente@sustentacion.local", "Gerente", "gerente", "Gerente12345!"),
    ("auditor@sustentacion.local", "Auditor", "auditor", "Auditor12345!"),
    ("vendedor@sustentacion.local", "Vendedor", "vendedor", "Vendedor12345!"),
]

PRODUCTS = [
    ("Gas refrigerante R410A", "refrigeracion", "Cilindro para mantenimiento", "10", "2", "180", "250"),
    ("Filtro secador 1/4", "refrigeracion", "Repuesto de refrigeracion", "20", "5", "18", "30"),
    ("Vaso desechable 9 oz", "desechables", "Paquete para despacho", "100", "20", "4", "7"),
    ("Servilletas", "desechables", "Paquete institucional", "80", "15", "3", "5"),
    ("Jabon liquido", "aseo", "Limpieza de superficies", "25", "5", "12", "20"),
    ("Desinfectante", "aseo", "Galon", "18", "4", "16", "26"),
    ("Arroz 1 kg", "abarrotes", "Producto de consumo", "50", "10", "5", "8"),
    ("Cafe 500 g", "abarrotes", "Producto de consumo", "30", "6", "18", "27"),
]


class Command(BaseCommand):
    help = "Crea datos idempotentes para demostracion y sustentacion."

    @transaction.atomic
    def handle(self, *args, **options):
        users = {}
        for email, nombre, rol, password in USERS:
            user, created = Usuario.objects.get_or_create(
                email=email,
                defaults={"nombre": nombre, "rol": rol, "email_verified": True},
            )
            changed = []
            if user.nombre != nombre:
                user.nombre = nombre
                changed.append("nombre")
            if user.rol != rol:
                user.rol = rol
                changed.append("rol")
            if not user.email_verified:
                user.email_verified = True
                changed.append("email_verified")
            if created or not user.check_password(password):
                user.set_password(password)
                changed.append("password")
            if changed:
                user.save(update_fields=sorted(set(changed + ["updated_at"])))
            users[rol] = user

        libro, _ = Libro.objects.get_or_create(
            nit="1010085627",
            anio=timezone.localdate().year,
            defaults={"nombre": "Andres", "propietario": users["admin"]},
        )
        if libro.nombre != "Andres":
            libro.nombre = "Andres"
            libro.save(update_fields=["nombre"])

        for nombre, categoria, descripcion, stock, minimo, costo, precio in PRODUCTS:
            Producto.objects.update_or_create(
                propietario=users["admin"],
                nombre=nombre,
                defaults={
                    "categoria": categoria,
                    "descripcion": descripcion,
                    "stock_actual": Decimal(stock),
                    "stock_minimo": Decimal(minimo),
                    "costo_unitario": Decimal(costo),
                    "precio_venta": Decimal(precio),
                    "activo": True,
                },
            )

        for nombre in ("Proveedor Refrigeracion SAS", "Distribuciones La Central", "Aseo Integral Ltda"):
            Provider.objects.get_or_create(nombre=nombre, defaults={"activo": True})

        self.stdout.write(self.style.SUCCESS("Seed de sustentacion aplicado correctamente."))
        self.stdout.write("NIT: 1010085627")
        self.stdout.write("Usuarios: admin, gerente, auditor y vendedor en dominio sustentacion.local")
        self.stdout.write(f"Productos precargados: {len(PRODUCTS)}")
