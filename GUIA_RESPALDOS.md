# 📋 GUÍA: Sistema de Copias de Seguridad (Respaldos)

## ¿Qué es?
El sistema de copias de seguridad permite crear y restaurar "puntos de control" de tu aplicación. Esto significa que puedes guardar una copia completa de tu base de datos en un momento específico y restaurarla cuando lo necesites.

## Acceso
- **URL**: `/respaldos` (dentro del panel de administración)
- **Permisos**: Solo administradores pueden acceder
- **Ubicación en menú**: Administración → Copias de Seguridad

## Características Principales

### 1. **Crear Respaldos**
Puedes crear tres tipos de respaldos:
- **Completo**: Base de datos + Configuración (recomendado)
- **Solo Base de Datos**: Solo los datos transaccionales
- **Solo Configuración**: Solo configuraciones del sistema

**Pasos:**
1. Haz clic en "+ Crear Nuevo Respaldo"
2. Completa el formulario:
   - **Nombre**: Identificar tu respaldo (ej: "Respaldo fin de mes")
   - **Descripción**: Notas sobre por qué lo creaste (opcional)
   - **Tipo**: Elige el tipo de respaldo
3. Haz clic en "✓ Crear Respaldo"

### 2. **Ver Estadísticas**
En la parte superior verás:
- **Total de Respaldos**: Cantidad total de puntos de control
- **Completados**: Cuántos se crearon exitosamente
- **Fallidos**: Cuántos tuvieron errores
- **Espacio Utilizado**: Tamaño total de todos los respaldos

### 3. **Restaurar Respaldos**
Recupera tu sistema a un estado anterior.

**Pasos:**
1. Busca el respaldo que deseas restaurar
2. Haz clic en el botón 🔄 (Restaurar)
3. Lee la advertencia y confirma (esto sobrescribirá los datos actuales)
4. El sistema restaurará automáticamente

**Importante:**
- Se crea una copia de seguridad de tu BD actual antes de restaurar
- Si hay error, se revierte automáticamente
- El proceso puede tomar varios segundos

### 4. **Descargar Respaldos**
Descarga un respaldo en tu computadora como archivo `.sql`

**Pasos:**
1. Busca el respaldo deseado
2. Haz clic en el botón ⬇️ (Descargar)
3. El archivo se descargará automáticamente

### 5. **Eliminar Respaldos**
Borra respaldos que ya no necesitas para liberar espacio.

**Pasos:**
1. Busca el respaldo a eliminar
2. Haz clic en el botón 🗑️ (Eliminar)
3. Confirma la eliminación

## Filtros y Búsqueda

Puedes filtrar respaldos por:
- **Tipo**: Completo, Base de Datos, Configuración
- **Estado**: Completado, En Proceso, Fallido

Esto te ayuda a encontrar rápidamente el respaldo que necesitas.

## Estados de Respaldos

| Estado | Significado |
|--------|------------|
| ✅ Completado | Respaldo exitoso y listo para usar |
| ⏳ En Proceso | Se está creando (espera a que termine) |
| ❌ Fallido | Error al crear, no se puede restaurar |

## Información Almacenada

Para cada respaldo se guarda:
- Nombre y descripción
- Tipo de respaldo
- Estado actual
- Fecha de creación
- Usuario que lo creó
- Tamaño del archivo
- Fecha de última restauración
- Usuario que lo restauró
- Historial de restauraciones

## Seguridad y Mejores Prácticas

### ✅ Recomendaciones:
1. **Respaldos regulares**: Crea respaldos semanales o mensuales
2. **Nombres descriptivos**: Usa nombres claros (ej: "Respaldo-2026-08-28")
3. **Respaldos externos**: Descarga respaldos importantes a tu PC
4. **Antes de cambios mayores**: Crea un respaldo antes de actualizaciones
5. **Documentación**: Anota por qué creaste cada respaldo

### ⚠️ Precauciones:
1. **La restauración es destructiva**: Sobrescribe datos actuales
2. **Confirma siempre**: Lee el aviso antes de restaurar
3. **Espacio en servidor**: Los respaldos ocupan espacio
4. **No es backup remoto**: Los respaldos están en el mismo servidor

## Respaldo automático en Render

En producción, el respaldo diario se ejecuta mediante el Cron Job `respaldo-postgres-diario` a las 07:30 UTC. El comando usa `pg_dump` para PostgreSQL, sube un archivo `.dump` a un bucket S3 compatible y elimina los archivos con más de 30 días.

Para activarlo en Render, configura estas variables secretas en el Cron Job:

```text
BACKUP_S3_BUCKET=nombre-del-bucket
BACKUP_S3_ACCESS_KEY_ID=...
BACKUP_S3_SECRET_ACCESS_KEY=...
```

También puedes definir:

```text
BACKUP_S3_REGION=us-east-1
BACKUP_S3_ENDPOINT_URL=https://...   # Necesario para R2, MinIO u otro S3 compatible
BACKUP_S3_PREFIX=libro-fiscal
```

`BACKUP_S3_ENDPOINT_URL` se deja vacío cuando se usa Amazon S3. Las credenciales deben tener permiso para listar, subir y eliminar objetos del bucket. Render usa UTC; para otra hora hay que cambiar el horario cron.

## Casos de Uso

### Caso 1: Error en datos
```
1. Identificas que algo salió mal
2. Creas un respaldo actual como referencia
3. Restauras un respaldo anterior al error
4. Verificas que todo está bien
```

### Caso 2: Mantenimiento programado
```
1. Creas respaldo pre-mantenimiento
2. Realizas las tareas de actualización
3. Pruebas la aplicación
4. Si hay problemas, restauras el respaldo anterior
```

### Caso 3: Auditoría
```
1. Descargas un respaldo específico
2. Analizas los datos con herramientas externas
3. Verificas la integridad de datos históricos
```

## Preguntas Frecuentes

### ¿Cuánto tardan los respaldos?
Depende del tamaño de tu base de datos. Generalmente:
- BD pequeña: 1-5 segundos
- BD mediana: 5-30 segundos
- BD grande: 30-120 segundos

### ¿Se puede restaurar parcialmente?
No, la restauración reemplaza todo. Opción: descargar el SQL y modificarlo manualmente.

### ¿Dónde se guardan?
En el directorio `/backend/respaldos/` del servidor.

### ¿Puedo restaurar remotamente?
Sí, los respaldos descargados son archivos SQL estándar que puedes importar en cualquier SQLite.

### ¿Hay límite de respaldos?
No hay límite, pero considera el espacio disponible.

## Troubleshooting

### Error: "Archivo de respaldo no encontrado"
- El archivo se eliminó del servidor
- Solución: Elimina el respaldo de la lista y crea uno nuevo

### Error durante restauración
- Se revierte automáticamente a la copia anterior
- Revisa los logs del servidor para detalles
- Intenta de nuevo o contacta al soporte

### Respaldo en estado "En Proceso" forever
- El proceso se quedó colgado
- Solución: Elimina y crea uno nuevo

## API Endpoints

Para desarrolladores:

```
GET    /api/respaldos/                    # Listar respaldos
POST   /api/respaldos/crear_respaldo/     # Crear respaldo
POST   /api/respaldos/{id}/restaurar/     # Restaurar
GET    /api/respaldos/{id}/descargar/     # Descargar
DELETE /api/respaldos/{id}/                # Eliminar
GET    /api/respaldos/estadisticas/       # Estadísticas
```

---

**Última actualización**: 2026-08-28
**Versión**: 1.0
**Autor**: Sistema de Gestión de Libro Fiscal
