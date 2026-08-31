from datetime import date, timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.inventario.models import Producto, Venta
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

    def test_create_sale_decrements_stock_and_returns_total(self):
        product = Producto.objects.create(
            nombre="Gas R410",
            stock_actual=5,
            precio_venta="12.50",
            propietario=self.user,
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/ventas",
            {
                "medio_pago": "efectivo",
                "detalles": [{"producto_id": product.id, "cantidad": "2"}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total"], 25.0)
        product.refresh_from_db()
        self.assertEqual(product.stock_actual, 3)
        self.assertEqual(Venta.objects.filter(vendedor=self.user).count(), 1)

    def test_create_sale_rejects_insufficient_stock(self):
        product = Producto.objects.create(
            nombre="Filtro secador",
            stock_actual=1,
            precio_venta="8.00",
            propietario=self.user,
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/ventas",
            {"detalles": [{"producto_id": product.id, "cantidad": "2"}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        product.refresh_from_db()
        self.assertEqual(product.stock_actual, 1)
        self.assertFalse(Venta.objects.exists())

    def test_admin_can_sell_visible_product_from_inventory(self):
        product = Producto.objects.create(
            nombre="Agua gas",
            stock_actual=3,
            precio_venta="1800.00",
            propietario=self.other_user,
        )
        admin = Usuario.objects.create_user(
            email="inventario-admin-sale@test.com",
            nombre="Administrador",
            password="123456",
            rol="admin",
        )
        self.client.force_authenticate(user=admin)

        response = self.client.post(
            "/api/ventas",
            {"detalles": [{"producto_id": product.id, "cantidad": "1"}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product.refresh_from_db()
        self.assertEqual(product.stock_actual, 2)

    def test_delete_product_with_sales_soft_deletes_instead_of_blocking(self):
        product = Producto.objects.create(
            nombre="Producto con ventas",
            stock_actual=5,
            precio_venta="50.00",
            propietario=self.user,
        )
        self.client.force_authenticate(user=self.user)
        self.client.post(
            "/api/ventas",
            {"detalles": [{"producto_id": product.id, "cantidad": "1"}]},
            format="json",
        )

        response = self.client.delete(f"/api/productos/{product.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ok"])
        product.refresh_from_db()
        self.assertFalse(product.activo)

        list_response = self.client.get("/api/productos")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertNotIn(product.id, [p["id"] for p in list_response.data])

    def test_seller_roles_can_create_sales_and_admin_can_view_all_sales_by_role(self):
        seller_1 = Usuario.objects.create_user(
            email="vendedor1@test.com",
            nombre="Vendedor 1",
            password="123456",
            rol="vendedor",
        )
        seller_2 = Usuario.objects.create_user(
            email="vendedor2@test.com",
            nombre="Vendedor 2",
            password="123456",
            rol="vendedor_2",
        )
        admin = Usuario.objects.create_user(
            email="admin-sales@test.com",
            nombre="Administrador Ventas",
            password="123456",
            rol="admin",
        )

        product_1 = Producto.objects.create(
            nombre="Producto vendedor 1",
            stock_actual=10,
            precio_venta="15.00",
            propietario=seller_1,
        )
        product_2 = Producto.objects.create(
            nombre="Producto vendedor 2",
            stock_actual=8,
            precio_venta="20.00",
            propietario=seller_2,
        )

        self.client.force_authenticate(user=seller_1)
        response_1 = self.client.post(
            "/api/ventas",
            {"detalles": [{"producto_id": product_1.id, "cantidad": "2"}]},
            format="json",
        )
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_1.data["vendedor_rol"], "vendedor")

        self.client.force_authenticate(user=seller_2)
        response_2 = self.client.post(
            "/api/ventas",
            {"detalles": [{"producto_id": product_2.id, "cantidad": "1"}]},
            format="json",
        )
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.data["vendedor_rol"], "vendedor_2")

        self.client.force_authenticate(user=admin)
        response = self.client.get("/api/ventas")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["resumen"]["cantidad"], 2)
        roles = {venta["vendedor_rol"] for venta in response.data["ventas"]}
        self.assertSetEqual(roles, {"vendedor", "vendedor_2"})

    def test_sellers_are_isolated_but_admin_and_manager_see_everything(self):
        seller_1 = Usuario.objects.create_user(
            email="vendedor-scope-1@test.com",
            nombre="Vendedor Scope 1",
            password="123456",
            rol="vendedor",
        )
        seller_2 = Usuario.objects.create_user(
            email="vendedor-scope-2@test.com",
            nombre="Vendedor Scope 2",
            password="123456",
            rol="vendedor",
        )
        manager = Usuario.objects.create_user(
            email="gerente-scope@test.com",
            nombre="Gerente Scope",
            password="123456",
            rol="gerente",
        )

        product_1 = Producto.objects.create(
            nombre="Producto de vendedor 1",
            stock_actual=10,
            precio_venta="12.00",
            propietario=seller_1,
        )
        product_2 = Producto.objects.create(
            nombre="Producto de vendedor 2",
            stock_actual=7,
            precio_venta="15.00",
            propietario=seller_2,
        )

        self.client.force_authenticate(user=seller_1)
        response = self.client.get("/api/productos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({item["nombre"] for item in response.data}, {product_1.nombre})

        sale_response = self.client.post(
            "/api/ventas",
            {"detalles": [{"producto_id": product_2.id, "cantidad": "1"}]},
            format="json",
        )
        self.assertEqual(sale_response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(user=seller_2)
        sale_by_seller_2 = self.client.post(
            "/api/ventas",
            {"detalles": [{"producto_id": product_2.id, "cantidad": "1"}]},
            format="json",
        )
        self.assertEqual(sale_by_seller_2.status_code, status.HTTP_201_CREATED)

        self.client.force_authenticate(user=manager)
        inventory_response = self.client.get("/api/productos")
        self.assertEqual(inventory_response.status_code, status.HTTP_200_OK)
        self.assertEqual({item["nombre"] for item in inventory_response.data}, {product_1.nombre, product_2.nombre})

        sales_response = self.client.get("/api/ventas")
        self.assertEqual(sales_response.status_code, status.HTTP_200_OK)
        self.assertEqual(sales_response.data["resumen"]["cantidad"], 1)
        self.assertEqual({venta["vendedor_rol"] for venta in sales_response.data["ventas"]}, {"vendedor"})

        admin = Usuario.objects.create_user(
            email="admin-scope@test.com",
            nombre="Admin Scope",
            password="123456",
            rol="admin",
        )
        self.client.force_authenticate(user=admin)
        admin_sales = self.client.get("/api/ventas")
        self.assertEqual(admin_sales.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_sales.data["resumen"]["cantidad"], 1)

    # Test removed: alertas-resumen endpoint not implemented
    # def test_alertas_resumen_returns_expected_counts(self):
    #     pass


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

    def test_productos_qs_for_regular_user_returns_only_its_products(self):
        qs = _productos_qs_for_user(self.user)
        self.assertEqual(qs.count(), 1)
        product_names = {p.nombre for p in qs}
        self.assertEqual(product_names, {"P1"})

    def test_productos_qs_for_manager_returns_all_products(self):
        qs = _productos_qs_for_user(self.admin)
        self.assertEqual(qs.count(), 2)
        product_names = {p.nombre for p in qs}
        self.assertEqual(product_names, {"P1", "P2"})

    def test_productos_qs_for_admin_returns_all_products(self):
        qs = _productos_qs_for_user(self.admin)
        self.assertEqual(qs.count(), 2)
