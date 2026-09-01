# 🚀 GUÍA RÁPIDA DE INICIO - Inventario Centralizado en Tiempo Real

## Instalación Local (Desarrollo)

### 1. Activar Entorno Virtual
```bash
cd "c:\Users\MAURICIO\Desktop\libro fiscal\libro fiscal\libro_fiscal_v2"
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar Dependencias
```bash
cd backend
pip install -r requirements.txt
```

### 3. Aplicar Migraciones
```bash
python manage.py migrate
```

### 4. Crear Superusuario (si no existe)
```bash
python manage.py createsuperuser
# Email: admin@test.com
# Nombre: Administrador
# Contraseña: admin123
# Rol: admin
```

### 5. Iniciar Servidor

**Opción A: Con Daphne (WebSocket completo)**
```bash
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```

**Opción B: Con servidor development Django**
```bash
python manage.py runserver
```

### 6. Acceder
- 🌐 API: http://localhost:8000/api/
- 🔐 Admin: http://localhost:8000/admin/
- 📡 WebSocket: ws://localhost:8000/ws/inventario/

---

## Endpoints Disponibles (API REST)

### Inventario Centralizado
```bash
# Ver inventario centralizado compartido
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/inventario-centralizado/

# Ver solo productos críticos
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/inventario-centralizado/?critico=1"

# Resumen general del inventario
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/resumen/inventario/
```

### Historial de Ventas
```bash
# Ver tu historial de ventas
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/historial/ventas/

# Ver últimos 90 días
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/historial/ventas/?dias=90"

# Ver historial de otro vendedor (solo gerente/admin)
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/historial/ventas/?vendedor_id=2"
```

### Historial de Inventario
```bash
# Ver movimientos de un producto
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/historial/inventario/1/

# Últimos 7 días
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/historial/inventario/1/?dias=7"
```

### Estadísticas
```bash
# Tus estadísticas personales
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/estadisticas/vendedor/

# Resumen diario de ventas
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/resumen/ventas-diarias/

# Fecha específica
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/resumen/ventas-diarias/?fecha=2024-01-15"
```

---

## Pruebas con Python

### Crear Datos de Prueba
```python
from django.contrib.auth import get_user_model
from apps.inventario.models import Producto
from decimal import Decimal

Usuario = get_user_model()

# Crear vendedor
vendedor = Usuario.objects.create_user(
    email="vendedor@test.com",
    nombre="Vendedor Prueba",
    password="test123",
    rol="vendedor"
)

# Crear producto
producto = Producto.objects.create(
    nombre="Arroz Premium",
    propietario=vendedor,
    categoria="Alimentos",
    stock_actual=Decimal("100"),
    stock_minimo=Decimal("10"),
    costo_unitario=Decimal("1.50"),
    precio_venta=Decimal("2.50"),
)

print(f"✓ Producto creado: {producto.nombre}")
```

### Registrar Movimiento
```python
from apps.inventario.services import InventarioCentralizadoService
from decimal import Decimal

# Registrar entrada de stock
historial = InventarioCentralizadoService.registrar_movimiento_inventario(
    producto=producto,
    tipo_movimiento="entrada",
    cantidad_movida=Decimal("50"),
    usuario=vendedor,
    razon="Compra a proveedor"
)

print(f"✓ Movimiento registrado: {historial.cantidad_movida}")
```

### Crear Venta
```python
from apps.inventario.services import VentasService
from decimal import Decimal

venta = VentasService.crear_venta_con_historial(
    cliente="Cliente Test",
    medio_pago="efectivo",
    detalles_venta=[
        {"producto_id": producto.id, "cantidad": Decimal("5")}
    ],
    vendedor=vendedor,
    dispositivo="Test Script"
)

print(f"✓ Venta creada: #{venta.id} - ${venta.total}")
```

### Ver Estadísticas
```python
estadisticas = InventarioCentralizadoService.obtener_estadisticas_vendedor(vendedor.id)
print(f"Ventas hoy: {estadisticas['cantidad_ventas_hoy']}")
print(f"Monto: ${estadisticas['monto_vendido_hoy']:.2f}")
print(f"Ganancia: ${estadisticas['ganancia_hoy']:.2f}")
```

---

## Pruebas con WebSocket (JavaScript)

### Conectar a WebSocket
```javascript
// Conectar al inventario centralizado
const socket = new WebSocket(
  `ws://${window.location.host}/ws/inventario/`
);

// Cuando se conecta
socket.onopen = (event) => {
  console.log('✓ Conectado al inventario centralizado');
  
  // Solicitar estado inicial
  socket.send(JSON.stringify({ tipo: 'request_estado' }));
};

