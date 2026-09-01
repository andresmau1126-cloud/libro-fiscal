# 🚀 GUÍA RENDER - PASO A PASO

## ✅ STATUS ACTUAL
- ✓ Código en GitHub (push completado)
- ✓ Commit: feat(inventario): sistema centralizado con persistencia garantizada
- ⏳ Falta: Configurar servicios en Render

---

## 📋 PASO 1: Iniciar Sesión en Render

1. Ir a: https://dashboard.render.com
2. Click en **"GitHub"**
3. Autorizar Render en GitHub
4. Seleccionar repositorio: **`libro-fiscal`**
5. Confirmar

---

## 📦 PASO 2: Crear PostgreSQL Database

1. En Dashboard → Click **"New +"** en esquina superior derecha
2. Seleccionar **"PostgreSQL"**
3. Configurar:
   - **Name**: `postgres-libro-fiscal`
   - **Database Name**: `libro_fiscal`
   - **User**: (dejar por defecto o crear)
   - **Password**: (generar automática)
   - **Region**: `Ohio` (o tu región preferida)
   - **PostgreSQL Version**: 15
   - **Plan**: `Standard` ($15/mes)

4. Click **"Create Database"**
5. **IMPORTANTE**: Una vez creada, aparecerá en el dashboard
   - Click en el nombre: `postgres-libro-fiscal`
   - Copiar el **`Connection String`** (empieza con `postgresql://`)
   - Guardarla en un lugar seguro (la usarás en Paso 5)

**Ejemplo de conexión:**
```
postgresql://usuario:password@dpg-xxxxx-a.ohio-postgres.render.com/libro_fiscal
```

---

## 🔴 PASO 3: Crear Redis Cache

1. En Dashboard → Click **"New +"**
2. Seleccionar **"Redis"**
3. Configurar:
   - **Name**: `redis-libro-fiscal`
   - **Region**: `Ohio`
   - **Plan**: `Standard` ($15/mes)
   - **Maxmemory Policy**: `allkeys-lru`

4. Click **"Create"**
5. Una vez creada:
   - Click en el nombre: `redis-libro-fiscal`
   - Copiar el **`Connection String`** (empieza con `redis://` o `rediss://`)
   - Guardarla

**Ejemplo de conexión:**
```
rediss://default:password@red-xxxxx.c331.ohio-postgres.render.com:6380
```

---

## 🌐 PASO 4: Crear Web Service

1. En Dashboard → Click **"New +"**
2. Seleccionar **"Web Service"**
3. Conectar GitHub:
   - Click **"GitHub"**
   - Seleccionar repositorio: **`libro-fiscal`**
   - Seleccionar rama: **`main`**
   - Click **"Connect"**

4. Configurar el servicio:
   - **Name**: `libro-fiscal-api`
   - **Environment**: `Python 3`
   - **Build Command** (copiar exactamente):
   ```
   cd backend && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
   - **Start Command** (copiar exactamente):
   ```
   cd backend && daphne -b 0.0.0.0 -p $PORT config.asgi:application
   ```
   - **Region**: `Ohio`
   - **Plan**: `Standard` ($7/mes)

5. Click **"Create Web Service"** (esto iniciará el deployment)

---

## 🔑 PASO 5: Agregar Variables de Entorno

Una vez creado el Web Service, aparecerá en el dashboard.

1. Click en el nombre: **`libro-fiscal-api`**
2. En el menú de la izquierda → Click **"Environment"**
3. Click **"Add Environment Variable"**

Agregar estas variables (una por una):

### Variable 1: DEBUG
- **Key**: `DEBUG`
- **Value**: `false`
- Click **"Add"**

### Variable 2: ALLOWED_HOSTS
- **Key**: `ALLOWED_HOSTS`
- **Value**: `libro-fiscal-api.onrender.com`
- Click **"Add"**

### Variable 3: SECRET_KEY
Generar una clave segura. En PowerShell (en tu proyecto):
```powershell
cd backend
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copiar el resultado y pegarlo:
- **Key**: `SECRET_KEY`
- **Value**: `[pegar el resultado]`
- Click **"Add"**

### Variable 4: DATABASE_URL
Copiar la conexión de PostgreSQL del Paso 2:
- **Key**: `DATABASE_URL`
- **Value**: `[pegar Connection String de PostgreSQL]`
- Click **"Add"**

### Variable 5: REDIS_URL
Copiar la conexión de Redis del Paso 3:
- **Key**: `REDIS_URL`
- **Value**: `[pegar Connection String de Redis]`
- Click **"Add"**

### Variable 6: CHANNEL_LAYER_BACKEND
- **Key**: `CHANNEL_LAYER_BACKEND`
- **Value**: `channels_redis.core.RedisChannelLayer`
- Click **"Add"**

### Variable 7: ASGI_APPLICATION
- **Key**: `ASGI_APPLICATION`
- **Value**: `config.asgi.application`
- Click **"Add"**

---

## 🚀 PASO 6: Deployment

1. Una vez agregadas todas las variables, el Web Service comenzará a compilar automáticamente
2. Ver progreso en el tab **"Logs"**
3. Esperar ~3-5 minutos
4. Cuando veas: `Starting Daphne 4.x` → ✅ Deployment exitoso
5. Tu URL será: `https://libro-fiscal-api.onrender.com`

---

## ✅ VERIFICACIÓN POST-DEPLOYMENT

Una vez que Daphne esté corriendo:

### Test 1: Verificar que la API responde
```bash
curl https://libro-fiscal-api.onrender.com/api/inventario/ -H "Authorization: Token YOUR_TOKEN"
```

### Test 2: Verificar persistencia
Crear una venta de prueba y luego verificar que persiste después de recargar.

---

## 📊 COSTO MENSUAL EN RENDER

- PostgreSQL: $15
- Redis: $15
- Web Service: $7
- **Total: $37/mes**

(Puedes usar free tier, pero tiene limitaciones)

---

## 🆘 TROUBLESHOOTING

### Logs muestran "Database connection failed"
- Verificar que DATABASE_URL es correcto
- Esperar a que PostgreSQL esté listo (~1 minuto)
- Hacer click **"Restart service"** en el dashboard

### Logs muestran "Redis connection failed"
- Verificar que REDIS_URL es correcto
- Esperar a que Redis esté listo (~1 minuto)
- El servicio funcionará sin Redis (fallback a memory)

### Build fallaQué
- Ver logs completos
- Verificar requirements.txt existe
- Revisar que settings.py está correcto

---

## 🎯 PRÓXIMOS PASOS DESPUÉS DE DEPLOYMENT

1. ✅ Crear usuario admin
2. ✅ Crear usuarios vendedor, gerente
3. ✅ Crear productos de prueba
4. ✅ Probar inventario centralizado
5. ✅ Configurar frontend React (opcional)

