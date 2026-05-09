from datetime import date, timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.inventario.models import Producto
from apps.inventario.views import _productos_qs_for_user
from apps.usuarios.models import Usuario


class InventarioBlackBoxAPITests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="inventario@test.com",
            nombre="Inventario",
            password="123456",
        )
        self.other_user = Usuario.objects.create_user(
            email="inventario2@test.com",
            nombre="Inventario 2",
            password="123456",
        )

    def test_productos_requires_authentication(self):
        response = self.client.get("/api/productos")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_duplicate_producto_same_user_returns_409(self):
        Producto.objects.create(
            nombre="Arroz",
            stock_actual=10,
            stock_minimo=2,
            propietario=self.user,
        )

        self.client.force_authenticate(user=self.user)
        payload = {
            "nombre": "Arroz",
            "categoria": "Granos",
            "descripcion": "Presentacion 1kg",
            "stock_actual": "5.00",
            "stock_minimo": "1.00",
            "costo_unitario": "2.50",
            "precio_venta": "3.50",
            "fecha_vencimiento": None,
            "dias_alerta": 30,
        }
        response = self.client.post("/api/productos", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("ya está registrado", response.data["error"])

    def test_low_stock_filter_returns_only_low_stock_products(self):
        Producto.objects.create(
            nombre="Producto Bajo",
            stock_actual=3,
            stock_minimo=5,
            propietario=self.user,
        )
        Producto.objects.create(
            nombre="Producto Normal",
            stock_actual=10,
            stock_minimo=2,
            propietario=self.user,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/productos?low_stock=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nombre"], "Producto Bajo")

    def test_alertas_resumen_returns_expected_counts(self):
        hoy = date.today()
        Producto.objects.create(
            nombre="Bajo stock",
            stock_actual=1,
            stock_minimo=2,
            propietario=self.user,
            dias_alerta=5,
        )
        Producto.objects.create(
            nombre="Por vencer",
            stock_actual=10,
            stock_minimo=2,
            fecha_vencimiento=hoy + timedelta(days=2),
            dias_alerta=3,
            propietario=self.user,
        )
        Producto.objects.create(
            nombre="Vencido",
            stock_actual=10,
            stock_minimo=2,
            fecha_vencimiento=hoy - timedelta(days=1),
            dias_alerta=10,
            propietario=self.user,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/alertas-resumen")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bajo_stock"], 1)
        self.assertEqual(response.data["por_vencer"], 1)
        self.assertEqual(response.data["vencidos"], 1)
        self.assertEqual(response.data["total"], 3)


class InventarioWhiteBoxTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="inventario-white@test.com",
            nombre="Inventario White",
            password="123456",
            rol="usuario",
        )
        self.admin = Usuario.objects.create_user(
            email="inventario-admin@test.com",
            nombre="Admin",
            password="123456",
            rol="admin",
        )
        Producto.objects.create(nombre="P1", propietario=self.user)
        Producto.objects.create(nombre="P2", propietario=self.admin)

    def test_productos_qs_for_regular_user_returns_only_owned_products(self):
        qs = _productos_qs_for_user(self.user)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().nombre, "P1")

    def test_productos_qs_for_admin_returns_all_products(self):
        qs = _productos_qs_for_user(self.admin)
        self.assertEqual(qs.count(), 2)
