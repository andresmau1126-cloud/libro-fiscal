from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone

from apps.inventario.models import Producto, Venta
from apps.turnos.models import Turno
from apps.usuarios.models import Usuario


class ClientesAPITests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="cliente-test@test.com",
            nombre="Vendedor cliente",
            password="123456",
        )
        self.client.force_authenticate(user=self.user)

    def test_nit_is_unique(self):
        payload = {"nombre": "Cliente Uno", "nit": "900123456-1"}
        first = self.client.post("/api/clientes", payload, format="json")
        duplicate = self.client.post("/api/clientes", payload | {"nombre": "Cliente Dos"}, format="json")

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sale_is_linked_to_registered_client(self):
        client_response = self.client.post(
            "/api/clientes",
            {"nombre": "Cliente Venta", "nit": "800123456-2"},
            format="json",
        )
        product = Producto.objects.create(nombre="Producto cliente", stock_actual=2, precio_venta="10.00", propietario=self.user)
        Turno.objects.create(vendedor=self.user, fecha=timezone.localdate())
        sale_response = self.client.post(
            "/api/ventas",
            {
                "cliente_id": client_response.data["id"],
                "detalles": [{"producto_id": product.id, "cantidad": "1"}],
            },
            format="json",
        )

        self.assertEqual(sale_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Venta.objects.get(pk=sale_response.data["id"]).cliente_registro_id, client_response.data["id"])

    def test_daily_sales_are_consolidated_by_seller(self):
        second_seller = Usuario.objects.create_user(
            email="cliente-test-2@test.com",
            nombre="Segundo vendedor",
            password="123456",
            rol="vendedor_2",
        )
        Venta.objects.create(vendedor=self.user, total="25.00")
        Venta.objects.create(vendedor=self.user, total="15.00")
        Venta.objects.create(vendedor=second_seller, total="60.00")

        supervisor = Usuario.objects.create_user(
            email="cliente-test-admin@test.com",
            nombre="Supervisor clientes",
            password="123456",
            rol="admin",
        )
        self.client.force_authenticate(user=supervisor)

        response = self.client.get("/api/resumen/ventas-diarias")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_dia"], 100.0)
        self.assertEqual(
            {(row["vendedor"], row["monto_total"]) for row in response.data["resumen"]},
            {("Vendedor cliente", 40.0), ("Segundo vendedor", 60.0)},
        )
