"""
Comando Django: enviar_alertas_whatsapp
Envía alertas por WhatsApp (via CallMeBot) de productos vencidos o próximos a vencer.

Uso:
    python manage.py enviar_alertas_whatsapp

Configuración en variables de entorno (o .env):
    WHATSAPP_PHONE   → número con código de país, sin + ni espacios, ej: 573194233482
    WHATSAPP_APIKEY  → clave que CallMeBot te envía al registrarte

Cómo registrarse en CallMeBot (solo una vez):
    1. Agrega el contacto +34 644 85 00 48 en WhatsApp.
    2. Envíale el mensaje: I allow callmebot to send me messages
    3. Recibirás tu apikey en respuesta.
"""

import os
import urllib.parse
import urllib.request
from datetime import date

from django.core.management.base import BaseCommand

from apps.inventario.models import Producto


CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"


def _enviar_whatsapp(phone: str, apikey: str, texto: str) -> bool:
    params = urllib.parse.urlencode({
        "phone": phone,
        "text": texto,
        "apikey": apikey,
    })
    url = f"{CALLMEBOT_URL}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return resp.status == 200
    except Exception as exc:
        print(f"    Error al enviar WhatsApp: {exc}")
        return False


class Command(BaseCommand):
    help = "Envía alertas de vencimiento e inventario bajo por WhatsApp via CallMeBot."

    def add_arguments(self, parser):
        parser.add_argument(
            "--phone",
            default=None,
            help="Número WhatsApp con código de país (ej: 573194233482). "
                 "Si no se pasa, usa la variable WHATSAPP_PHONE.",
        )
        parser.add_argument(
            "--apikey",
            default=None,
            help="API key de CallMeBot. Si no se pasa, usa WHATSAPP_APIKEY.",
        )

    def handle(self, *args, **options):
        phone = options["phone"] or os.getenv("WHATSAPP_PHONE", "")
        apikey = options["apikey"] or os.getenv("WHATSAPP_APIKEY", "")

        if not phone or not apikey:
            self.stderr.write(
                self.style.ERROR(
                    "Falta WHATSAPP_PHONE o WHATSAPP_APIKEY. "
                    "Defínelos como variables de entorno o pásalos con --phone y --apikey."
                )
            )
            return

        hoy = date.today()
        productos = Producto.objects.exclude(fecha_vencimiento=None)

        vencidos = []
        por_vencer = []

        for p in productos:
            delta = (p.fecha_vencimiento - hoy).days
            if delta < 0:
                vencidos.append(p)
            elif delta <= p.dias_alerta:
                por_vencer.append(p)

        # También productos con bajo stock
        bajo_stock = list(
            Producto.objects.filter(stock_actual__lte=0) |
            Producto.objects.extra(where=["stock_actual <= stock_minimo"])
        )

        if not vencidos and not por_vencer and not bajo_stock:
            self.stdout.write(self.style.SUCCESS("Sin alertas pendientes."))
            return

        lineas = ["📦 *Alerta Inventario Refrigeracion*", f"📅 {hoy.strftime('%d/%m/%Y')}", ""]

        if vencidos:
            lineas.append("🔴 *VENCIDOS:*")
            for p in vencidos:
                dias = abs((p.fecha_vencimiento - hoy).days)
                lineas.append(f"  • {p.nombre} — venció hace {dias} día(s) ({p.fecha_vencimiento})")
            lineas.append("")

        if por_vencer:
            lineas.append("🟡 *PRÓXIMOS A VENCER:*")
            for p in por_vencer:
                dias = (p.fecha_vencimiento - hoy).days
                lineas.append(f"  • {p.nombre} — vence en {dias} día(s) ({p.fecha_vencimiento})")
            lineas.append("")

        if bajo_stock:
            lineas.append("🔻 *BAJO STOCK:*")
            for p in bajo_stock:
                lineas.append(f"  • {p.nombre} — stock: {p.stock_actual}")
            lineas.append("")

        mensaje = "\n".join(lineas)

        self.stdout.write(f"Enviando alerta a {phone}...")
        ok = _enviar_whatsapp(phone, apikey, mensaje)

        if ok:
            self.stdout.write(self.style.SUCCESS("✅ Alerta enviada por WhatsApp."))
        else:
            self.stderr.write(self.style.ERROR("❌ No se pudo enviar el mensaje."))
