from django.urls import path
from . import views

urlpatterns = [
    path("productos", views.productos_list_create, name="productos-list-create"),
    path("productos/<int:producto_id>", views.producto_detail, name="producto-detail"),
    path("ventas", views.ventas_list_create, name="ventas-list-create"),
    path("ventas/", views.ventas_list_create, name="ventas-list-create-slash"),
    path("test-mail", views.test_mail, name="test-mail"),
]
