# ── Stage 1: Build frontend ──
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python + serve ──
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist /app/frontend_dist

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py crear_usuario_prueba && \
    gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
