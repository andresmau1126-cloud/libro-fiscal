# Manual tecnico - Libro Fiscal v2

## 1. Alcance y arquitectura

Aplicacion web Django + React/Vite para libro fiscal, inventario, ventas, egresos, proveedores, auditoria y estadisticas.

- Backend: Django 4.2, Django REST Framework y PostgreSQL en Render.
- Cliente: React/Vite compilado a `frontend_dist` y servido por Django/WhiteNoise.
- Servidor: Daphne/ASGI (`config.asgi:application`).
- Tiempo real: Django Channels; Redis se configura con `REDIS_URL` y `CHANNEL_LAYER_BACKEND=channels_redis.core.RedisChannelLayer`.
- Despliegue: Dockerfile; migraciones, static files y `seed_demo` se ejecutan al iniciar.

## 2. Roles y reglas

| Rol | Permisos |
|---|---|
| vendedor / vendedor_2 | Crear ventas, consultar productos y consultar unicamente sus ventas e historial. |
| admin | Consolidado de todos los vendedores; crear, editar y eliminar productos, proveedores, egresos, movimientos y libros; gestionar usuarios. |
| gerente | Consultar inventario, libros, movimientos, ventas y estadisticas; no modifica catalogo, proveedores, egresos ni usuarios. |
| auditor | Solo lectura en todos los modulos; no crea, edita ni elimina. |

Toda venta se guarda en `Venta`/`DetalleVenta`, descuenta inventario y actualiza el libro con NIT `1010085627`. La consolidacion diaria elimina el movimiento anterior de ventas del dia, calcula el nuevo SUM y crea un unico movimiento.

Los egresos son creados por admin con su proveedor y libro fiscal; cada egreso queda asociado a un `Movimiento` de tipo egreso y se recalculan saldos inmediatamente.

## 3. Tablas principales

- `usuarios`, `sesiones`, `otps`: identidad, autenticacion y sesiones.
- `libro`: libros fiscales por NIT y anio.
- `movimientos`: ingresos, egresos y saldo acumulado.
- `inventario_producto`: catalogo, categoria, stock, costos, precios y vencimiento.
- `inventario_venta`, `inventario_detalle_venta`: ventas y detalle.
- `providers`: nombre, NIT, telefono y direccion de proveedores.
- `expenses`: proveedores y egresos vinculados a libro/movimiento.
- `inventario_producto.proveedor_id`: proveedor de cada producto.
- `inventario_historial_inventario`, `inventario_historial_ventas`, `inventario_estado_centralizado`, `inventario_resumen_ventas_vendedor`: trazabilidad y consolidado.
- `auditoria`: registro de acciones.

## 4. API

Base: `/api/`. Autenticacion: cookie `session_token` o `Authorization: Bearer <session_token>`.

| Metodo | Ruta | Uso |
|---|---|---|
| POST | `/auth/register/` | Registrar usuario |
| POST | `/auth/login/` | Iniciar sesion |
| GET/PATCH | `/auth/me/` | Consultar/actualizar preferencias |
| GET/POST | `/libros` | Consultar o crear libro |
| GET/PUT/DELETE | `/libros/<id>` | Consultar, editar o eliminar libro |
| GET | `/entries` | Consultar movimientos |
| POST | `/entries` | Crear egreso, solo admin |
| PUT/DELETE | `/entries/<id>` | Editar/eliminar movimiento, solo admin |
| GET | `/productos` | Inventario compartido |
| POST | `/productos` | Crear producto, solo admin |
| GET/PUT/DELETE | `/productos/<id>` | Consultar o administrar producto |
| GET/POST | `/ventas` | Vendedor crea; vendedor ve las propias; supervisores consultan |
| DELETE | `/ventas/<id>` | Vendedor propietario o admin elimina y restaura stock |
| GET/POST | `/providers` | Consultar o crear proveedor, escritura solo admin |
| GET/POST | `/expenses` | Consultar o registrar egreso, escritura solo admin |
| GET | `/stats` | Estadisticas de ventas, gerente/admin/auditor |
| GET | `/auditoria` | Auditoria para roles de supervision |
| GET | `/healthz/` | Health check de Render |
| GET | `/fiscal-books` | Consolidado diario de ventas y egresos del NIT `1010085627` |

## 5. Seeds y datos de sustentacion

Comando idempotente:

```bash
python backend/manage.py seed_demo
node scripts/seed.js
```

Crea 4 usuarios, 10 proveedores con NIT/telefono/direccion, 42 productos de refrigeracion, desechables, aseo, abarrotes y bebidas, 20 ventas, 10 egresos y el libro fiscal del NIT `1010085627`. En Render se ejecuta automaticamente desde `scripts/start_render.sh` despues de migraciones. Los wrappers equivalentes son `seeds/products_seed.js` y `seeds/full_seed.js`.

## 6. Crons y respaldos

- `compilar-ventas-diarias`: consolida ventas del dia en el libro fiscal y reemplaza el movimiento diario. Configurar a las 06:10 UTC.
- `backup-fiscal-diario`: ejecuta `backup_fiscal` cada 24 horas y requiere `BACKUP_DIR`, `GITHUB_BACKUP_REPOSITORY` y `GITHUB_BACKUP_TOKEN`.
- Los crons deben usar la misma `DATABASE_URL` PostgreSQL del servicio web.

## 7. Verificacion de despliegue

1. Revisar logs de Render: migraciones, `seed_demo` y `Starting Daphne`.
2. Abrir `/healthz/` y comprobar `{"status":"ok"}`.
3. Iniciar sesion con un usuario demo.
4. Probar venta, egreso, libro fiscal, estadisticas y acceso auditor.
5. Confirmar persistencia tras reinicio del servicio.
