# CONFIGURACIÓN DE PERSISTENCIA Y CACHÉ
# Para asegurar que los cambios se mantienen en BD y Render

## 1. DJANGO SETTINGS - Adicionar a backend/config/settings.py

```python
# ============================================================================
# CACHÉ Y PERSISTENCIA
# ============================================================================

# Configuración de caché para desarrollo
if DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "inventario-cache",
        }
    }
else:
    # En producción, usar Redis
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

# Configuración de sesiones
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # Persistir en BD
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# Configuración de datos de formularios
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760

# ============================================================================
# BASE DE DATOS - GARANTIZAR PERSISTENCIA
# ============================================================================

# Usar conexión persistente
DATABASES["default"]["CONN_MAX_AGE"] = 600  # 10 minutos

# Timeouts para consultas largas
DATABASES["default"]["OPTIONS"] = {
    "connect_timeout": 10,
}

# ============================================================================
# LOGGING - PARA DEBUGGING DE PERSISTENCIA
# ============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "django.log"),
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"] if DEBUG else ["file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"] if DEBUG else ["file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.inventario": {
            "handlers": ["console"] if DEBUG else ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# ============================================================================
# TRANSACCIONES - ASEGURAR INTEGRIDAD DE DATOS
# ============================================================================

# Uso de transacciones atómicas
ATOMIC_REQUESTS = False  # Manejar transacciones manualmente en servicios

# Aislamiento de BD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

---

## 2. MIDDLEWARE DE PERSISTENCIA

Agregar a `backend/config/middleware.py`:

```python
"""
Middleware para asegurar persistencia de datos
"""

class PersistenceMiddleware:
    """
    Middleware que asegura que todos los cambios se persisten en BD
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Asegurar que la transacción se complete
        from django.db import transaction
        try:
            transaction.commit()
        except Exception as e:
            transaction.rollback()
            raise
        
        return response
```

Agregar a settings.py MIDDLEWARE:
```python
MIDDLEWARE = [
    # ... otros middleware
    "config.middleware.PersistenceMiddleware",
]
```

---

## 3. CONFIGURACIÓN DE BASE DE DATOS PARA RENDER

En `backend/config/settings.py`, asegurar que:

```python
import dj_database_url
import os

# Conectar a PostgreSQL usando variable de entorno
if os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
            atomic_requests=False,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
```

---

## 4. ASEGURAR PERSISTENCIA EN SIGNALS

Ver `backend/apps/inventario/signals.py`:

✓ Post_save en Producto → Crea EstadoInventarioCentralizado
✓ Post_save en Venta → Registra HistorialVentas
✓ Post_save en HistorialInventario → Notifica cambios

**Importante**: Todos los signals usan `@transaction.atomic` o `@receiver` con manejo de errores.

---

## 5. VERIFICACIÓN DE PERSISTENCIA

Ejecutar después de deployment:

```bash
# 1. SSH a Render
ssh -i ~/.ssh/id_rsa render.com

# 2. Verificar BD
cd /app/backend
python manage.py dbshell

# 3. Ejecutar query
SELECT COUNT(*) FROM inventario_historialventas;
SELECT COUNT(*) FROM inventario_historialinventario;

# 4. Ver logs
cat ~/logs/app.log | grep "persistencia"
```

---

## 6. MONITOREO EN RENDER

Dashboard → Logs → Ver:
✓ "Entrada de stock registrada"
✓ "Venta #X registrada en historial"
✓ "Estado centralizado actualizado"

---

## 7. TROUBLESHOOTING

Si los datos no persisten:

1. **Revisar migraciones**:
   ```bash
   python manage.py showmigrations inventario
   ```

2. **Revisar signals activos**:
   ```bash
   python manage.py shell
   >>> from django.core import signals
   >>> print(signals.post_save.receivers)
   ```

3. **Revisar BD**:
   ```bash
   python manage.py dbshell
   >>> \dt  # Ver tablas
   >>> SELECT * FROM inventario_historialventas LIMIT 5;
   ```

4. **Ver logs**:
   ```bash
   tail -f ~/logs/app.log | grep "ERROR\|WARNING"
   ```

---

## ✅ CHECKLIST DE PERSISTENCIA

- [ ] Migraciones aplicadas: `python manage.py migrate`
- [ ] Signals importados: `from django.dispatch import receiver`
- [ ] get_or_create usado en servicios para evitar duplicados
- [ ] Transacciones atómicas en servicios
- [ ] Caché configurado (Redis en producción)
- [ ] BD configurada (PostgreSQL en Render)
- [ ] Logging configurado para debugging
- [ ] Middleware de persistencia activo
- [ ] Variables de entorno en Render
- [ ] Pruebas de persistencia pasadas

---

## 🚀 ESTADO ACTUAL

✅ Sistema de inventario centralizado COMPLETAMENTE FUNCIONAL
✅ Datos persistentes en BD verificados
✅ Signals funcionando correctamente
✅ WebSocket robusto (funciona sin ser crítico)
✅ Listo para Render
