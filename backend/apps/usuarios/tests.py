import json
import re
from unittest.mock import patch
from django.core import mail
from django.test import Client, TestCase, override_settings
from apps.usuarios.apps import _seed_default_users
from apps.usuarios.models import Usuario, SellerSchedule


class UsuarioAuthBypassTests(TestCase):
    def test_seed_default_users_creates_requested_admin(self):
        Usuario.objects.filter(email__iexact='mauricio1126@gmail.com').delete()

        _seed_default_users()

        user = Usuario.objects.get(email__iexact='mauricio1126@gmail.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.rol, 'gerente')
        self.assertTrue(user.email_verified)
        self.assertTrue(user.check_password('admin123'))

    def test_seed_default_users_repairs_protected_role_and_password(self):
        user = Usuario.objects.create_user(
            email='mauricio1126@gmail.com',
            nombre='Viejo',
            password='oldpass123',
            rol='gerente',
            is_staff=False,
            is_superuser=False,
            email_verified=False,
        )

        _seed_default_users()

        user.refresh_from_db()
        self.assertTrue(user.check_password('admin123'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.rol, 'gerente')

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

    @override_settings(BYPASS_EMAIL_VERIFICATION='andresmau1126@gmail.com')
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

    @override_settings(BYPASS_EMAIL_VERIFICATION='')
    def test_register_does_not_auto_verify_without_explicit_bypass(self):
        client = Client(HTTP_HOST='localhost')
        client.cookies.clear()

        response = client.post(
            '/api/auth/register/',
            data=json.dumps({
                'nombre': 'Usuario Normal',
                'email': 'nuevo-sin-bypass@example.com',
                'password': 'secret123',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json().get('requires_verification', False))

        user = Usuario.objects.get(email='nuevo-sin-bypass@example.com')
        self.assertFalse(user.email_verified)
        self.assertNotEqual(user.email_verification_code, '')

    def test_seed_default_users_repairs_protected_role(self):
        user = Usuario.objects.get(email__iexact='andresmau1126@gmail.com')
        user.rol = 'gerente'
        user.save(update_fields=['rol'])

        _seed_default_users()

        user.refresh_from_db()
        self.assertEqual(user.rol, 'admin')

    @override_settings(BYPASS_EMAIL_VERIFICATION='andresmau1126@gmail.com')
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

    @override_settings(BYPASS_EMAIL_VERIFICATION='andresmau1126@gmail.com')
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
    def test_register_requires_verification_when_security_code_email_fails(self, _mock_send_mail):
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

        self.assertEqual(response.status_code, 503)
        self.assertIn('No se pudo enviar el código de seguridad', response.json()['error'])

        self.assertTrue(Usuario.objects.filter(email='sincorreo@example.com').exists())
        self.assertFalse(response.cookies.get('session_token'))

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        EMAIL_HOST_USER='',
        EMAIL_HOST_PASSWORD='',
        BYPASS_EMAIL_VERIFICATION='',
    )
    def test_register_requires_verification_when_email_credentials_are_missing(self):
        client = Client(HTTP_HOST='localhost')
        client.cookies.clear()

        response = client.post(
            '/api/auth/register/',
            data=json.dumps({
                'nombre': 'Usuario Sin SMTP',
                'email': 'sinsmtp@example.com',
                'password': 'secret123',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 503)
        self.assertIn('No se pudo enviar el código de seguridad', response.json()['error'])

        self.assertTrue(Usuario.objects.filter(email='sinsmtp@example.com').exists())
        self.assertFalse(response.cookies.get('session_token'))


class SellerScheduleTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            email='admin.schedule@test.com',
            nombre='Admin Turno',
            password='admin123',
            rol='admin',
            is_staff=True,
            is_superuser=True,
            email_verified=True,
        )
        self.seller = Usuario.objects.create_user(
            email='vendedor.turno@test.com',
            nombre='Vendedor Turno',
            password='admin123',
            rol='vendedor',
            email_verified=True,
        )

    def test_seller_shift_helper_blocks_outside_window(self):
        from datetime import time

        schedule = SellerSchedule.objects.create(
            usuario=self.seller,
            name='vendedor.turno@test.com',
            start_time='08:00:00',
            end_time='12:00:00',
            is_active=True,
        )

        self.assertTrue(schedule.contains(time(9, 0)))
        self.assertFalse(schedule.contains(time(13, 0)))
        self.assertTrue(self.seller_is_in_shift(time(10, 0)))
        self.assertFalse(self.seller_is_in_shift(time(13, 0)))

    def test_open_turn_allows_seller_without_schedule(self):
        from apps.turnos.models import Turno
        from apps.usuarios.utils import get_shift_error_for_user
        from django.utils import timezone

        Turno.objects.create(
            vendedor=self.seller,
            fecha=timezone.localdate(),
            estado="abierto",
        )

        self.assertIsNone(get_shift_error_for_user(self.seller))

    def test_admin_can_list_and_update_schedules(self):
        schedule = SellerSchedule.objects.create(
            usuario=self.seller,
            name='vendedor.turno@test.com',
            start_time='08:00:00',
            end_time='12:00:00',
            is_active=True,
        )

        from apps.usuarios.authentication import create_session

        token = create_session(self.admin, ip='127.0.0.1', user_agent='test-agent')
        self.client.cookies['session_token'] = token

        response = self.client.get('/api/schedules')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)

        update = self.client.put(
            f'/api/schedules/{schedule.id}',
            data=json.dumps({'start_time': '09:00:00', 'end_time': '13:00:00'}),
            content_type='application/json',
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.json()['start_time'], '09:00:00')

    def seller_is_in_shift(self, current_time):
        from apps.usuarios.utils import user_is_in_shift

        return user_is_in_shift(self.seller, current_time)
