"""
Django settings for Libro Fiscal project.
"""
import os
from pathlib import Path
from datetime import timedelta
from email.utils import formataddr
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables del archivo .env si existe
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me-in-production")

DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# ── Aplicaciones ──
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Local apps
    "apps.usuarios",
    "apps.libros",
    "apps.movimientos",
    "apps.auditoria",
    "apps.dashboard",
    "apps.exportacion",
    "apps.inventario",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# ── Frontend build directory ──
# Local dev: ../frontend/dist | Docker/Railway: ../frontend_dist
_FRONTEND_LOCAL = BASE_DIR.parent / "frontend" / "dist"
_FRONTEND_DOCKER = BASE_DIR / "frontend_dist"
FRONTEND_DIR = _FRONTEND_DOCKER if _FRONTEND_DOCKER.exists() else _FRONTEND_LOCAL

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [FRONTEND_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ── Base de datos ──
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600),
    }
else:
    DB_ENGINE = os.getenv("DB_ENGINE", "mysql").strip().lower()

    if DB_ENGINE in ("postgres", "postgresql"):
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.getenv("DB_NAME", "libro_fiscal"),
                "USER": os.getenv("DB_USER", "postgres"),
                "PASSWORD": os.getenv("DB_PASSWORD", "12345"),
                "HOST": os.getenv("DB_HOST", "127.0.0.1"),
                "PORT": os.getenv("DB_PORT", "5432"),
            }
        }
    elif DB_ENGINE == "mysql":
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": os.getenv("DB_NAME", "libro_fiscal"),
                "USER": os.getenv("DB_USER", "root"),
                "PASSWORD": os.getenv("DB_PASSWORD", ""),
                "HOST": os.getenv("DB_HOST", "127.0.0.1"),
                "PORT": os.getenv("DB_PORT", "3306"),
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

# ── Auth ──
AUTH_USER_MODEL = "usuarios.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 6}},
]

# ── REST Framework ──
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.usuarios.authentication.TokenCookieAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "EXCEPTION_HANDLER": "config.exceptions.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": None,
}

# ── Internacionalización ──
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Guatemala"
USE_I18N = True
USE_TZ = True

# ── Static files ──
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [FRONTEND_DIR / "static"] if FRONTEND_DIR.exists() and (FRONTEND_DIR / "static").exists() else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_ROOT = FRONTEND_DIR if FRONTEND_DIR.exists() else None

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── CORS ──
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# ── CSRF trusted origins ──
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://*.ngrok-free.dev,https://*.ngrok.io"
).split(",")

# ── Session token ──
SESSION_TOKEN_EXPIRY_HOURS = int(os.getenv("SESSION_TOKEN_EXPIRY_HOURS", "24"))

# ── Email (Brevo SMTP) ──
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp-relay.brevo.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "").strip()
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "").strip()
if BREVO_SENDER_EMAIL:
    DEFAULT_FROM_EMAIL = formataddr((BREVO_SENDER_NAME, BREVO_SENDER_EMAIL)) if BREVO_SENDER_NAME else BREVO_SENDER_EMAIL
else:
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", os.getenv("EMAIL_HOST_USER", ""))
ALERTA_EMAIL_DESTINO = os.getenv("ALERTA_EMAIL_DESTINO", "maurcio1126@gmail.com")
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")

# ── Security headers (producción) ──
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
