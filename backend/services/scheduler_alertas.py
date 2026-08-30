"""
Scheduler para ejecutar alertas de inventario automáticamente.
Usa APScheduler para programar tareas periódicas.
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from services.inventario_alertas import enviar_alerta_inventario

logger = logging.getLogger(__name__)

# Variable global para el scheduler
_scheduler = None


def _enviar_alerta_programada():
    """Función que ejecuta el envío de alertas de forma programada."""
    try:
        resultado = enviar_alerta_inventario()
        if resultado["ok"]:
            logger.info(
                f"✓ Alerta de inventario enviada exitosamente. "
                f"Stock bajo: {resultado['stock_bajo']}, "
                f"Próximos vencer: {resultado['proximos_vencer']}"
            )
        else:
            logger.error(f"✗ Error al enviar alerta: {resultado.get('error', 'Error desconocido')}")
    except Exception as e:
        logger.error(f"✗ Excepción en envío programado de alertas: {str(e)}", exc_info=True)


def iniciar_scheduler(hora=7, minuto=0):
    """
    Inicia el scheduler de alertas de inventario.
    
    Args:
        hora: Hora del día para ejecutar (0-23, default: 7 = 7 AM)
        minuto: Minuto de la hora (0-59, default: 0)
    
    Returns:
        BackgroundScheduler: La instancia del scheduler
    """
    global _scheduler
    
    if _scheduler is not None and _scheduler.running:
        logger.warning("El scheduler ya está en ejecución")
        return _scheduler
    
    try:
        _scheduler = BackgroundScheduler()
        
        # Programar la tarea para ejecutarse diariamente a la hora especificada
        _scheduler.add_job(
            _enviar_alerta_programada,
            "cron",
            hour=hora,
            minute=minuto,
            id="alertas_inventario_diarias",
            name="Alertas de Inventario Diarias",
            replace_existing=True,
        )
        
        _scheduler.start()
        logger.info(
            f"✓ Scheduler iniciado. Alertas programadas para las {hora:02d}:{minuto:02d} diariamente"
        )
        return _scheduler
    
    except Exception as e:
        logger.error(f"✗ Error al iniciar scheduler: {str(e)}", exc_info=True)
        raise


def detener_scheduler():
    """Detiene el scheduler de alertas."""
    global _scheduler
    
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("✓ Scheduler detenido")
    else:
        logger.warning("El scheduler no está en ejecución")


def obtener_proximo_disparo():
    """Retorna la fecha/hora del próximo disparo programado."""
    global _scheduler
    
    if _scheduler is None or not _scheduler.running:
        return None
    
    jobs = _scheduler.get_jobs()
    if jobs:
        return jobs[0].next_run_time
    
    return None


def obtener_estado_scheduler():
    """Retorna información sobre el estado del scheduler."""
    global _scheduler
    
    return {
        "activo": _scheduler is not None and _scheduler.running,
        "proximo_disparo": obtener_proximo_disparo(),
        "timestamp": datetime.now().isoformat(),
    }
