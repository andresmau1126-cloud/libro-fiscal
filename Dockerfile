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

# Copy deployment scripts
COPY scripts/ ./scripts

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist ./frontend_dist

# Ensure proper permissions for static files
RUN chmod -R 755 frontend_dist && chmod -R 755 scripts

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

RUN chmod +x scripts/start_render.sh

CMD ["./scripts/start_render.sh"]
