"""
Comando Django: enviar_alertas_correo
Envía alertas de vencimiento e inventario bajo por correo electrónico.

Uso:
    python manage.py enviar_alertas_correo

Variables de entorno necesarias (.env o sistema):
    EMAIL_HOST           → smtp-relay.sendinblue.com (Brevo SMTP)
    EMAIL_PORT           → 587
    EMAIL_HOST_USER      → login SMTP de Brevo
    EMAIL_HOST_PASSWORD  → password SMTP de Brevo
    ALERTA_EMAIL_DESTINO → correo donde llegan las alertas (puede ser el mismo)
"""

import os
from datetime import date

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from apps.inventario.models import Producto


class Command(BaseCommand):
    help = "Envía alertas de vencimiento e inventario bajo por correo electrónico."

    def add_arguments(self, parser):
        parser.add_argument(
            "--destino",
            default=None,
            help="Correo destino. Si no se pasa usa ALERTA_EMAIL_DESTINO del settings.",
        )

    def handle(self, *args, **options):
        destino = options["destino"] or getattr(settings, "ALERTA_EMAIL_DESTINO", "")
        remitente = settings.EMAIL_HOST_USER

        if not remitente or not settings.EMAIL_HOST_PASSWORD:
            self.stderr.write(self.style.ERROR(
                "Faltan EMAIL_HOST_USER o EMAIL_HOST_PASSWORD en las variables de entorno.\n"
                "Configúralas en el archivo .env o en el sistema."
            ))
            return

        if not destino:
            self.stderr.write(self.style.ERROR("No hay correo destino configurado."))
            return

        hoy = date.today()
        productos = Producto.objects.all()

        vencidos = []
        por_vencer = []
        bajo_stock = []

        for p in productos:
            if p.fecha_vencimiento:
                delta = (p.fecha_vencimiento - hoy).days
                if delta < 0:
                    vencidos.append((p, abs(delta)))
                elif delta <= p.dias_alerta:
                    por_vencer.append((p, delta))
            if p.stock_actual <= p.stock_minimo:
                bajo_stock.append(p)

        if not vencidos and not por_vencer and not bajo_stock:
            self.stdout.write(self.style.SUCCESS("Sin alertas pendientes. No se envió correo."))
            return

        # ── Construir mensaje ──
        lineas_html = [
            "<h2 style='color:#333'>📦 Alerta de Inventario — Refrigeración</h2>",
            f"<p><strong>Fecha:</strong> {hoy.strftime('%d/%m/%Y')}</p>",
            "<hr>",
        ]
        lineas_txt = [
            "ALERTA DE INVENTARIO — Refrigeración",
            f"Fecha: {hoy.strftime('%d/%m/%Y')}",
            "",
        ]

        if vencidos:
            lineas_html.append("<h3 style='color:#dc3545'>🔴 Productos VENCIDOS</h3><ul>")
            lineas_txt.append("VENCIDOS:")
            for p, dias in vencidos:
                lineas_html.append(
                    f"<li><strong>{p.nombre}</strong> — venció hace {dias} día(s) "
                    f"({p.fecha_vencimiento})</li>"
                )
                lineas_txt.append(f"  • {p.nombre} — venció hace {dias} día(s) ({p.fecha_vencimiento})")
            lineas_html.append("</ul>")
            lineas_txt.append("")

        if por_vencer:
            lineas_html.append("<h3 style='color:#fd7e14'>🟡 Próximos a VENCER</h3><ul>")
            lineas_txt.append("PRÓXIMOS A VENCER:")
            for p, dias in por_vencer:
                lineas_html.append(
                    f"<li><strong>{p.nombre}</strong> — vence en {dias} día(s) "
                    f"({p.fecha_vencimiento})</li>"
                )
                lineas_txt.append(f"  • {p.nombre} — vence en {dias} día(s) ({p.fecha_vencimiento})")
            lineas_html.append("</ul>")
            lineas_txt.append("")

        if bajo_stock:
            lineas_html.append("<h3 style='color:#6c757d'>🔻 Bajo Stock</h3><ul>")
            lineas_txt.append("BAJO STOCK:")
            for p in bajo_stock:
                lineas_html.append(
                    f"<li><strong>{p.nombre}</strong> — stock actual: {p.stock_actual} "
                    f"(mínimo: {p.stock_minimo})</li>"
                )
                lineas_txt.append(f"  • {p.nombre} — stock: {p.stock_actual} / mínimo: {p.stock_minimo}")
            lineas_html.append("</ul>")

        lineas_html.append("<hr><p style='color:#999;font-size:12px'>Sistema Inventario — MoneyControl</p>")

        asunto = f"⚠️ Alerta Inventario {hoy.strftime('%d/%m/%Y')}"
        cuerpo_txt = "\n".join(lineas_txt)
        cuerpo_html = "\n".join(lineas_html)

        try:
            send_mail(
                subject=asunto,
                message=cuerpo_txt,
                from_email=remitente,
                recipient_list=[destino],
                html_message=cuerpo_html,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Alerta enviada a {destino}"))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"❌ Error al enviar correo: {exc}"))
