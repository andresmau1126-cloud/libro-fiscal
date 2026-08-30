# 📅 Scheduler de Alertas de Inventario

Sistema automático para enviar alertas de inventario diariamente a `andresmau1126@gmail.com`.

## 🚀 Inicio Rápido

### Opción 1: Desde la API (Recomendado para producción)

**Iniciar scheduler** - POST a las 7:00 AM:
```bash
curl -X POST http://localhost:8000/api/inventario/scheduler/start \
  -H "Content-Type: application/json" \
  -d '{"hora": 7, "minuto": 0}'
```

**Verificar estado**:
```bash
curl http://localhost:8000/api/inventario/scheduler/status
```

Respuesta:
```json
{
  "ok": true,
  "estado": {
    "activo": true,
    "proximo_disparo": "2026-08-29T07:00:00",
    "timestamp": "2026-08-28T15:30:00.123456"
  }
}
```

**Detener scheduler**:
```bash
curl -X POST http://localhost:8000/api/inventario/scheduler/stop
```

---

### Opción 2: Desde el comando Django

**Iniciar scheduler** a las 7:00 AM (ejecutar en background):
```bash
python manage.py scheduler_alertas start --hora 7 --minuto 0
```

Para detener, presiona `Ctrl+C`.

**Ver estado**:
```bash
python manage.py scheduler_alertas status
```

**Detener** (desde otra terminal):
```bash
python manage.py scheduler_alertas stop
```

---

### Opción 3: Disparo Manual (Sin scheduler)

Ejecuta alertas ahora sin programación:
```bash
python manage.py enviar_alertas_inventario --email andresmau1126@gmail.com
```

O vía API:
```bash
curl http://localhost:8000/api/inventario/alertas-inventario?email=andresmau1126@gmail.com
```

---

## ⚙️ Configuración

### Cambiar hora de disparo

Edita `backend/config/settings.py`:
```python
# Default: 7 AM
ALERTAS_INVENTARIO_HORA = int(os.getenv("ALERTAS_INVENTARIO_HORA", "7"))
ALERTAS_INVENTARIO_MINUTO = int(os.getenv("ALERTAS_INVENTARIO_MINUTO", "0"))
```

O usa variables de entorno:
```bash
export ALERTAS_INVENTARIO_HORA=14  # 2 PM
export ALERTAS_INVENTARIO_MINUTO=30
```

### Cambiar correo destino

Edita `backend/config/settings.py`:
```python
ALERTA_EMAIL_DESTINO = os.getenv("ALERTA_EMAIL_DESTINO", "andresmau1126@gmail.com")
```

---

## 🔄 Automatización en Producción

### En Linux/Mac (usando systemd)

Crea archivo `/etc/systemd/system/django-alertas.service`:
```ini
[Unit]
Description=Django Inventory Alerts Scheduler
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
ExecStart=/path/to/venv/bin/python manage.py scheduler_alertas start --hora 7 --minuto 0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Habilita e inicia:
```bash
sudo systemctl daemon-reload
sudo systemctl enable django-alertas
sudo systemctl start django-alertas
```

---

### En Windows (usando Task Scheduler)

1. Abre **Task Scheduler** (`taskschd.msc`)
2. Crea una **nueva tarea**:
   - **Nombre**: Django Alertas de Inventario
   - **Descripción**: Envía alertas de inventario automáticamente
   - **Ejecutar con máximos privilegios**: ✓

3. **Trigger** (Disparador):
   - Tipo: Diaria
   - Hora: 07:00:00
   - Repetición: Diaria

4. **Acción** (Action):
   - Programa: `C:\Users\MAURICIO\.venv\Scripts\python.exe`
   - Argumentos: `backend/manage.py enviar_alertas_inventario`
   - Inicio en: `C:\Users\MAURICIO\Desktop\libro fiscal\libro fiscal\libro_fiscal_v2`

5. Guarda y prueba

---

### En Docker/Railway/Render

Ejecuta en background:
```dockerfile
# Dockerfile
CMD ["sh", "-c", "python manage.py scheduler_alertas start --hora 7 --minuto 0 & gunicorn config.wsgi:application"]
```

O usa dos procesos en `Procfile`:
```
web: gunicorn config.wsgi:application
scheduler: python manage.py scheduler_alertas start --hora 7 --minuto 0
```

---

## 📊 Monitoreo

### Logs

Los logs se escriben en el nivel `INFO`:
```bash
# Ver logs del scheduler
tail -f /var/log/django-alertas.log
```

Configurar logging en `backend/config/settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django-alertas.log',
        },
    },
    'loggers': {
        'services.scheduler_alertas': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### Verificación de envíos

Revisa el bandeja de entrada de **andresmau1126@gmail.com** cada día a las 7:00 AM (o la hora configurada).

Contenido del email:
- 📦 Productos con **stock bajo**
- 📅 Productos **próximos a vencer**
- ⏰ Timestamp de generación

---

## 🆘 Troubleshooting

### "Scheduler ya está en ejecución"
Solo puede haber una instancia. Detén primero:
```bash
python manage.py scheduler_alertas stop
```

### "Faltan variables EMAIL_HOST_USER o EMAIL_HOST_PASSWORD"
Verifica las variables de entorno:
```bash
echo $EMAIL_HOST_USER
echo $EMAIL_HOST_PASSWORD
```

### No se envían alertas a pesar de estar programadas
1. Verifica el estado: `curl http://localhost:8000/api/inventario/scheduler/status`
2. Revisa logs de Django
3. Intenta un envío manual: `curl http://localhost:8000/api/inventario/alertas-inventario`

---

## 📝 Código de referencia

- Servicio: `backend/services/inventario_alertas.py`
- Scheduler: `backend/services/scheduler_alertas.py`
- Management command: `backend/apps/inventario/management/commands/scheduler_alertas.py`
- Endpoints API: `backend/apps/inventario/views.py` (`scheduler_alertas_*`)
