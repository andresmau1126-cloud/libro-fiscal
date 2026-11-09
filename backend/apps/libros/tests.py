from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from apps.libros.models import Libro
from apps.movimientos.models import Movimiento
from apps.usuarios.models import Usuario


class FiscalBooksRolePermissionsTests(APITestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            email="admin.libros@test.com",
            nombre="Admin",
            password="test-password",
            rol="admin",
        )
        self.manager = Usuario.objects.create_user(
            email="manager.libros@test.com",
            nombre="Gerente",
            password="test-password",
            rol="gerente",
        )
        self.auditor = Usuario.objects.create_user(
            email="auditor.libros@test.com",
            nombre="Auditor",
            password="test-password",
            rol="auditor",
        )
        self.supervisors = (self.admin, self.manager, self.auditor)
        self.libro = Libro.objects.create(
            nombre="Libro fiscal",
            nit="1010085627-1",
            anio=date.today().year,
            propietario=self.admin,
        )

    def test_supervisors_can_list_and_read_books_owned_by_other_users(self):
        for user in self.supervisors:
            with self.subTest(role=user.rol):
                self.client.force_authenticate(user=user)
                response = self.client.get("/api/libros")
                detail = self.client.get(f"/api/libros/{self.libro.id}")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual([book["id"] for book in response.data], [self.libro.id])
                self.assertEqual(detail.status_code, status.HTTP_200_OK)

    def test_supervisors_can_create_and_update_books(self):
        for user in self.supervisors:
            with self.subTest(role=user.rol):
                self.client.force_authenticate(user=user)
                create_response = self.client.post(
                    "/api/libros",
                    {
                        "nombre": f"Libro de {user.rol}",
                        "nit": f"NIT-{user.id}",
                        "anio": date.today().year,
                    },
                    format="json",
                )
                update_response = self.client.put(
                    f"/api/libros/{self.libro.id}",
                    {
                        "nombre": f"Libro actualizado por {user.rol}",
                        "nit": "1010085627-1",
                        "anio": date.today().year,
                    },
                    format="json",
                )

                self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(update_response.status_code, status.HTTP_200_OK)
                self.assertEqual(update_response.data["nombre"], f"Libro actualizado por {user.rol}")

    def test_supervisors_can_create_and_update_entries(self):
        for user in self.supervisors:
            with self.subTest(role=user.rol):
                self.client.force_authenticate(user=user)
                list_response = self.client.get(
                    "/api/entries",
                    {"libro_id": self.libro.id, "year": self.libro.anio, "month": date.today().month},
                )
                create_response = self.client.post(
                    "/api/entries",
                    {
                        "libro_id": self.libro.id,
                        "fecha": date.today().isoformat(),
                        "descripcion": f"Movimiento de {user.rol}",
                        "ingresos": "100.00",
                        "egresos": "0.00",
                    },
                    format="json",
                )
                entry_id = create_response.data["id"]
                update_response = self.client.put(
                    f"/api/entries/{entry_id}",
                    {
                        "fecha": date.today().isoformat(),
                        "descripcion": f"Movimiento actualizado por {user.rol}",
                        "ingresos": "150.00",
                        "egresos": "0.00",
                    },
                    format="json",
                )

                self.assertEqual(list_response.status_code, status.HTTP_200_OK)
                self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(update_response.status_code, status.HTTP_200_OK)
                self.assertEqual(update_response.data["descripcion"], f"Movimiento actualizado por {user.rol}")

    def test_supervisors_can_see_and_edit_the_same_admin_owned_entry(self):
        entry = Movimiento.objects.create(
            fecha=date.today(),
            descripcion="Movimiento",
            ingresos=100,
            egresos=0,
            saldo=100,
            libro=self.libro,
        )

        for user in self.supervisors:
            with self.subTest(role=user.rol):
                self.client.force_authenticate(user=user)
                response = self.client.get(
                    "/api/entries",
                    {"libro_id": self.libro.id, "year": self.libro.anio, "month": date.today().month},
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn(entry.id, [row["id"] for row in response.data["rows"]])

                update_response = self.client.put(
                    f"/api/entries/{entry.id}",
                    {
                        "fecha": date.today().isoformat(),
                        "descripcion": f"Editado por {user.rol}",
                        "ingresos": "200.00",
                        "egresos": "0.00",
                    },
                    format="json",
                )
                self.assertEqual(update_response.status_code, status.HTTP_200_OK)
                self.assertEqual(update_response.data["descripcion"], f"Editado por {user.rol}")

    def test_only_admin_can_delete_entries(self):
        for user in self.supervisors:
            with self.subTest(role=user.rol):
                entry = Movimiento.objects.create(
                    fecha=date.today(),
                    descripcion="Movimiento",
                    ingresos=100,
                    egresos=0,
                    saldo=100,
                    libro=self.libro,
                )
                self.client.force_authenticate(user=user)

                response = self.client.delete(f"/api/entries/{entry.id}")

                if user == self.admin:
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertFalse(Movimiento.objects.filter(pk=entry.id).exists())
                else:
                    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                    self.assertTrue(Movimiento.objects.filter(pk=entry.id).exists())
