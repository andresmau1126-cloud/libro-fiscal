from django.urls import path
from . import views

urlpatterns = [
    path("turnos/abrir", views.abrir_turno, name="turnos-abrir"),
    path("turnos/cerrar", views.cerrar_turno, name="turnos-cerrar"),
    path("turnos/reporte", views.turnos_reporte, name="turnos-reporte"),
    path("turnos", views.turnos_list, name="turnos-list"),
]
