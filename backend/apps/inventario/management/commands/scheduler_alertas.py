"""
Management command para iniciar el scheduler de alertas de inventario.
Uso: python manage.py scheduler_alertas start [--hora 7] [--minuto 0]
     python manage.py scheduler_alertas status
     python manage.py scheduler_alertas stop
"""
from django.core.management.base import BaseCommand, CommandError
from services.scheduler_alertas import (
    iniciar_scheduler,
    detener_scheduler,
    obtener_estado_scheduler,
)
import time


class Command(BaseCommand):
    help = "Gestiona el scheduler de alertas de inventario"

    def add_arguments(self, parser):
        parser.add_argument(
            "accion",
            type=str,
            choices=["start", "status", "stop"],
            help="Acción a ejecutar: start, status o stop",
        )
        parser.add_argument(
            "--hora",
            type=int,
            default=7,
            help="Hora del día para ejecutar alertas (0-23, default: 7 = 7 AM)",
        )
        parser.add_argument(
            "--minuto",
            type=int,
            default=0,
            help="Minuto de la hora (0-59, default: 0)",
        )

    def handle(self, *args, **options):
        accion = options.get("accion")
        
        if accion == "start":
            try:
                hora = options.get("hora")
                minuto = options.get("minuto")
                
                if not (0 <= hora <= 23):
                    raise CommandError(f"Hora inválida: {hora} (debe ser 0-23)")
                if not (0 <= minuto <= 59):
                    raise CommandError(f"Minuto inválido: {minuto} (debe ser 0-59)")
                
                iniciar_scheduler(hora=hora, minuto=minuto)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Scheduler iniciado\n"
                        f"  Alertas programadas para las {hora:02d}:{minuto:02d} diariamente\n"
                        f"  Presiona Ctrl+C para detener"
                    )
                )
                
                # Mantener el process activo
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stdout.write(self.style.WARNING("\n\n⏹  Deteniendo scheduler..."))
                    detener_scheduler()
                    self.stdout.write(self.style.SUCCESS("✓ Scheduler detenido"))
            
            except Exception as e:
                raise CommandError(f"Error al iniciar scheduler: {str(e)}")
        
        elif accion == "status":
            estado = obtener_estado_scheduler()
            
            if estado["activo"]:
                self.stdout.write(self.style.SUCCESS("✓ Scheduler ACTIVO"))
                self.stdout.write(f"  Próximo disparo: {estado['proximo_disparo']}")
            else:
                self.stdout.write(self.style.WARNING("⊗ Scheduler INACTIVO"))
        
        elif accion == "stop":
            try:
                detener_scheduler()
                self.stdout.write(self.style.SUCCESS("✓ Scheduler detenido"))
            except Exception as e:
                raise CommandError(f"Error al detener scheduler: {str(e)}")
