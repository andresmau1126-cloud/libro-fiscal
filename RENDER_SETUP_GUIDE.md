# Guía Paso a Paso: Configurar Render para Verificación de Email y Persistencia

## 📋 Prerequisitos

- Tienes una cuenta en [Render.com](https://render.com)
- Tu repositorio está en GitHub/GitLab
- Ya desplegaste una vez en Render (tienes un servicio creado)

---

## 🚀 Paso 1: Obtener Credenciales Brevo

1. Ve a [Brevo.com](https://www.brevo.com) (antes Sendinblue)
2. Inicia sesión en tu cuenta
3. En el menú izquierdo, ve a **Configuración → SMTP**
4. Busca y copia estos datos:
   - **Servidor SMTP**: `smtp-relay.brevo.com`
   - **Puerto**: `587`
   - **Usuario SMTP**: tu email o usuario registrado
   - **Contraseña SMTP**: busca la sección "Claves de acceso SMTP"
   - **Email remitente**: el email asociado a tu cuenta

**Si no tienes cuenta Brevo:**
- Regístrate gratis en [Brevo.com](https://www.brevo.com)
- Completa verificación básica
- Obtendrás acceso a SMTP

---

## 🔧 Paso 2: Actualizar Variables en Render

### Opción A: Desde el Dashboard (Recomendado)

1. Ve a [Render.com](https://render.com) Dashboard
2. Selecciona tu servicio web (`render4` o como se llame)
3. Haz clic en **Settings** (esquina superior derecha)
4. Desplázate a **Environment**
5. Busca estas variables (están en azul si están desincronizadas con `render.yaml`):

| Variable | Valor | Ejemplo |
|----------|-------|---------|
| `EMAIL_HOST` | Servidor SMTP | `smtp-relay.brevo.com` |
| `EMAIL_PORT` | Puerto | `587` |
| `EMAIL_HOST_USER` | Tu usuario Brevo | `tu_email@ejemplo.com` |
| `EMAIL_HOST_PASSWORD` | Tu contraseña Brevo | `xxxxxxxxxxx` |
| `DEFAULT_FROM_EMAIL` | Email remitente | `tu_email@ejemplo.com` |
| `BREVO_SENDER_EMAIL` | Email remitente | `tu_email@ejemplo.com` |
| `BREVO_SENDER_NAME` | Nombre del remitente | `Libro Fiscal` |

**Instrucciones detalladas:**

```
Para cada variable:
1. Haz clic en el campo "Value"
2. Pega el valor correspondiente
3. Haz clic en "Update" o presiona Enter
4. El servicio se reiniciará automáticamente
```

### Opción B: Editar render.yaml Localmente

Si prefieres versionar en Git:

```bash
# Edita el archivo
code render.yaml

# Reemplaza las líneas vacías con tus valores:
EMAIL_HOST_USER: "tu_usuario_brevo@ejemplo.com"
EMAIL_HOST_PASSWORD: "tu_contraseña_brevo"
DEFAULT_FROM_EMAIL: "tu_email_brevo@ejemplo.com"
BREVO_SENDER_EMAIL: "tu_email_brevo@ejemplo.com"

# Guarda, haz commit y push
git add render.yaml
git commit -m "Configure Brevo email for Render"
git push origin master

# Render redesplegará automáticamente
```

---

## 🔄 Paso 3: Verificar Base de Datos

En Render Dashboard:

1. Ve a tu servicio web
2. En la pestaña **Databases**, verifica que exista `libro-fiscal-db`
3. El estado debe ser **"Available"** (verde)
4. Si no existe, crea una:
   - Haz clic en **New Database**
   - Elige **PostgreSQL**
   - Nombre: `libro-fiscal-db`
   - Plan: Starter (gratuito)

---

## 🔌 Paso 4: Ejecutar Migraciones en Render

Después de actualizar variables, ejecuta migraciones:

1. En Render Dashboard, ve a tu servicio
2. Haz clic en **Shell** (arriba, al lado de Logs)
3. Ejecuta estos comandos:

```bash
# Navega a la carpeta backend
cd backend

# Ejecuta migraciones
python manage.py migrate

# Verifica que no hay errores
echo "✓ Migraciones completadas"

# Opcional: crea superusuario
# python manage.py createsuperuser
```

---

## ✅ Paso 5: Probar el Flujo Completo

### Prueba 1: Verificación de Email al Registrarse

1. Ve a tu app en Render (la URL está en el dashboard)
2. Haz clic en **Iniciar Sesión** → **¿No tienes cuenta?**
3. Completa:
   - **Nombre**: Tu nombre
   - **Email**: Tu email (DEBE ser accesible)
   - **Contraseña**: Al menos 6 caracteres
   - Haz clic en **Registrarse**

4. **Deberías recibir un email** con un código de 6 dígitos en 1-2 minutos
5. Copia el código y pégalo en la pantalla
6. Haz clic en **Verificar código**
7. ✅ Si funciona: estás logueado

**Si NO llega el email:**
- Revisa Spam/Promociones
- Verifica variables de email en Render
- Revisa logs en Render Shell: `tail -f render.log`

### Prueba 2: Guardar Preferencias

1. Después de iniciar sesión, ve a **Perfil** (esquina superior)
2. Haz clic en **Preferencias** (tab)
3. Cambia:
   - Zona horaria: GMT-5 (Colombia)
   - Moneda: USD
   - Desactiva "Notificaciones por correo"
4. Haz clic en **Guardar preferencias**
5. Verifica el mensaje "Guardadas correctamente"
6. Recarga la página (F5)
7. ✅ Si los cambios persisten: funcionan

### Prueba 3: Crear Libros Fiscales

1. Ve a **Libros Fiscales**
2. Haz clic en **+ Nuevo Libro**
3. Completa:
   - **Nombre**: "Libro 2024"
   - **NIT**: "1234567890"
   - **Año**: 2024
4. Haz clic en **Crear**
5. Haz clic en el libro para verlo
6. Agrega un movimiento de **Ingreso** de $100
7. Cierra sesión completamente
8. Vuelve a iniciar sesión
9. ✅ Si el libro y movimiento están: ¡TODO FUNCIONA!

---

## 🐛 Troubleshooting

### "No recibo código de email"

**Causas comunes:**
1. Variables de email vacías en Render
2. Credenciales de Brevo incorrectas
3. Email en spam

**Soluciones:**
```bash
# En Render Shell:
cd backend

# Prueba envío de email:
python manage.py shell
>>> from apps.usuarios.otp_service import enviar_otp_email
>>> from apps.usuarios.models import Usuario
>>> user = Usuario.objects.first()
>>> enviar_otp_email(user, "123456")
True  # Si retorna True, el email funciona
```

### "La sesión se pierde después de recargar"

**Causas:**
1. Cookie no se guarda correctamente
2. Problema con CSRF

**Soluciones:**
```bash
# Verifica en dev tools (F12):
# Application → Cookies → busca "session_token"
# Debe estar presente y sin "Secure" en dev, con "Secure" en prod

# En Render Shell:
python manage.py shell
>>> from apps.usuarios.models import Usuario
>>> Usuario.objects.count()  # Verifica que puedes acceder a BD
```

### "Los libros no aparecen después de recargar"

**Causas:**
1. Migraciones no ejecutadas
2. Propietario no se asigna correctamente

**Soluciones:**
```bash
# En Render Shell:
cd backend
python manage.py migrate --list  # Ver estado de migraciones
python manage.py migrate  # Ejecutar todas
python manage.py shell
>>> from apps.libros.models import Libro
>>> Libro.objects.count()  # Debe ser > 0 si creaste libros
>>> Libro.objects.first().propietario  # Debe mostrar el usuario
```

---

## 📝 Notas Importantes

- **EMAIL_HOST_PASSWORD**: Mantén esto privado. Usar variables de entorno en Render es seguro
- **SESSION_COOKIE_SECURE**: Ya está configurado en `settings.py` para HTTPS
- **Reinicio automático**: Render reinicia el servicio al cambiar variables (normal, toma ~1 min)
- **Base de datos persistente**: PostgreSQL en Render persiste todos los datos

---

## 🎯 Resumen de Lo Que Debería Funcionar

| Funcionalidad | Backend | Frontend | Render |
|---------------|---------|----------|--------|
| Registro con código | ✅ Listo | ✅ Listo | ⚙️ Requiere email |
| Login con email | ✅ Listo | ✅ Listo | ✅ Funciona |
| Guardar preferencias | ✅ Listo | ✅ Listo | ✅ Funciona |
| Crear libros fiscales | ✅ Listo | ✅ Listo | ✅ Funciona |
| Persistencia de datos | ✅ Listo | ✅ Listo | ✅ BD PostgreSQL |

---

## 💬 Próximos Pasos

Si después de seguir esto aún hay problemas:

1. **Comparte los logs de Render** (Shell):
   ```bash
   tail -f render.log
   ```

2. **Verifica estado de email:**
   ```bash
   cd backend && python manage.py shell
   from django.core.mail import send_mail
   send_mail("Test", "Esto es una prueba", "FROM_EMAIL", ["tu@email.com"])
   ```

3. **Revisa la base de datos:**
   ```bash
   python manage.py dbshell
   SELECT COUNT(*) FROM usuarios;
   ```

---

## ✨ ¡Listo! 

Una vez completados estos pasos, tu aplicación estará completamente funcional con:
- ✅ Verificación de email
- ✅ Persistencia de preferencias
- ✅ Persistencia de libros fiscales
- ✅ Sistema de sesiones seguro

¡Que funcione! 🚀
