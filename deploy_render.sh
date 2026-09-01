#!/bin/bash
# Script de deployment para Render.com
# Sistema de Inventario Centralizado v1.0
# 
# Uso: ./deploy_render.sh

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  DEPLOYMENT - Sistema de Inventario Centralizado en Render    ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 PASO 1: Verificar que Git está actualizado${NC}"
git status

echo -e "\n${YELLOW}📋 PASO 2: Hacer commit de los cambios${NC}"
git add .
git commit -m "fix(inventario): asegurar persistencia de datos y arreglar WebSocket

- Arreglar channel layer para funcionar sin WebSocket configurado
- Cambiar get_or_create en HistorialVentas para evitar duplicados
- Actualizar websocket_utils para ser más robusto
- Pruebas de persistencia: TODO persiste correctamente en BD

Sistema listo para Render con datos persistentes."

echo -e "${GREEN}✓ Cambios commiteados${NC}"

echo -e "\n${YELLOW}📋 PASO 3: Push a GitHub${NC}"
git push origin main

echo -e "${GREEN}✓ Push completado${NC}"

echo -e "\n${YELLOW}📋 PASO 4: Configuración de Render${NC}"

echo -e "\n${YELLOW}Instrucciones para Render.com:${NC}"
echo "
1. Ir a: https://dashboard.render.com
2. Clickear: 'New +' → 'Web Service'
3. Conectar repositorio GitHub
4. Configurar servicio:
   - Name: libro-fiscal-api
   - Environment: Python 3.11
   - Build Command:
     cd backend && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   - Start Command:
     cd backend && daphne -b 0.0.0.0 -p 10000 config.asgi:application
   
5. Agregar variables de entorno:
   ✓ DEBUG=false
   ✓ ALLOWED_HOSTS=tu-dominio.onrender.com
   ✓ SECRET_KEY=generar-clave-segura
   ✓ DATABASE_URL=postgres://...
   ✓ REDIS_URL=redis://...
   ✓ CHANNEL_LAYER_BACKEND=channels_redis.core.RedisChannelLayer
   
6. Crear servicios adicionales:
   - PostgreSQL Database
   - Redis
   
7. Conectar servicios
8. Deploy
"

echo -e "\n${GREEN}✅ Script de deployment completado${NC}"
echo -e "${GREEN}Próximo paso: Configurar servicios en Render${NC}"
