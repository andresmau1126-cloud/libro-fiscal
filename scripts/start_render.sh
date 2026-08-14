#!/usr/bin/env sh
set -eu

APP_DIR="${APP_DIR:-/app}"
cd "$APP_DIR"

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py crear_usuario_prueba || true
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); print('seed-ready')" >/dev/null 2>&1 || true

exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
