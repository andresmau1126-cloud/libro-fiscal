from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.inventario"
    
    def ready(self):
        """Se ejecuta cuando la aplicación está lista."""
        import apps.inventario.signals  # noqa
