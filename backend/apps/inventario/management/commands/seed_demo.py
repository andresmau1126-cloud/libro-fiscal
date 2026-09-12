from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.finanzas.models import Expense, Provider
from apps.inventario.models import DetalleVenta, Producto, Venta
from apps.libros.models import Libro
from apps.movimientos.models import Movimiento
from apps.usuarios.models import Usuario
from services.saldo import recompute_saldos
from services.ventas_libro import compilar_ventas_diarias

USERS = [
    ("admin@sustentacion.local", "Administrador", "admin", "admin123"),
    ("gerente@sustentacion.local", "Gerente", "gerente", "gerente123"),
    ("vendedor@sustentacion.local", "Vendedor", "vendedor", "vendedor123"),
    ("auditor@sustentacion.local", "Auditor", "auditor", "auditor123"),
]

PROVIDERS = [
    ("Frio Tecnico SAS", "900100001-1", "3001000001", "Cra 10 # 20-01"),
    ("Refrigeracion Central", "900100002-2", "3001000002", "Calle 11 # 21-02"),
    ("Empaques del Norte", "900100003-3", "3001000003", "Cra 12 # 22-03"),
    ("Desechables La 14", "900100004-4", "3001000004", "Calle 13 # 23-04"),
    ("Aseo Profesional", "900100005-5", "3001000005", "Cra 14 # 24-05"),
    ("Limpieza Total", "900100006-6", "3001000006", "Calle 15 # 25-06"),
    ("Abarrotes El Punto", "900100007-7", "3001000007", "Cra 16 # 26-07"),
    ("Distribuciones La Central", "900100008-8", "3001000008", "Calle 17 # 27-08"),
    ("Bebidas del Valle", "900100009-9", "3001000009", "Cra 18 # 28-09"),
    ("Refrescos y Jugos SAS", "900100010-0", "3001000010", "Calle 19 # 29-10"),
]

PRODUCTS = [
    ("Gas refrigerante R410A", "refrigeracion", 180, 250, 100, 10, 0),
    ("Gas refrigerante R22", "refrigeracion", 160, 230, 100, 10, 1),
    ("Gas refrigerante R134A", "refrigeracion", 150, 220, 100, 10, 0),
    ("Filtro secador 1/4", "refrigeracion", 18, 30, 100, 15, 1),
    ("Filtro secador 3/8", "refrigeracion", 22, 36, 100, 15, 1),
    ("Termostato universal", "refrigeracion", 25, 42, 100, 15, 0),
    ("Capacitor 35uf", "refrigeracion", 14, 25, 100, 15, 0),
    ("Capacitor 45uf", "refrigeracion", 17, 29, 100, 15, 1),
    ("Relay de arranque", "refrigeracion", 12, 22, 100, 15, 1),
    ("Tubo capilar", "refrigeracion", 8, 15, 100, 15, 0),
    ("Vaso desechable 9 oz", "desechables", 4, 7, 200, 30, 2),
    ("Vaso desechable 12 oz", "desechables", 5, 9, 200, 30, 2),
    ("Plato desechable 9 pulgadas", "desechables", 6, 10, 200, 30, 2),
    ("Plato desechable 6 pulgadas", "desechables", 4, 7, 200, 30, 3),
    ("Cubiertos desechables", "desechables", 5, 9, 200, 30, 3),
    ("Servilletas paquete", "desechables", 3, 5, 200, 30, 3),
    ("Bolsas plasticas medianas", "desechables", 7, 12, 200, 30, 2),
    ("Pitillos paquete", "desechables", 3, 6, 200, 30, 3),
    ("Contenedor comida 500ml", "desechables", 10, 16, 200, 30, 2),
    ("Contenedor comida 1000ml", "desechables", 14, 22, 200, 30, 3),
    ("Jabon liquido", "aseo", 12, 20, 100, 15, 4),
    ("Desinfectante galon", "aseo", 16, 26, 100, 15, 5),
    ("Cloro galon", "aseo", 10, 17, 100, 15, 4),
    ("Desengrasante", "aseo", 13, 22, 100, 15, 5),
    ("Limpiavidrios", "aseo", 9, 16, 100, 15, 4),
    ("Esponja abrasiva", "aseo", 2, 4, 100, 15, 5),
    ("Guantes de caucho", "aseo", 5, 9, 100, 15, 4),
    ("Toalla absorbente", "aseo", 8, 14, 100, 15, 5),
    ("Escoba", "aseo", 15, 25, 100, 15, 4),
    ("Trapeador", "aseo", 18, 30, 100, 15, 5),
    ("Arroz 1 kg", "abarrotes", 5, 8, 150, 20, 6),
    ("Cafe 500 g", "abarrotes", 18, 27, 150, 20, 7),
    ("Azucar 1 kg", "abarrotes", 4, 7, 150, 20, 6),
    ("Harina de trigo", "abarrotes", 5, 9, 150, 20, 7),
    ("Aceite vegetal 1L", "abarrotes", 8, 13, 150, 20, 6),
    ("Sal 500 g", "abarrotes", 2, 4, 150, 20, 7),
    ("Galletas surtidas", "abarrotes", 7, 12, 150, 20, 6),
    ("Papas fritas paquete", "abarrotes", 6, 10, 150, 20, 7),
    ("Gaseosa 1.5L", "bebidas", 8, 13, 150, 20, 8),
    ("Agua botella 600ml", "bebidas", 3, 6, 150, 20, 9),
    ("Jugo caja", "bebidas", 4, 8, 150, 20, 9),
    ("Bebida energetica", "bebidas", 7, 12, 150, 20, 8),
]