// Recibir mensajes
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Mensaje recibido:', data);
  
  if (data.tipo === 'inventario_actualizado') {
    console.log(`Stock actualizado: ${data.data.producto_id}`);
  } else if (data.tipo === 'venta_registrada') {
    console.log(`Nueva venta: #${data.data.venta_id}`);
  } else if (data.tipo === 'stock_bajo') {
    console.log(`⚠️ ${data.mensaje}`);
  }
};

// Enviar ping
setInterval(() => {
  socket.send(JSON.stringify({ tipo: 'ping' }));
}, 30000);
```

### Conectar a Notificaciones
```javascript
const notifSocket = new WebSocket(
  `ws://${window.location.host}/ws/notificaciones/`
);

notifSocket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.tipo === 'stock_bajo') {
    // Mostrar alerta
    alert(`⚠️ ${data.mensaje}`);
  } else if (data.tipo === 'alerta') {
    console.log(`[${data.nivel}] ${data.titulo}: ${data.mensaje}`);
  }
};
```

---

## Flujo de Uso Típico

### Vendedor Realizando una Venta

```
1. Vendedor inicia sesión
   └─ Se conecta automáticamente a WebSocket

2. Vendedor crea una venta
   POST /api/ventas/
   └─ Sistema registra:
      ├─ Venta
      ├─ DetalleVenta
      ├─ HistorialInventario (movimiento)
      ├─ HistorialVentas (con métricas)
      └─ Notifica a todos vía WebSocket

3. Vendedor ve estadísticas personales
   GET /api/estadisticas/vendedor/
   └─ Ve: ventas hoy, ganancia, margen

4. Gerente ve todas las ventas
   GET /api/historial/ventas/
   └─ Ve historial de TODOS los vendedores

5. Sistema notifica si stock es crítico
   WebSocket: stock_bajo
   └─ Alerta a gerentes y admin
```

---

## Troubleshooting

### WebSocket no conecta
```bash
# Verificar que Daphne está corriendo
# Y que Redis está disponible (en producción)

# En desarrollo, verificar en logs:
# "User ... conectado a inventario centralizado"
```

### Migraciones no se aplican
```bash
# Verificar estatus
python manage.py showmigrations inventario

# Aplicar forzadamente
python manage.py migrate inventario --force
```

### Errores de permisos
```bash
# Verificar rol del usuario
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> Usuario = get_user_model()
>>> u = Usuario.objects.get(email="user@test.com")
>>> print(u.rol)
```

### Ver logs de errores
```bash
# En servidor de desarrollo
# Los errores aparecen en la consola

# En Render, ver en:
# Dashboard → Servicio → Logs
```

---

## Comandos Útiles

### Limpiar caché
```bash
python manage.py clear_cache
```

### Ver tablas de inventario
```bash
python manage.py dbshell
```

### Resetear datos de prueba
```bash
python manage.py flush  # ⚠️ Borra TODO
```

### Generar reporte
```bash
python manage.py shell
>>> from apps.inventario.services import InventarioCentralizadoService
>>> resumen = InventarioCentralizadoService.obtener_resumen_inventario_hoy()
>>> print(resumen)
```

---

## Documentación Completa

Ver archivos:
- 📖 `SISTEMA_INVENTARIO_CENTRALIZADO_RESUMEN.md` - Descripción completa del sistema
- 📖 `DEPLOY_RENDER_INVENTARIO_CENTRALIZADO.md` - Guía de deployment en Render

---

## ¿Preguntas Frecuentes?

**P: ¿Por qué dos vendedores ven diferente inventario?**
R: El `EstadoInventarioCentralizado` es compartido. Si ven diferente, refresca la página o reconecta WebSocket.

**P: ¿Cómo veo el historial de un producto específico?**
R: `GET /api/historial/inventario/<producto_id>/`

**P: ¿Puedo exportar historial de ventas?**
R: Sí, desde el endpoint `/api/historial/ventas/` (se puede exportar a CSV desde el frontend)

**P: ¿Qué pasa si se cae el servidor?**
R: Las ventas se guardan en BD. Al reconectar, se sincroniza automáticamente.

**P: ¿Se puede usar sin WebSocket?**
R: Sí, los endpoints REST funcionan sin WebSocket. El WebSocket es solo para notificaciones en tiempo real.

---

## 🎯 Resumen Final

✅ Sistema totalmente implementado  
✅ Inventario sincronizado en tiempo real  
✅ Historial detallado de todas las transacciones  
✅ Estadísticas consolidadas por vendedor  
✅ Listo para producción en Render  

¡Cualquier pregunta, consulta la documentación o los logs! 🚀
