# Inventario Compartido en Render - Instrucciones de Despliegue

## 📋 Resumen del Cambio

Se ha modificado la lógica del inventario para que sea **verdaderamente compartido** entre todos los usuarios (vendedores, admin, gerente):

### Cambios Realizados:
1. **GET /api/productos** → Devuelve TODOS los productos a todos los usuarios
2. **POST /api/productos** → Solo usuarios con `can_write` pueden crear
3. **PUT /api/productos/{id}** → Solo propietario o admin/gerente pueden editar
4. **DELETE /api/productos/{id}** → Solo propietario o admin/gerente pueden eliminar

### Beneficio:
- Vendedores, admin y gerente ven el **mismo inventario en tiempo real**
- Las actualizaciones de stock se reflejan inmediatamente para todos
- Base de datos: sin cambios (compatible hacia atrás)

---

## 🚀 Pasos para Actualizar en Render

### 1. **Render ya debe detectar el cambio automáticamente**
   - GitHub → Render está conectado en `main` branch
   - El nuevo commit `b5eee5f` debería triggerear un redeploy automático

### 2. **Verificar que el deploy comenzó**
   - Ir a: https://dashboard.render.com
   - Seleccionar el Web Service (libro-fiscal)
   - Ver la sección "Deploys" - debe mostrar un nuevo deploy en progreso

### 3. **Esperar a que termine (3-5 minutos)**
   - Ver los logs para confirmar:
     - ✅ `npm run build` completó
     - ✅ `python manage.py collectstatic` completó
     - ✅ `daphne config.asgi:application` inició

### 4. **Probar en producción**
   ```bash
   # Abrir en navegador
   https://tu-app-render.com/inventario
   
   # Probar como vendedor:
   # - Ver que muestra TODOS los productos (no solo los propios)
   
   # Probar como admin:
   # - Ver que muestra TODOS los productos
   # - Intentar editar un producto de otro vendedor (debe permitir)
   ```

---

## ✅ Checklist de Validación

- [ ] Render muestra deploy completado sin errores
- [ ] Login funciona correctamente
- [ ] Vendedor ve todos los productos
- [ ] Admin ve todos los productos
- [ ] Gerente ve todos los productos
- [ ] Stock actualizado se refleja en tiempo real para todos
- [ ] Intentar editar un producto ajeno como vendedor (debe fallar con 403)

---

## 🔄 Si Algo Falla

### Opción 1: Rollback Manual
```bash
# En Render dashboard:
1. Ir a Web Service → Deploys
2. Encontrar el deploy anterior (b5eee5f)
3. Clickear "Redeploy"
```

### Opción 2: Check Logs
```bash
# En Render:
1. Ir a Logs
2. Buscar errores con: "error", "failed", "AttributeError"
3. Si hay error en vistas.py, revisar sintaxis
```

### Opción 3: Rebuild Manual
```bash
# En Render dashboard:
1. Ir a Web Service
2. Clickear "Manual Deploy"
3. Seleccionar branch "main"
```

---

## 📝 Notas Técnicas

### Cambios en Backend:
- **Archivo**: `backend/apps/inventario/views.py`
- **Función nueva**: `_productos_qs_visible_to_user(user)` 
- **Cambio en**: `productos_list_create()` y `producto_detail()`

### Base de Datos:
- ✅ Modelo `Producto` sin cambios
- ✅ Campo `propietario` se mantiene (auditoria)
- ✅ Compatible con datos existentes

### Base de Datos de Render:
- ✅ NO requiere migraciones nuevas
- ✅ Los datos existentes siguen igual
- ✅ El cambio es solo en lógica de lectura

---

## 🎯 Próximos Pasos

1. Confirmar que el deploy completó ✅
2. Probar inventario compartido en producción
3. Si funciona, documentar en COMIENZA_AQUI.md
4. Crear punto de control (respaldo) como referencia

---

**Última actualización**: 2026-09-01  
**Rama**: main  
**Commit**: b5eee5f (inventario compartido)
