# 🔑 VARIABLES DE ENTORNO PARA RENDER

**COPIA CADA UNA EN EL DASHBOARD DE RENDER**

---

## Variable 1: DEBUG
```
Key:   DEBUG
Value: false
```

---

## Variable 2: ALLOWED_HOSTS
```
Key:   ALLOWED_HOSTS
Value: libro-fiscal-api.onrender.com
```

---

## Variable 3: SECRET_KEY (GENERADA)
```
Key:   SECRET_KEY
Value: +@=uh+iud++vk3scel#m5xp_rgej%snn5#9qpiu5@6=+8_=2i0
```

⚠️ **NOTA**: Esta clave es única y generada para este deployment. Cópiala exactamente como aparece.

---

## Variable 4: DATABASE_URL
```
Key:   DATABASE_URL
Value: [OBTENER DEL PASO 2 - PostgreSQL Connection String]
```

Ejemplo (reemplazar con tu valor real):
```
postgresql://user:password@dpg-xxxxx-a.ohio-postgres.render.com/libro_fiscal
```

---

## Variable 5: REDIS_URL
```
Key:   REDIS_URL
Value: [OBTENER DEL PASO 3 - Redis Connection String]
```

Ejemplo (reemplazar con tu valor real):
```
rediss://default:password@red-xxxxx.c331.ohio-postgres.render.com:6380
```

---

## Variable 6: CHANNEL_LAYER_BACKEND
```
Key:   CHANNEL_LAYER_BACKEND
Value: channels_redis.core.RedisChannelLayer
```

---

## Variable 7: ASGI_APPLICATION
```
Key:   ASGI_APPLICATION
Value: config.asgi.application
```

---

## 📋 RESUMEN - Orden de creación:

1. **DEBUG** = `false`
2. **ALLOWED_HOSTS** = `libro-fiscal-api.onrender.com`
3. **SECRET_KEY** = `+@=uh+iud++vk3scel#m5xp_rgej%snn5#9qpiu5@6=+8_=2i0`
4. **DATABASE_URL** = [De PostgreSQL]
5. **REDIS_URL** = [De Redis]
6. **CHANNEL_LAYER_BACKEND** = `channels_redis.core.RedisChannelLayer`
7. **ASGI_APPLICATION** = `config.asgi.application`

---

**Una vez agregadas todas las variables, Render automáticamente iniciará el deployment ✅**
