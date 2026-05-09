from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

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
        self.client.force_authenticate(user=self.user)
        payload = {
            "fecha": "2026-01-10",
            "descripcion": "Intento ajeno",
            "ingresos": "15.00",
            "egresos": "0.00",
            "libro_id": self.other_libro.id,
        }

        response = self.client.post("/api/entries", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


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
