from django.urls import path
from . import views

urlpatterns = [
    path("productos", views.productos_list_create, name="productos-list-create"),
    path("productos/<int:producto_id>", views.producto_detail, name="producto-detail"),
    path("ventas", views.ventas_list_create, name="ventas-list-create"),
    path("ventas/", views.ventas_list_create, name="ventas-list-create-slash"),
    path("test-mail", views.test_mail, name="test-mail"),
    path("alertas-inventario", views.enviar_alertas_inventario_manual, name="alertas-inventario"),
    path("scheduler/start", views.scheduler_alertas_start, name="scheduler-start"),
    path("scheduler/status", views.scheduler_alertas_status, name="scheduler-status"),
    path("scheduler/stop", views.scheduler_alertas_stop, name="scheduler-stop"),
]
