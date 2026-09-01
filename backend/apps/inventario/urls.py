from django.urls import path
from . import views

urlpatterns = [
    path("productos", views.productos_list_create, name="productos-list-create"),
    path("productos/<int:producto_id>", views.producto_detail, name="producto-detail"),
    path("ventas", views.ventas_list_create, name="ventas-list-create"),
    path("ventas/", views.ventas_list_create, name="ventas-list-create-slash"),
    path("ventas/<int:venta_id>", views.venta_delete, name="venta-delete"),
    path("test-mail", views.test_mail, name="test-mail"),
    path("alertas-inventario", views.enviar_alertas_inventario_manual, name="alertas-inventario"),
    path("scheduler/start", views.scheduler_alertas_start, name="scheduler-start"),
    path("scheduler/status", views.scheduler_alertas_status, name="scheduler-status"),
    path("scheduler/stop", views.scheduler_alertas_stop, name="scheduler-stop"),
    
    # Endpoints para inventario centralizado y rastreo
    path("inventario-centralizado", views.inventario_centralizado_list, name="inventario-centralizado"),
    path("historial/inventario/<int:producto_id>", views.historial_inventario_producto, name="historial-inventario-producto"),
    path("historial/ventas", views.historial_ventas_vendedor, name="historial-ventas"),
    path("estadisticas/vendedor", views.estadisticas_vendedor, name="estadisticas-vendedor"),
    path("resumen/ventas-diarias", views.resumen_ventas_diarias, name="resumen-ventas-diarias"),
    path("resumen/inventario", views.resumen_inventario_actual, name="resumen-inventario"),
    path("productos/criticos", views.productos_criticos, name="productos-criticos"),
    
    # Endpoints para monitoreo de turnos
    path("monitoreo/turnos-hoy", views.monitoreo_turnos_hoy, name="monitoreo-turnos-hoy"),
    path("reportes/turnos", views.reportes_turnos, name="reportes-turnos"),
]
