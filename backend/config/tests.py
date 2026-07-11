from pathlib import Path

from django.test import SimpleTestCase


class RenderDeploymentConfigTests(SimpleTestCase):
    def test_render_yaml_uses_connection_string_for_database_url(self) -> None:
        render_yaml_path = Path(__file__).resolve().parents[2] / "render.yaml"
        content = render_yaml_path.read_text(encoding="utf-8")

        self.assertIn("property: connectionString", content)
