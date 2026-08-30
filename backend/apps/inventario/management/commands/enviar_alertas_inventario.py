"""
Management command para enviar alertas de inventario.
Uso: python manage.py enviar_alertas_inventario [--email EMAIL]
"""
from django.core.management.base import BaseCommand
from services.inventario_alertas import enviar_alerta_inventario
from django.conf import settings


class Command(BaseCommand):
    help = "Envía alertas de inventario (stock bajo y productos próximos a vencer) por email"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default=settings.ALERTA_EMAIL_DESTINO,
            help=f"Email destino (default: {settings.ALERTA_EMAIL_DESTINO})",
        )

    def handle(self, *args, **options):
        email = options.get("email")
        
        self.stdout.write(f"Enviando alerta de inventario a {email}...")
        resultado = enviar_alerta_inventario(destino=email)
        
        if resultado["ok"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {resultado.get('mensaje', 'Alerta enviada')} "
                    f"({resultado['stock_bajo']} stock bajo, "
                    f"{resultado['proximos_vencer']} próximos a vencer)"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"✗ Error: {resultado.get('error', 'Error desconocido')} "
                    f"({resultado.get('stock_bajo', 0)} stock bajo, "
                    f"{resultado.get('proximos_vencer', 0)} próximos a vencer)"
                )
            )
