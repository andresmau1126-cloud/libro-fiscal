from django.urls import path
from . import views

urlpatterns = [
    path("dashboard", views.dashboard_stats, name="dashboard"),
    path("resumen-anual", views.resumen_anual, name="resumen-anual"),
]
