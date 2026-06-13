#!/usr/bin/env bash
set -euo pipefail

echo "--- Railway deploy diagnostic script ---"
echo "PWD: $(pwd)"

echo "\n--- List backend/frontend_dist ---"
if [ -d backend/frontend_dist ]; then
  ls -la backend/frontend_dist | sed -n '1,200p'
else
  echo "backend/frontend_dist not found"
fi

echo "\n--- List backend/staticfiles ---"
if [ -d backend/staticfiles ]; then
  ls -la backend/staticfiles | sed -n '1,200p'
else
  echo "backend/staticfiles not found"
fi

echo "\n--- Head of backend/frontend_dist/index.html ---"
if [ -f backend/frontend_dist/index.html ]; then
  sed -n '1,120p' backend/frontend_dist/index.html || true
else
  echo "index.html not found in backend/frontend_dist"
fi

echo "\n--- Environment variables of interest ---"
python - <<'PY'
import os
keys = [
  'DEBUG',
  'ALLOWED_HOSTS',
  'CSRF_TRUSTED_ORIGINS',
  'DATABASE_URL',
  'PORT'
]
for k in keys:
    print(k + ':', os.getenv(k))
PY

echo "\n--- Django checks: showmigrations (first) and collectstatic ---"
echo "Showing migrations (first 200 lines):"
python manage.py showmigrations | sed -n '1,200p' || true

echo "\nRunning collectstatic --noinput (this will copy static files to STATIC_ROOT):"
python manage.py collectstatic --noinput || true

echo "\n--- End of diagnostic script ---"

echo "If this runs on Railway, paste the full output here for analysis."
