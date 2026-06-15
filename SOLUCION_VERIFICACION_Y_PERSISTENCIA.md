# Solución: Verificación de Email y Persistencia de Datos

## Resumen del Análisis

El backend **YA TIENE TODO IMPLEMENTADO**:
- ✅ Verificación por código al registrarse
- ✅ Sistema OTP para login
- ✅ Endpoint para guardar preferencias (`PATCH /api/auth/me`)
- ✅ Libros fiscales guardados con propietario (FK)

El frontend **YA TIENE TODO**:
- ✅ Formulario de registro con verificación
- ✅ Tab de preferencias con botón guardar
- ✅ Carga de libros y movimientos

## Problema Principal: En Render No Funciona Porque

### 1. Falta Configuración de Email (Brevo)
- El código está listo pero **NO TIENE credenciales** en Render
- Variables necesarias: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

### 2. Base de Datos
- ✅ `render.yaml` ya configura PostgreSQL (correcto)
- Pero necesitas verificar que esté creada

### 3. Sesión del Usuario
- Las cookies de sesión se configuran correctamente
- Problema potencial: `SESSION_COOKIE_SECURE` en producción

---

## Pasos Para Arreglarlo en Render

### Paso 1: Agregar Variables de Entorno en Render

Ve a **Render Dashboard → tu servicio → Environment**

Agrega estas variables (reemplaza con tus valores):

```
EMAIL_HOST_USER = tu_usuario_brevo@ejemplo.com
EMAIL_HOST_PASSWORD = tu_clave_brevo
EMAIL_PORT = 587
EMAIL_HOST = smtp-relay.brevo.com
DEFAULT_FROM_EMAIL = tu_email_brevo@ejemplo.com
BREVO_SENDER_EMAIL = tu_email_brevo@ejemplo.com
BREVO_SENDER_NAME = Libro Fiscal
```

**Cómo obtener las credenciales Brevo:**
1. Ve a [Brevo.com](https://www.brevo.com)
2. Inicia sesión → SMTP → Configuración
3. Obtén: Servidor SMTP, Puerto, Usuario, Contraseña

### Paso 2: Verificar Base de Datos

En Render Dashboard:
1. Ve a tu servicio → Databases
2. Verifica que `libro-fiscal-db` exista y esté "Available"
3. Si no, créala desde el botón "New Database"

### Paso 3: Ejecutar Migraciones

En Render, ve a Shell y ejecuta:

```bash
cd backend
python manage.py migrate
```

### Paso 4: Probar el Flujo

1. **Registro:**
   - Ve a tu app → `/login`
   - Haz clic en "¿No tienes cuenta?"
   - Completa: Nombre, Email, Contraseña
   - Deberías recibir un **email con código de 6 dígitos**
   - Ingresa el código → Se crea la cuenta

2. **Preferencias:**
   - Inicia sesión
   - Ve a Perfil → Preferencias
   - Cambia moneda/zona horaria
   - Haz clic "Guardar" → Verifica en la base de datos

3. **Libros Fiscales:**
   - Crea un libro
   - Agrega movimientos (ingresos/egresos)
   - Cierra sesión y vuelve a iniciar
   - Los datos deberían estar ahí

---

## Archivos Importantes (Ya Configurados)

```
backend/apps/usuarios/
├── models.py              → Usuario con campos pref_*
├── views.py               → Endpoints de registro y PATCH /me
├── serializers.py         → UsuarioSerializer con preferences
├── otp_service.py         → Envío de emails
└── authentication.py      → Manejo de sesiones

frontend/src/
├── pages/auth/LoginPage.jsx     → Flujo de registro y verificación
├── pages/perfil/ProfilePage.jsx → Tab de preferencias
├── pages/libros/LibrosPage.jsx  → CRUD de libros
└── context/AuthContext.jsx      → Estado de usuario
```

---

## Variables de Entorno Necesarias en render.yaml

El archivo `render.yaml` necesita actualización (opcional pero recomendado):

```yaml
envVars:
  - key: EMAIL_HOST_USER
    sync: false  # Asegúrate de mantener privado
  - key: EMAIL_HOST_PASSWORD
    sync: false  # Asegúrate de mantener privado
  - key: BREVO_SENDER_EMAIL
    value: "tu_email_brevo@ejemplo.com"
```

---

## Checklist de Verificación

- [ ] Email HOST_USER y HOST_PASSWORD están en Render Env
- [ ] Base de datos PostgreSQL existe y está disponible
- [ ] Migraciones ejecutadas (`python manage.py migrate`)
- [ ] Puedes registrarte y recibir código por email
- [ ] Puedes verificar el código y acceder
- [ ] Puedes guardar preferencias
- [ ] Los libros se ven después de recargar
- [ ] Los movimientos persisten

---

## Troubleshooting

### "No se envía el email"
- [ ] Verifica EMAIL_HOST_USER y EMAIL_HOST_PASSWORD en Render
- [ ] Comprueba que Brevo está activo y tiene créditos
- [ ] Revisa logs de Render: `docker logs` o Shell

### "No veo mis libros después de recargar"
- [ ] Verifica que DATABASE_URL esté en Render Env
- [ ] Ejecuta: `python manage.py migrate` en Shell de Render
- [ ] Comprueba sesión: `authMe()` debería retornar usuario con datos

### "La sesión se pierde"
- [ ] Verifica que la cookie `session_token` está siendo guardada
- [ ] En producción (RENDER), asegúrate: `SESSION_COOKIE_SECURE = True` (ya está en `settings.py`)

---

## Archivos Clave a Revisar

1. **Backend Email Setup** → `backend/config/settings.py` línea 220-235
2. **OTP Service** → `backend/apps/usuarios/otp_service.py`
3. **Registro Frontend** → `frontend/src/pages/auth/LoginPage.jsx`
4. **Preferencias Frontend** → `frontend/src/pages/perfil/ProfilePage.jsx`

---

## Notas Importantes

- El código backend ya está **100% funcional**
- El frontend ya está **100% funcional**
- Solo falta **configuración de email en Render**
- La base de datos está **correctamente configurada** en `render.yaml`

¡Que funcione bien! 🚀
