# Railway deployment instructions

1. **Variables de entorno**
   - Ve a tu proyecto en Railway > Settings > Variables de entorno.
   - Agrega todas las variables del archivo `.env.railway.example` (ajusta valores reales).

2. **Script de build**
    - Ve a Settings > Build Command y pon:
       ```sh
       cd frontend && npm install && npm run build:railway
       ```

3. **Procfile**
   - Ya está correcto:
     ```
     web: cd backend && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
     ```

4. **Logs**
   - Ve a Deployments > Logs y busca errores de migración, base de datos, Gunicorn o Django.
   - Si ves errores, pégalos aquí para diagnóstico.

5. **Base de datos**
   - Si usas PostgreSQL, asegúrate de tener el plugin de Railway y que `DATABASE_URL` apunte a esa base.

6. **Frontend**
   - El build debe estar en `frontend_dist` antes de iniciar Gunicorn.

---

**Con esto tu app debería levantar correctamente en Railway.**

Si tienes errores en los logs, copia el mensaje aquí para ayuda específica.