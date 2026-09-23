from django.urls import path

from . import views


urlpatterns = [
    path("clientes", views.clientes_list_create, name="clientes-list-create"),
    path("clientes/<int:cliente_id>", views.cliente_detail, name="cliente-detail"),
]
