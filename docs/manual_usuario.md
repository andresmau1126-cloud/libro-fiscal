# Manual de usuario - Sustentacion Libro Fiscal v2

## Datos de prueba

El seed crea cuatro perfiles. Se puede iniciar sesión usando el alias corto o el correo equivalente:

- `admin` / `admin123`
- `gerente` / `gerente123`
- `vendedor` / `vendedor123`
- `auditor` / `auditor123`

El libro fiscal principal usa el NIT `1010085627` y los productos ya aparecen cargados por categoria.

## Orden de operacion

### 1. Login

1. Abrir la URL de Render.
2. Escribir usuario y contraseña.
3. Confirmar que el menu corresponde al rol.
4. Verificar el dashboard y el nombre del usuario.

### 2. Venta del vendedor

1. Entrar a **Ventas**.
2. Seleccionar producto, cantidad y medio de pago.
3. Confirmar la venta.
4. Verificar que el stock disminuye.
5. Revisar **Ventas del dia**: el vendedor solo ve sus registros.
6. Confirmar que el total se refleja en el libro fiscal y en el movimiento consolidado del dia.

### 3. Egreso por proveedor

1. Ingresar con el perfil admin.
2. Abrir **Egresos**.
3. Seleccionar o crear proveedor.
4. Seleccionar el libro fiscal del NIT `1010085627`.
5. Ingresar fecha, producto/descripcion, cantidad, valor unitario y valor pagado.
6. Guardar y comprobar que se crea el egreso y su movimiento con saldo recalculado.
7. Confirmar que gerente y auditor pueden consultarlo, pero no modificarlo.

### 4. Libro fiscal

1. Abrir **Libros fiscales**.
2. Elegir el libro por NIT y año.
3. Filtrar movimientos por año/mes.
4. Comprobar ingresos de ventas, egresos de proveedor y saldo acumulado.
5. Exportar a Excel cuando se requiera entregar el periodo.

### 5. Estadisticas

1. Entrar con admin, gerente o auditor.
2. Abrir el dashboard de estadísticas.
3. Seleccionar periodo diario o mensual.
4. Comparar vendedor, cantidad de ventas, total vendido y ticket promedio.
5. Confirmar que el vendedor no puede consultar datos de otros vendedores.

## Prueba de solo lectura del auditor

Con `auditor@sustentacion.local` comprobar que puede consultar productos, ventas, egresos, libros, movimientos, estadísticas y auditoría. Intentar crear, editar y eliminar en cada módulo: todas las operaciones deben responder con acceso denegado.

## Prueba de roles

- Vendedor: vender y consultar sus propias ventas.
- Admin: administrar catálogo, proveedores, egresos, usuarios y consolidado.
- Gerente: consultar estadísticas y libro fiscal sin cambiar configuración.
- Auditor: solo visualizar.

## Cierre para sustentacion

Antes de la demostracion confirmar que `/healthz/` responde correctamente, que el servicio conserva datos después de reiniciar y que los logs muestran migraciones, `seed_demo` y Daphne iniciados.
