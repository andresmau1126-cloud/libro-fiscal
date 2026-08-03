import json
import re
from unittest.mock import patch
from django.core import mail
from django.test import Client, TestCase, override_settings
from apps.usuarios.apps import _seed_default_users
from apps.usuarios.models import Usuario


class UsuarioAuthBypassTests(TestCase):
    def test_seed_default_users_creates_requested_admin(self):
        Usuario.objects.filter(email__iexact='mauricio1126@gmail.com').delete()

        _seed_default_users()

        user = Usuario.objects.get(email__iexact='mauricio1126@gmail.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.rol, 'admin')
        self.assertTrue(user.email_verified)
        self.assertTrue(user.check_password('admin123'))

    def test_seed_default_users_updates_existing_admin_password(self):
        user = Usuario.objects.create_user(
            email='mauricio1126@gmail.com',
            nombre='Viejo',
            password='oldpass123',
            rol='usuario',
            is_staff=False,
            is_superuser=False,
            email_verified=False,
        )

        _seed_default_users()

        user.refresh_from_db()
        self.assertTrue(user.check_password('admin123'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.rol, 'admin')

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

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_register_requires_email_verification(self):
        client = Client(HTTP_HOST='localhost')
        client.cookies.clear()

        response = client.post(
            '/api/auth/register/',
            data=json.dumps({
                'nombre': 'Prueba Usuario',
                'email': 'test@example.com',
                'password': 'secret123',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('Registro exitoso', data['message'])

        self.assertEqual(len(mail.outbox), 1)
        email_message = mail.outbox[0]
        self.assertEqual(email_message.to, ['test@example.com'])
        self.assertIn('Tu código de seguridad es:', email_message.body)

        # Intentar login sin verificar debe fallar
        login_response = client.post(
            '/api/auth/login/',
            data=json.dumps({'email': 'test@example.com', 'password': 'secret123'}),
            content_type='application/json',
        )
        self.assertEqual(login_response.status_code, 401)
        self.assertIn('Cuenta no verificada', login_response.json().get('error', ''))

        # Verificación del código enviado
        email_body = email_message.body
        match = re.search(r"(\d{6})", email_body)
        self.assertIsNotNone(match, "El email debe contener un código de 6 dígitos")
        code = match.group(1)
        verify_response = client.post(
            '/api/auth/verify-registration-code/',
            data=json.dumps({'email': 'test@example.com', 'code': code}),
            content_type='application/json',
        )
        self.assertEqual(verify_response.status_code, 200)
        self.assertIn('Correo verificado', verify_response.json().get('message', ''))

        # Ahora login debe funcionar
        login_response = client.post(
            '/api/auth/login/',
            data=json.dumps({'email': 'test@example.com', 'password': 'secret123'}),
            content_type='application/json',
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json()['user']['email'], 'test@example.com')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('apps.usuarios.views.send_mail', side_effect=Exception('smtp unavailable'))
    def test_register_auto_logs_in_when_security_code_email_fails(self, _mock_send_mail):
        client = Client(HTTP_HOST='localhost')
        client.cookies.clear()

        response = client.post(
            '/api/auth/register/',
            data=json.dumps({
                'nombre': 'Usuario Sin Correo',
                'email': 'sincorreo@example.com',
                'password': 'secret123',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json().get('requires_verification', True))
        self.assertIn('autorizada', response.json()['message'])

        user = Usuario.objects.get(email='sincorreo@example.com')
        self.assertTrue(user.email_verified)
        self.assertEqual(user.email_verification_code, '')
        self.assertTrue(response.cookies.get('session_token'))
