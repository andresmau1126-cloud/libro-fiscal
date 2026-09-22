from django.urls import path
from . import views

urlpatterns = [
    path("turnos/abrir", views.abrir_turno, name="turnos-abrir"),
    path("turnos/cerrar", views.cerrar_turno, name="turnos-cerrar"),
    path("turnos/reporte", views.turnos_reporte, name="turnos-reporte"),
    path("turnos/vendedores", views.turnos_vendedores, name="turnos-vendedores"),
    path("turnos/<int:turno_id>/horas", views.editar_horas_turno, name="turnos-editar-horas"),
    path("turnos", views.turnos_list, name="turnos-list"),
]
