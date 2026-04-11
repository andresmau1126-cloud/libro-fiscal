from django.urls import path
from . import views

urlpatterns = [
    path("auditoria", views.auditoria_list, name="auditoria-list"),
]
