import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import PuntoControl, RegistroRestauracion

User = get_user_model()


class PuntoControlTestCase(TestCase):
    """Pruebas unitarias para el modelo PuntoControl"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.usuario = User.objects.create_user(
            email='test@example.com',
            nombre='Test User',
            password='testpass123'
        )
    
    def test_crear_punto_control(self):
        """Prueba la creación de un punto de control"""
        punto = PuntoControl.objects.create(
            nombre='Prueba Respaldo',
            descripcion='Respaldo de prueba',
            tipo='completo',
            usuario_creador=self.usuario
        )
        self.assertEqual(punto.nombre, 'Prueba Respaldo')
        self.assertEqual(punto.tipo, 'completo')
        self.assertEqual(punto.estado, 'en_proceso')
    
    def test_marcar_completado(self):
        """Prueba marcar un respaldo como completado"""
        punto = PuntoControl.objects.create(
            nombre='Prueba Respaldo',
            usuario_creador=self.usuario
        )
        punto.marcar_completado(1024000)
        punto.refresh_from_db()
        
        self.assertEqual(punto.estado, 'completado')
        self.assertEqual(punto.tamano_archivo, 1024000)

    def test_crear_respaldo_acepta_json(self):
        """El endpoint debe aceptar JSON al crear un respaldo."""
        self.client.force_login(self.usuario)

        payload = {
            'nombre': 'Respaldo JSON',
            'descripcion': 'Prueba con JSON',
            'tipo': 'completo',
        }

        response = self.client.post(
            '/api/respaldos/crear_respaldo/',
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201, response.content.decode())
        self.assertTrue(PuntoControl.objects.filter(nombre='Respaldo JSON').exists())
