from django.urls import path
from . import views

urlpatterns = [
    path("auditoria", views.auditoria_list, name="auditoria-list"),
    path("auditoria/clear", views.auditoria_clear, name="auditoria-clear"),
    path("auditoria/<int:pk>", views.auditoria_delete, name="auditoria-delete"),
]
