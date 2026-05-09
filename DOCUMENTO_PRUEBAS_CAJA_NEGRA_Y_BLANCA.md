# Documento de Pruebas: Caja Negra y Caja Blanca

Fecha: 8 de mayo de 2026
Proyecto: Libro Fiscal v2

## 1. Objetivo

Establecer y ejecutar pruebas funcionales (caja negra) y pruebas estructurales (caja blanca) para validar comportamiento externo del sistema y lógica interna crítica del backend.

## 2. Alcance

Se implementaron pruebas en módulos del backend:

- Movimientos
- Inventario

Archivos de pruebas creados:

- backend/apps/movimientos/tests.py
- backend/apps/inventario/tests.py

## 3. Pruebas de Caja Negra

Las pruebas de caja negra validan entradas y salidas del sistema sin depender de la implementación interna.

### 3.1 Movimientos (API)

Casos cubiertos:

1. Acceso a /api/entries sin autenticación: acceso denegado.
2. Creación válida de movimiento: retorna 201 y saldo calculado correctamente.
3. Creación con fecha fuera del año del libro: retorna 400.
4. Creación sobre libro de otro usuario: retorna 404.

Resultado esperado: el endpoint respeta permisos, reglas de dominio y contratos de respuesta.

### 3.2 Inventario (API)

Casos cubiertos:

1. Acceso a /api/productos sin autenticación: acceso denegado.
2. Registro duplicado de producto por mismo usuario: retorna 409.
3. Filtro low_stock=1: devuelve solo productos con stock bajo.
4. /api/alertas-resumen: conteos correctos de bajo_stock, por_vencer, vencidos y total.

Resultado esperado: respuestas HTTP y contenido de payload consistentes con la lógica funcional.

## 4. Pruebas de Caja Blanca

Las pruebas de caja blanca validan funciones internas y rutas de decisión específicas del código.

### 4.1 Movimientos (lógica interna)

Casos cubiertos:

1. _build_filters con year + month + libro_id: genera rango mensual correcto.
2. _build_filters con solo year: genera rango anual correcto.
3. recompute_saldos: recalcula saldo acumulado en orden fecha,id.

Resultado esperado: cálculo determinístico y correcto de filtros y saldos.

### 4.2 Inventario (lógica interna)

Casos cubiertos:

1. _productos_qs_for_user con rol usuario: retorna solo productos propios.
2. _productos_qs_for_user con rol admin: retorna todos los productos.

Resultado esperado: aislamiento por propietario y privilegio administrativo correctos.

## 5. Ejecución de Pruebas

Comando ejecutado:

PowerShell:

Set-Location "c:/Users/MAURICIO/Desktop/libro fiscal/libro fiscal/libro_fiscal_v2/backend"; $env:DB_ENGINE="sqlite"; & "c:/Users/MAURICIO/Desktop/libro fiscal/libro fiscal/libro_fiscal_v2/.venv/Scripts/python.exe" manage.py test apps.movimientos apps.inventario

Resultado de ejecución:

- 13 pruebas ejecutadas
- 13 pruebas exitosas
- Estado final: OK

## 6. Hallazgos

1. En este proyecto, solicitudes sin credenciales en endpoints protegidos devolvieron 403, no 401.
2. Se ajustaron las expectativas de pruebas para reflejar el comportamiento real del sistema.

## 7. Conclusión

La batería actual valida correctamente:

- Comportamiento externo de endpoints críticos (caja negra).
- Reglas internas clave de filtrado y recálculo de saldos (caja blanca).

Con este conjunto, se reduce riesgo de regresiones en operaciones financieras e inventario.

## 8. Recomendaciones

1. Extender el mismo enfoque a módulos Libros y Usuarios.
2. Agregar pruebas negativas de serializers (valores límite y formatos inválidos).
3. Integrar esta suite en CI para ejecución automática por commit.
