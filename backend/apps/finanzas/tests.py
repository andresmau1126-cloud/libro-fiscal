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
            nombre="Andres", nit="1010085627", anio=date.today().year, propietario=self.admin
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

    def test_auditor_cannot_create_expense(self):
        self.client.force_authenticate(user=self.auditor)
        response = self.client.post("/api/expenses", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
