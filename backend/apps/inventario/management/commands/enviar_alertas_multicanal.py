"""
Comando Django: enviar_alertas_multicanal
Ejecuta las alertas por correo y WhatsApp en una sola corrida.

Uso:
    python manage.py enviar_alertas_multicanal

Opciones:
    --destino correo@dominio.com
    --phone 573001112233
    --apikey TU_APIKEY
    --force-whatsapp
"""

from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Envía alertas por correo y WhatsApp en una sola ejecución."

    def add_arguments(self, parser):
        parser.add_argument(
            "--destino",
            default=None,
            help="Correo destino para enviar_alertas_correo.",
        )
        parser.add_argument(
            "--phone",
            default=None,
            help="Numero WhatsApp con codigo de pais, ej: 573001112233.",
        )
        parser.add_argument(
            "--apikey",
            default=None,
            help="API key de CallMeBot para WhatsApp.",
        )
        parser.add_argument(
            "--force-whatsapp",
            action="store_true",
            help="Fuerza envio WhatsApp aunque ENABLE_WHATSAPP_ALERTAS sea false.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando alertas multicanal..."))

        correo_kwargs = {}
        if options.get("destino"):
            correo_kwargs["destino"] = options["destino"]

        whatsapp_kwargs = {}
        if options.get("phone"):
            whatsapp_kwargs["phone"] = options["phone"]
        if options.get("apikey"):
            whatsapp_kwargs["apikey"] = options["apikey"]
        if options.get("force_whatsapp"):
            whatsapp_kwargs["force"] = True

        errores = []

        try:
            self.stdout.write("\n[1/2] Enviando alertas por correo...")
            call_command("enviar_alertas_correo", **correo_kwargs)
        except Exception as exc:
            errores.append(f"Correo: {exc}")

        try:
            self.stdout.write("\n[2/2] Enviando alertas por WhatsApp...")
            call_command("enviar_alertas_whatsapp", **whatsapp_kwargs)
        except Exception as exc:
            errores.append(f"WhatsApp: {exc}")

        if errores:
            self.stderr.write(self.style.ERROR("\nFinalizo con errores:"))
            for err in errores:
                self.stderr.write(f" - {err}")
            return

        self.stdout.write(self.style.SUCCESS("\nOK: Alertas enviadas por todos los canales disponibles."))
