from datetime import date, datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.finanzas.models import Expense
from apps.inventario.models import Venta
from apps.libros.models import Libro
from apps.movimientos.models import Movimiento
from apps.movimientos.views import _build_filters
from apps.usuarios.models import Usuario
from services.saldo import recompute_saldos


class MovimientosBlackBoxAPITests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="usuario@test.com",
            nombre="Usuario",
            password="123456",
            rol="admin",
        )
        self.other_user = Usuario.objects.create_user(
            email="otro@test.com",
            nombre="Otro",
            password="123456",
        )
        self.libro = Libro.objects.create(
            nombre="Libro 2026",
            nit="1234567",
            anio=2026,
            propietario=self.user,
        )
        self.other_libro = Libro.objects.create(
            nombre="Libro Otro",
            nit="7654321",
            anio=2026,
            propietario=self.other_user,
        )

    def test_entries_requires_authentication(self):
        response = self.client.get("/api/entries")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_entry_recomputes_saldo_and_returns_201(self):
        Movimiento.objects.create(
            fecha=date(2026, 1, 1),
            descripcion="Saldo inicial",
            ingresos=Decimal("100.00"),
            egresos=Decimal("0.00"),
            saldo=Decimal("0.00"),
            libro=self.libro,
        )

        self.client.force_authenticate(user=self.user)
        payload = {
            "fecha": "2026-01-02",
            "descripcion": "Compra de utiles",
            "ingresos": "0.00",
            "egresos": "30.00",
            "libro_id": self.libro.id,
        }
        response = self.client.post("/api/entries", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["saldo"], 70.0)

        saldos = list(
            Movimiento.objects.filter(libro=self.libro)
            .order_by("fecha", "id")
            .values_list("saldo", flat=True)
        )
        self.assertEqual(saldos, [Decimal("100.00"), Decimal("70.00")])

    def test_create_entry_rejects_fecha_fuera_del_anio(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "fecha": "2025-12-31",
            "descripcion": "Fecha invalida",
            "ingresos": "10.00",
            "egresos": "0.00",
            "libro_id": self.libro.id,
        }

        response = self.client.post("/api/entries", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("año 2026", response.data["error"])

    def test_create_entry_returns_404_for_libro_from_other_user(self):
        seller = Usuario.objects.create_user(
            email="seller-isolation@test.com",
            nombre="Seller isolation",
            password="123456",
            rol="vendedor",
        )
        self.client.force_authenticate(user=seller)
        payload = {
            "fecha": "2026-01-10",
            "descripcion": "Intento ajeno",
            "ingresos": "15.00",
            "egresos": "0.00",
            "libro_id": self.other_libro.id,
        }

        response = self.client.post("/api/entries", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_november_0011_view_uses_real_transactions_and_ignores_manual_and_simulated_rows(self):
        libro = Libro.objects.create(
            nombre="Libro Folio 0011",
            nit="1010085627-1",
            anio=2026,
            propietario=self.user,
        )
        sale_date = timezone.make_aware(datetime(2026, 11, 8))
        Venta.objects.create(
            fecha=sale_date,
            total=Decimal("100.00"),
            vendedor=self.user,
            libro=libro,
        )
        Venta.objects.create(
            fecha=sale_date,
            total=Decimal("900.00"),
            vendedor=self.user,
            libro=libro,
            es_simulado=True,
        )
        Expense.objects.create(
            descripcion="Compra real",
            fecha=date(2026, 11, 8),
            descripcion_producto="Mercancía",
            valor_unitario=Decimal("20.00"),
            valor_pagado=Decimal("20.00"),
            cantidad=Decimal("1.00"),
            libro=libro,
            creado_por=self.user,
        )
        Expense.objects.create(
            descripcion="Compra simulada",
            fecha=date(2026, 11, 8),
            descripcion_producto="Mercancía simulada",
            valor_unitario=Decimal("300.00"),
            valor_pagado=Decimal("300.00"),
            cantidad=Decimal("1.00"),
            libro=libro,
            creado_por=self.user,
            es_simulado=True,
        )
        manual = Movimiento.objects.create(
            fecha=date(2026, 11, 8),
            descripcion="Movimiento manual que se conserva",
            ingresos=Decimal("5000.00"),
            egresos=Decimal("0.00"),
            saldo=Decimal("5000.00"),
            libro=libro,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            "/api/entries",
            {"libro_id": libro.id, "year": 2026, "month": 11},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["rows"]), 1)
        self.assertEqual(response.data["rows"][0]["dia"], 8)
        self.assertEqual(response.data["rows"][0]["ingresos"], 100.0)
        self.assertEqual(response.data["rows"][0]["egresos"], 20.0)
        self.assertEqual(response.data["totals"]["ingresos"], 100.0)
        self.assertEqual(response.data["totals"]["egresos"], 20.0)
        self.assertTrue(Movimiento.objects.filter(pk=manual.pk).exists())

        Venta.objects.filter(
            libro=libro,
            fecha__date=date(2026, 11, 8),
            es_simulado=False,
        ).update(total=Decimal("125.00"))
        Expense.objects.filter(libro=libro, fecha=date(2026, 11, 8), es_simulado=False).delete()

        updated_response = self.client.get(
            "/api/entries",
            {"libro_id": libro.id, "year": 2026, "month": 11},
        )
        self.assertEqual(updated_response.data["totals"]["ingresos"], 125.0)
        self.assertEqual(updated_response.data["totals"]["egresos"], 0.0)

    def test_november_0011_manual_entries_remain_read_only(self):
        libro = Libro.objects.create(
            nombre="Libro Folio 0011",
            nit="1010085627-1",
            anio=2026,
            propietario=self.user,
        )
        manual = Movimiento.objects.create(
            fecha=date(2026, 11, 1),
            descripcion="Movimiento manual preservado",
            ingresos=Decimal("10.00"),
            egresos=Decimal("0.00"),
            saldo=Decimal("10.00"),
            libro=libro,
        )
        self.client.force_authenticate(user=self.user)

        create_response = self.client.post(
            "/api/entries",
            {
                "libro_id": libro.id,
                "fecha": "2026-11-02",
                "descripcion": "Movimiento manual",
                "ingresos": "50.00",
                "egresos": "0.00",
            },
            format="json",
        )
        delete_response = self.client.delete(f"/api/entries/{manual.id}")

        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(delete_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Movimiento.objects.filter(pk=manual.pk).exists())


class MovimientosWhiteBoxTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="whitebox@test.com",
            nombre="White Box",
            password="123456",
        )
        self.libro = Libro.objects.create(
            nombre="Caja Blanca",
            nit="9999999",
            anio=2026,
            propietario=self.user,
        )

    def test_build_filters_with_year_and_month(self):
        filters = _build_filters({"year": "2026", "month": "2", "libro_id": "5"})

        self.assertEqual(filters["libro_id"], 5)
        self.assertEqual(filters["fecha__gte"], date(2026, 2, 1))
        self.assertEqual(filters["fecha__lt"], date(2026, 3, 1))

    def test_build_filters_with_year_only(self):
        filters = _build_filters({"year": "2026"})

        self.assertEqual(filters["fecha__gte"], date(2026, 1, 1))
        self.assertEqual(filters["fecha__lt"], date(2027, 1, 1))

    def test_recompute_saldos_applies_accumulated_balance_in_order(self):
        Movimiento.objects.create(
            fecha=date(2026, 1, 2),
            descripcion="Ingreso",
            ingresos=Decimal("100.00"),
            egresos=Decimal("0.00"),
            saldo=Decimal("999.00"),
            libro=self.libro,
        )
        Movimiento.objects.create(
            fecha=date(2026, 1, 3),
            descripcion="Egreso",
            ingresos=Decimal("0.00"),
            egresos=Decimal("40.00"),
            saldo=Decimal("999.00"),
            libro=self.libro,
        )
        Movimiento.objects.create(
            fecha=date(2026, 1, 4),
            descripcion="Ingreso 2",
            ingresos=Decimal("30.00"),
            egresos=Decimal("0.00"),
            saldo=Decimal("999.00"),
            libro=self.libro,
        )

        recompute_saldos(self.libro.id)

        saldos = list(
            Movimiento.objects.filter(libro=self.libro)
            .order_by("fecha", "id")
            .values_list("saldo", flat=True)
        )
        self.assertEqual(saldos, [Decimal("100.00"), Decimal("60.00"), Decimal("90.00")])
