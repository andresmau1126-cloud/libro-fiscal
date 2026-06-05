#!/usr/bin/env bash
set -e

echo "=== Render sanity check ==="
echo "PWD: $(pwd)"
echo "USER: $(whoami)"

echo "\n--- Python / Django ---"
if command -v python >/dev/null 2>&1; then
  python --version
else
  echo "python no está disponible"
fi

echo "\n--- Environment variables ---"
for key in DEBUG ALLOWED_HOSTS CSRF_TRUSTED_ORIGINS DATABASE_URL DB_ENGINE DB_NAME DB_USER DB_HOST DB_PORT EMAIL_HOST EMAIL_PORT EMAIL_HOST_USER DEFAULT_FROM_EMAIL DJANGO_SETTINGS_MODULE; do
  value="$(printenv "$key" 2>/dev/null)"
  if [[ -z "$value" ]]; then
    echo "$key: <not set>"
  else
    echo "$key: set"
  fi
done

echo "\n--- Frontend / static files ---"
if [[ -d backend/frontend_dist ]]; then
  echo "backend/frontend_dist exists"
  ls -la backend/frontend_dist | sed -n '1,20p'
else
  echo "backend/frontend_dist NOT FOUND"
fi

if [[ -d backend/staticfiles ]]; then
  echo "backend/staticfiles exists"
  ls -la backend/staticfiles | sed -n '1,20p'
else
  echo "backend/staticfiles NOT FOUND"
fi

echo "\n--- Django checks ---"
cd backend
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings}
python manage.py check --deploy || true

echo "\n--- Database connectivity ---"
python manage.py showmigrations --plan | head -n 40 || true

echo "\n--- End of Render check ==="