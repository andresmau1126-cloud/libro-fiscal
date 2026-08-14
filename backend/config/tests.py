import importlib
import os
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase


class RenderDeploymentConfigTests(SimpleTestCase):
    def test_render_yaml_uses_connection_string_for_database_url(self) -> None:
        render_yaml_path = Path(__file__).resolve().parents[2] / "render.yaml"
        content = render_yaml_path.read_text(encoding="utf-8")

        self.assertIn("property: connectionString", content)

    def test_database_url_takes_precedence_over_sqlite_when_debug_is_enabled(self) -> None:
        from config import settings as settings_module

        with patch.dict(os.environ, {"DEBUG": "true", "DATABASE_URL": "postgres://user:pass@localhost:5432/libro_fiscal"}, clear=False):
            reloaded_settings = importlib.reload(settings_module)

        self.assertEqual(reloaded_settings.DATABASES["default"]["ENGINE"], "django.db.backends.postgresql")
