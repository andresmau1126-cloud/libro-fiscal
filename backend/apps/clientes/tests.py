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
