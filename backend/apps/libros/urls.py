from django.urls import path
from . import views

urlpatterns = [
    path("libros", views.libros_list_create, name="libros-list-create"),
    path("libros/<int:libro_id>", views.libro_detail, name="libro-detail"),
]
