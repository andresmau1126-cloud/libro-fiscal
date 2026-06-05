Guía rápida para desplegar en Render (automatizada con `scripts/deploy_to_render.ps1`)

1) Generar `SECRET_KEY` segura (opcional):

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

2) Ejecutar el script para añadir commit y hacer push (pasa la URL remota si no tienes `origin`):

```powershell
# Desde la raíz del proyecto
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_to_render.ps1 -RemoteUrl "https://github.com/usuario/repo.git"
```

3) Entra a Render:
- New -> Web Service -> Connect a repository
- Selecciona la rama `main` y confirma
- Render detectará `render.yaml` y creará una base de datos PostgreSQL

4) Añade/valida variables de entorno en el servicio web:
- `DEBUG = false`
- `SECRET_KEY = <tu_clave_generada>`
- `DJANGO_SETTINGS_MODULE = config.settings`
- `ALLOWED_HOSTS = *`

5) Revisa logs (Build / Events). Si hay errores pega aquí los logs y te ayudo a resolverlos.

6) Para confirmar desde el shell de Render, ejecuta:

```bash
bash scripts/render_check.sh
```

Notas:
- El `Dockerfile` ya construye el frontend y el backend.
- Si prefieres que yo ejecute el push aquí, proporciona la URL del repositorio remoto y confirma que autorizas a usar tus credenciales locales (no puedo usar credenciales externas desde aquí).