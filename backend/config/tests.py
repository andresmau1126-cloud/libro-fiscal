import importlib
import os
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings


class RenderDeploymentConfigTests(SimpleTestCase):
    def test_render_yaml_uses_connection_string_for_database_url(self) -> None:
        render_yaml_path = Path(__file__).resolve().parents[2] / "render.yaml"
        content = render_yaml_path.read_text(encoding="utf-8")

        self.assertIn("property: connectionString", content)
        self.assertIn("healthCheckPath: /healthz/", content)
        self.assertIn("generateValue: true", content)
        self.assertNotIn("RENDER_SECRET_KEY", content)
        self.assertNotIn("-p 10000", content)

    def test_database_url_takes_precedence_over_sqlite_when_debug_is_enabled(self) -> None:
        from config import settings as settings_module

        with patch.dict(os.environ, {"DEBUG": "true", "DATABASE_URL": "postgres://user:pass@localhost:5432/libro_fiscal"}, clear=False):
            reloaded_settings = importlib.reload(settings_module)

        self.assertEqual(reloaded_settings.DATABASES["default"]["ENGINE"], "django.db.backends.postgresql")

    def test_production_rejects_sqlite_database_url(self) -> None:
        from config import settings as settings_module

        with patch.dict(
            os.environ,
            {"DEBUG": "false", "DATABASE_URL": "sqlite:////tmp/render.sqlite3"},
            clear=False,
        ):
            with self.assertRaises(ImproperlyConfigured) as context:
                importlib.reload(settings_module)

        self.assertIn("persistent PostgreSQL database", str(context.exception))

    def test_render_production_allows_onrender_cookies_and_cors(self) -> None:
        from config import settings as settings_module

        with patch.dict(
            os.environ,
            {
                "DEBUG": "true",
                "DATABASE_URL": "postgresql://localhost:5432/libro_fiscal",
                "RENDER_EXTERNAL_HOSTNAME": "libro-fiscal.onrender.com",
                "CORS_ALLOWED_ORIGINS": "https://frontend.onrender.com",
                "CSRF_TRUSTED_ORIGINS": "https://frontend.onrender.com",
            },
            clear=False,
        ):
            reloaded_settings = importlib.reload(settings_module)

        self.assertFalse(reloaded_settings.DEBUG)
        self.assertIn("https://frontend.onrender.com", reloaded_settings.CORS_ALLOWED_ORIGINS)
        self.assertIn("https://libro-fiscal.onrender.com", reloaded_settings.CORS_ALLOWED_ORIGINS)
        self.assertIn("https://libro-fiscal.onrender.com", reloaded_settings.CSRF_TRUSTED_ORIGINS)
        self.assertEqual(reloaded_settings.SESSION_COOKIE_SAMESITE, "None")
        self.assertTrue(reloaded_settings.SESSION_COOKIE_SECURE)
        self.assertTrue(reloaded_settings.SECURE_SSL_REDIRECT)
        self.assertEqual(reloaded_settings.SECURE_HSTS_SECONDS, 31536000)
        self.assertTrue(reloaded_settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)

    @patch("config.urls.connection")
    def test_health_check_verifies_database_connection(self, mock_connection):
        response = self.client.get("/healthz/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})
        mock_connection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with(
            "SELECT 1"
        )

    @patch("config.urls.connection")
    def test_health_check_fails_when_database_is_unavailable(self, mock_connection):
        mock_connection.cursor.side_effect = DatabaseError("database unavailable")
        response = self.client.get("/healthz/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "unavailable", "database": "unavailable"},
        )

    @override_settings(
        DEBUG=False,
        SECURE_HSTS_SECONDS=31536000,
        SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
        SECURE_SSL_REDIRECT=False,
    )
    def test_production_hsts_is_set_when_tls_terminates_at_proxy(self):
        from config.middleware import ProductionHstsMiddleware

        request = RequestFactory().get("/healthz/")
        middleware = ProductionHstsMiddleware(lambda _request: HttpResponse())
        response = middleware(request)

        self.assertEqual(
            response["Strict-Transport-Security"],
            "max-age=31536000; includeSubDomains",
        )
