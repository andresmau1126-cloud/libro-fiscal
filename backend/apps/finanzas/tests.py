from datetime import date
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from apps.finanzas.models import Expense, Provider
from apps.libros.models import Libro
from apps.movimientos.models import Movimiento
from apps.usuarios.models import Usuario


class FinanzasPermissionsAndFiscalTests(APITestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            email="finanzas-admin@test.com",
            nombre="Admin",
            password="123456",
            rol="admin",
        )
        self.auditor = Usuario.objects.create_user(
            email="finanzas-auditor@test.com",
            nombre="Auditor",
            password="123456",
            rol="auditor",
        )
        self.libro = Libro.objects.create(
            nombre="Multivariedades Ricaurte", nit="1020085627-1", anio=date.today().year, propietario=self.admin
        )
        self.provider = Provider.objects.create(nombre="Proveedor prueba")

    def test_admin_expense_creates_movement_and_recomputes_balance(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/expenses",
            {
                "provider": self.provider.id,
                "descripcion": "Compra de insumos",
                "fecha": date.today().isoformat(),
                "descripcion_producto": "Material de aseo",
                "valor_unitario": "25.00",
                "valor_pagado": "50.00",
                "cantidad": "2.00",
                "libro": self.libro.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expense = Expense.objects.get(pk=response.data["id"])
        movement = Movimiento.objects.get(expense=expense)
        self.assertEqual(movement.egresos, Decimal("50.00"))
        self.assertEqual(movement.saldo, Decimal("-50.00"))

    def test_admin_can_create_expense_with_large_value_without_validation_error(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/expenses",
            {
                "provider": self.provider.id,
                "descripcion": "Compra de gran monto",
                "fecha": date.today().isoformat(),
                "descripcion_producto": "Producto grande",
                "valor_unitario": "1234567890123.45",
                "valor_pagado": "1234567890123.45",
                "cantidad": "1.00",
                "libro": self.libro.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)

    def test_auditor_cannot_create_expense(self):
        self.client.force_authenticate(user=self.auditor)
        response = self.client.post("/api/expenses", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_expense_and_its_movement(self):
        expense = Expense.objects.create(
            provider=self.provider,
            descripcion="Compra original",
            fecha=date.today(),
            descripcion_producto="Material original",
            valor_unitario=Decimal("25.00"),
            valor_pagado=Decimal("50.00"),
            cantidad=Decimal("2.00"),
            libro=self.libro,
            creado_por=self.admin,
        )
        movement = Movimiento.objects.create(
            fecha=expense.fecha,
            descripcion=expense.descripcion,
            ingresos=0,
            egresos=expense.valor_pagado,
            libro=self.libro,
        )
        expense.movimiento = movement
        expense.save(update_fields=["movimiento"])

        self.client.force_authenticate(user=self.admin)
        response = self.client.put(
            f"/api/expenses/{expense.id}",
            {
                "provider": self.provider.id,
                "descripcion": "Compra actualizada",
                "fecha": date.today().isoformat(),
                "descripcion_producto": "Material actualizado",
                "valor_unitario": "40.00",
                "valor_pagado": "80.00",
                "cantidad": "2.00",
                "libro": self.libro.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        movement.refresh_from_db()
        self.assertEqual(expense.valor_pagado, Decimal("80.00"))
        self.assertEqual(movement.egresos, Decimal("80.00"))
        self.assertEqual(movement.descripcion, "Compra actualizada")
