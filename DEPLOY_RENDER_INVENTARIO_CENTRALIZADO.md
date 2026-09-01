# Deploy en Render - Inventario Centralizado en Tiempo Real

## Descripción
Este documento describe cómo desplegar la aplicación Libro Fiscal v2 en Render con soporte completo para:
- Inventario centralizado sincronizado en tiempo real
- WebSocket para actualizaciones instantáneas
- Historial detallado de ventas e inventario
- Estadísticas por vendedor

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        RENDER.COM                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Django + Daphne (ASGI)                      │    │
│  │  - REST API (HTTP)                                  │    │
│  │  - WebSocket (ws://)                                │    │
│  │  - Inventario Centralizado                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                        ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │      PostgreSQL Database (Render)                   │    │
│  │  - Productos                                        │    │
│  │  - Ventas & HistorialVentas                        │    │
│  │  - HistorialInventario (auditoria)                 │    │
│  │  - EstadoInventarioCentralizado (tiempo real)      │    │
│  │  - ResumenVentasPorVendedor                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │      Redis (para Channels Layer)                   │    │
│  │  - Sincronización WebSocket                        │    │
│  │  - Broadcast de cambios de inventario              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         ↑                           ↑
         │ HTTP                      │ WebSocket
         │                           │
    ┌────────────────────────────────────────┐
    │         Frontend (React/Vite)          │
    │  - Vista de Inventario Centralizado    │
    │  - Historial de Ventas                 │
    │  - Estadísticas del Vendedor           │
    │  - Sincronización en Tiempo Real       │
    └────────────────────────────────────────┘
```

## Configuración Paso a Paso

### 1. Preparación del Repositorio

```bash
# En tu rama principal
git add .
git commit -m "Agregar inventario centralizado, WebSocket y rastreo de historial"
git push
```

### 2. Crear Servicio en Render

**a) Base de datos PostgreSQL:**

1. Ve a [render.com](https://render.com)
2. Dashboard → New → PostgreSQL
3. Configurar:
   - **Name:** `libro-fiscal-db`
   - **Database:** `libro_fiscal`
   - **User:** `postgres`
   - Region: Tu región
4. Copiar **Internal Database URL** (para conexión dentro de Render)

**b) Servicio Redis (para Channels):**

1. Dashboard → New → Redis
2. Configurar:
   - **Name:** `libro-fiscal-redis`
   - **Plan:** Free
3. Copiar **Internal Redis URL**

**c) Servicio Web (Django):**

1. Dashboard → New → Web Service
2. Conectar repositorio GitHub
3. Configurar:
   - **Name:** `libro-fiscal-api`
   - **Runtime:** Python 3
   - **Build Command:**
   ```bash
   pip install -r backend/requirements.txt && python backend/manage.py migrate --no-input && python backend/manage.py collectstatic --no-input
   ```
   - **Start Command:**
   ```bash
   cd backend && daphne -b 0.0.0.0 -p 10000 config.asgi:application
   ```

### 3. Variables de Entorno en Render

En el servicio Web, agregar en **Environment**:

```env
# Base de datos (obtener de PostgreSQL service)
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/libro_fiscal

# Redis (obtener de Redis service)
REDIS_URL=redis://default:PASSWORD@HOST:PORT

# Channels
CHANNEL_LAYER_BACKEND=channels_redis.core.RedisChannelLayer

# Django
DEBUG=False
SECRET_KEY=tu-clave-secreta-aqui-cambiar-en-produccion
ALLOWED_HOSTS=tu-dominio.onrender.com,localhost,127.0.0.1

# CORS
CORS_ALLOWED_ORIGINS=https://tu-dominio.onrender.com,https://frontend.onrender.com

# Email (Brevo)
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email-brevo@ejemplo.com
EMAIL_HOST_PASSWORD=tu-api-key-brevo
DEFAULT_FROM_EMAIL=tu-email-brevo@ejemplo.com
ALERTA_EMAIL_DESTINO=alerta@ejemplo.com

# Otros
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
CSRF_TRUSTED_ORIGINS=https://tu-dominio.onrender.com
```

### 4. Configuración de Procfile

El archivo `Procfile` ya existe, pero asegurate que tiene:

```procfile
web: cd backend && daphne -b 0.0.0.0 -p $PORT config.asgi:application
```

### 5. Conectar PostgreSQL y Redis

En la sección **Environment** del servicio Web en Render:

1. Agregar manualmente:
   - `DATABASE_URL` (de PostgreSQL)
   - `REDIS_URL` (de Redis)

### 6. Desplegar

1. Cambios automáticos: Cada push a GitHub dispara un deploy
2. Ver logs: Dashboard → Servicio → Logs
3. Probar: Ir a `https://tu-dominio.onrender.com/api/`

## Endpoints Disponibles

### Inventario Centralizado (REST)

```
GET    /api/inventario-centralizado/              # Ver inventario centralizado
GET    /api/inventario-centralizado/?critico=1   # Solo productos críticos
GET    /api/productos/criticos/                  # Productos con stock bajo
GET    /api/resumen/inventario/                  # Resumen general (solo supervisores)
```

### Historial e Historial de Inventario

```
GET    /api/historial/inventario/<producto_id>/  # Historial de movimientos de un producto
GET    /api/historial/ventas/                     # Historial de ventas del vendedor actual
GET    /api/historial/ventas/?vendedor_id=2      # Historial de otro vendedor (solo supervisores)
GET    /api/historial/ventas/?dias=90            # Últimos 90 días
```

### Estadísticas

```
GET    /api/estadisticas/vendedor/                # Estadísticas del vendedor actual
GET    /api/estadisticas/vendedor/?vendedor_id=2 # Estadísticas de otro vendedor (solo supervisores)
GET    /api/resumen/ventas-diarias/               # Resumen de ventas del día
GET    /api/resumen/ventas-diarias/?fecha=2024-01-15  # Fecha específica
```

### WebSocket (Tiempo Real)

```
ws://tu-dominio.onrender.com/ws/inventario/
ws://tu-dominio.onrender.com/ws/inventario/5/              # Producto específico
ws://tu-dominio.onrender.com/ws/ventas/2/                  # Ventas de vendedor
ws://tu-dominio.onrender.com/ws/notificaciones/             # Notificaciones
```

## Mensajes WebSocket

### Inventario Actualizado

```json
{
  "tipo": "inventario_actualizado",
  "data": {
    "producto_id": 1,
    "stock_anterior": 100,
    "stock_posterior": 95,
    "tipo_movimiento": "venta",
    "usuario": "Juan Vendedor",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Venta Registrada

```json
{
  "tipo": "venta_registrada",
  "data": {
    "venta_id": 42,
    "vendedor": "Juan Vendedor",
    "monto_total": 500.00,
    "cantidad_productos": 3,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Stock Bajo

```json
{
  "tipo": "stock_bajo",
  "titulo": "Stock Bajo",
  "mensaje": "Stock bajo: Arroz (5 <= 10)",
  "producto": "Arroz",
  "stock_actual": 5,
  "stock_minimo": 10
}
```

## Modelos de Base de Datos

### EstadoInventarioCentralizado
Sincroniza el estado actual del inventario en tiempo real.

```python
{
  "id": 1,
  "producto_id": 5,
  "stock_disponible": 50,
  "ultima_actualizacion": "2024-01-15T10:30:00Z",
  "usuario_actualizo": "Admin",
  "es_critico": false,
  "version": 15
}
```

### HistorialInventario
Registra todos los cambios de inventario (entradas, ventas, ajustes).

```python
{
  "id": 1,
  "producto": "Arroz",
  "tipo_movimiento": "venta",
  "cantidad_anterior": 100,
  "cantidad_movida": -5,
  "cantidad_posterior": 95,
  "usuario": "Juan Vendedor",
  "vendedor": "Juan Vendedor",
  "razon": "Venta a Cliente X",
  "fecha": "2024-01-15T10:30:00Z"
}
```

### HistorialVentas
Resumen detallado de cada venta con métricas.

```python
{
  "id": 1,
  "venta_id": 42,
  "vendedor": "Juan Vendedor",
  "fecha_venta": "2024-01-15T10:30:00Z",
  "cantidad_productos": 3,
  "cantidad_total_unidades": 10.5,
  "monto_total": 500.00,
  "monto_costo": 300.00,
  "ganancia": 200.00,
  "margen_ganancia": 40.0,
  "cliente": "Tienda X"
}
```

### ResumenVentasPorVendedor
Resumen diario de ventas por vendedor.

```python
{
  "id": 1,
  "vendedor": "Juan Vendedor",
  "fecha": "2024-01-15",
  "cantidad_ventas": 5,
  "cantidad_unidades": 50.5,
  "monto_total": 2500.00,
  "monto_costo": 1500.00,
  "ganancia_total": 1000.00,
  "margen_promedio": 40.0
}
```

## Pruebas

### 1. Probar API REST

```bash
# Obtener inventario centralizado
curl -H "Authorization: Token TU-TOKEN" \
  https://libro-fiscal.onrender.com/api/inventario-centralizado/

# Obtener historial de ventas
curl -H "Authorization: Token TU-TOKEN" \
  https://libro-fiscal.onrender.com/api/historial/ventas/

# Obtener estadísticas
curl -H "Authorization: Token TU-TOKEN" \
  https://libro-fiscal.onrender.com/api/estadisticas/vendedor/
```

### 2. Probar WebSocket

```bash
# Desde JavaScript/Frontend
const socket = new WebSocket(
  'wss://libro-fiscal.onrender.com/ws/inventario/'
);

socket.onopen = () => {
  console.log('Conectado');
  socket.send(JSON.stringify({ tipo: 'request_estado' }));
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Mensaje:', data);
};
```

## Troubleshooting

### 1. WebSocket no conecta

**Posibles causas:**
- Redis no está configurado correctamente
- CHANNEL_LAYER_BACKEND no es `channels_redis.core.RedisChannelLayer`
- Certificado SSL no válido

**Solución:**
```bash
# Verificar logs en Render
# Dashboard → Servicio → Logs

# Reiniciar servicio
# Dashboard → Servicio → Manual Deploy
```

### 2. Migraciones no se aplican

**Solución:**
```bash
# En Build Command, asegurar:
python backend/manage.py migrate --no-input
```

### 3. WebSocket desconecta frecuentemente

**Causa:** Redis no está conectado correctamente

**Solución:**
1. Verificar REDIS_URL en Environment
2. Usar Redis URL **Internal** (no Public)
3. Agregar puerto correcto al final (generalmente :6379)

## Rendimiento y Escalabilidad

### Para Producción:

1. **Usar Redis de pago en Render:**
   - Free tier tiene limitaciones de conexión

2. **Usar PostgreSQL Standard:**
   - Free tier tiene limitaciones de recursos

3. **Variables de Channels:**
   ```python
   CHANNEL_LAYERS = {
       "default": {
           "BACKEND": "channels_redis.core.RedisChannelLayer",
           "CONFIG": {
               "hosts": [os.getenv("REDIS_URL", "redis://localhost:6379")],
               "capacity": 1500,
               "expiry": 10,
           },
       },
   }
   ```

4. **Habilitar Compresión:**
   - En frontend: usar gzip
   - En backend: WHITENOISE_USE_FINDERS = True

## Monitoreo

### Logs Importantes

```bash
# WebSocket conectados
grep "conectado" <logs>

# Errores de Channels
grep "ChannelError" <logs>

# Errores de base de datos
grep "DatabaseError" <logs>
```

### Métricas Recomendadas

- Conexiones WebSocket activas
- Latencia de actualización de inventario
- Errores de conexión a base de datos
- Uso de memoria Redis

## Documentación Completa de Endpoints

### GET /api/inventario-centralizado/

Retorna el estado centralizado del inventario.

**Autenticación:** Requerida (Token)

**Query Parameters:**
- `critico` (opcional): "1" o "true" para filtrar solo críticos
- `categoria` (opcional): Filtrar por categoría

**Respuesta:**
```json
{
  "inventario": [
    {
      "id": 1,
      "producto_id": 5,
      "producto_nombre": "Arroz",
      "stock_disponible": 50,
      "stock_minimo": 10,
      "stock_actual": 50,
      "precio_venta": 2.50,
      "costo_unitario": 1.50,
      "categoria": "Alimentos",
      "es_critico": false,
      "ultima_actualizacion": "2024-01-15T10:30:00Z",
      "usuario_actualizo": "Admin",
      "version": 15
    }
  ],
  "total_items": 1,
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### GET /api/historial/inventario/<producto_id>/

Retorna el historial de movimientos de un producto.

**Autenticación:** Requerida

**Query Parameters:**
- `dias` (opcional): Últimos N días (default: 30)

**Respuesta:**
```json
{
  "producto_id": 5,
  "producto_nombre": "Arroz",
  "historial": [
    {
      "id": 1,
      "producto": "Arroz",
      "tipo_movimiento": "venta",
      "cantidad_anterior": 100,
      "cantidad_movida": -5,
      "cantidad_posterior": 95,
      "usuario": "Juan Vendedor",
      "vendedor": "Juan Vendedor",
      "razon": "Venta a Cliente X",
      "fecha": "2024-01-15T10:30:00Z"
    }
  ],
  "total_movimientos": 1
}
```

Completar con más documentación según sea necesario...