class Command(BaseCommand):
    help = "Precarga datos completos para sustentacion de Libro Fiscal."

    @transaction.atomic
    def handle(self, *args, **options):
        users = {}
        for email, nombre, rol, password in USERS:
            user, _ = Usuario.objects.get_or_create(email=email, defaults={"nombre": nombre, "rol": rol})
            changed = []
            for field, value in (("nombre", nombre), ("rol", rol)):
                if getattr(user, field) != value:
                    setattr(user, field, value)
                    changed.append(field)
            if not user.email_verified:
                user.email_verified = True
                user.email_verification_code = ""
                changed.extend(["email_verified", "email_verification_code"])
            if not user.check_password(password):
                user.set_password(password)
                changed.append("password")
            if changed:
                user.save(update_fields=sorted(set(changed + ["updated_at"])))
            users[rol] = user

        providers = []
        for nombre, nit, telefono, direccion in PROVIDERS:
            provider, _ = Provider.objects.update_or_create(
                nombre=nombre,
                defaults={"nit": nit, "telefono": telefono, "direccion": direccion, "activo": True},
            )
            providers.append(provider)

        libro, _ = Libro.objects.get_or_create(
            nit="1010085627", anio=timezone.localdate().year,
            defaults={"nombre": "Andres", "propietario": users["admin"]},
        )
        products = []
        for nombre, categoria, costo, precio, stock, minimo, provider_index in PRODUCTS:
            product, _ = Producto.objects.update_or_create(
                propietario=users["admin"], nombre=nombre,
                defaults={
                    "categoria": categoria, "descripcion": f"Producto de {categoria}",
                    "stock_actual": Decimal(stock), "stock_minimo": Decimal(minimo),
                    "costo_unitario": Decimal(costo), "precio_venta": Decimal(precio),
                    "proveedor": providers[provider_index], "activo": True,
                },
            )
            products.append(product)

        if not Venta.objects.filter(cliente__startswith="SUSTENTACION-").exists():
            for index in range(20):
                product = products[index % len(products)]
                sale = Venta.objects.create(
                    cliente=f"SUSTENTACION-{index + 1:02d}",
                    medio_pago="efectivo" if index % 2 == 0 else "transferencia",
                    turno="mañana", total=product.precio_venta,
                    vendedor=users["vendedor"], libro=libro,
                )
                DetalleVenta.objects.create(
                    venta=sale, producto=product, cantidad=1,
                    precio_unitario=product.precio_venta, subtotal=product.precio_venta,
                )

        if not Expense.objects.filter(descripcion__startswith="SUSTENTACION-").exists():
            for index in range(10):
                provider = providers[index % len(providers)]
                amount = Decimal("25") + Decimal(index * 5)
                movement = Movimiento.objects.create(
                    fecha=timezone.localdate(), descripcion=f"SUSTENTACION-EGRESO-{index + 1:02d}",
                    ingresos=0, egresos=amount, libro=libro,
                )
                Expense.objects.create(
                    provider=provider, descripcion=f"SUSTENTACION-EGRESO-{index + 1:02d}",
                    fecha=timezone.localdate(), descripcion_producto=products[index].nombre,
                    valor_unitario=amount, valor_pagado=amount, cantidad=1, libro=libro,
                    creado_por=users["admin"], movimiento=movement,
                )

        compilar_ventas_diarias(timezone.localdate())
        recompute_saldos(libro.id)
        self.stdout.write(self.style.SUCCESS("Seed completo aplicado: 4 usuarios, 10 proveedores, 42 productos, 20 ventas y 10 egresos."))
