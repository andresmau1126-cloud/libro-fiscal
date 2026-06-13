import json
from django.test import Client, TestCase
from apps.usuarios.models import Usuario


class UsuarioAuthBypassTests(TestCase):
    def setUp(self):
        self.email = 'andresmau1126@gmail.com'
        self.password = 'admin123'
        self.user = Usuario.objects.create_user(
            email=self.email,
            nombre='Andrés Mauricio',
            password=self.password,
            rol='admin',
            is_staff=True,
            is_superuser=True,
            email_verified=False,
        )

    def test_login_bypass_admin_email(self):
        client = Client(HTTP_HOST='localhost')
        response = client.post(
            '/api/auth/login/',
            data=json.dumps({'email': self.email, 'password': self.password}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['message'], 'Login exitoso')
        self.assertEqual(data['user']['email'], self.email)

        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_dashboard_access_after_login(self):
        client = Client(HTTP_HOST='localhost')
        response = client.post(
            '/api/auth/login/',
            data=json.dumps({'email': self.email, 'password': self.password}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

        dashboard_response = client.get('/api/dashboard')
        self.assertEqual(dashboard_response.status_code, 200)
        dashboard_data = dashboard_response.json()
        self.assertIn('total_libros', dashboard_data)
        self.assertIn('total_movimientos', dashboard_data)

    def test_request_otp_bypass_admin_email(self):
        client = Client(HTTP_HOST='localhost')
        response = client.post(
            '/api/auth/request-otp/',
            data=json.dumps({'email': self.email, 'password': self.password}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('Login automático', data['message'])
        self.assertEqual(data['user']['email'], self.email)
