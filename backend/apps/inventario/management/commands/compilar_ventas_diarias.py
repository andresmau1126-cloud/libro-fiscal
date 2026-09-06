from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from services.ventas_libro import LIBRO_VENTAS_VENDEDORES_NIT, compilar_ventas_diarias


class Command(BaseCommand):
    help = "Consolida las ventas de un día en los libros fiscales."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fecha",
            help="Fecha a compilar en formato YYYY-MM-DD. Por defecto, el día anterior.",
        )
        parser.add_argument(
            "--nit",
            default=LIBRO_VENTAS_VENDEDORES_NIT,
            help="NIT cuyo ingreso se sincroniza. Por defecto, el libro de Andrés.",
        )

    def handle(self, *args, **options):
        fecha = timezone.localdate() - timedelta(days=1)
        if options["fecha"]:
            try:
                fecha = datetime.strptime(options["fecha"], "%Y-%m-%d").date()
            except ValueError as error:
                raise CommandError("--fecha debe tener el formato YYYY-MM-DD.") from error

        cantidad = compilar_ventas_diarias(fecha, options["nit"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Ventas del {fecha.isoformat()} compiladas en {cantidad} libro(s) fiscal(es)."
            )
        )