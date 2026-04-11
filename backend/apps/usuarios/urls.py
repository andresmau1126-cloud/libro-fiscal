from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("register", views.register, name="auth-register"),
    path("login", views.login, name="auth-login"),
    path("logout", views.logout, name="auth-logout"),
    path("me", views.me, name="auth-me"),
    # Admin CRUD
    path("usuarios/", views.usuarios_list_create, name="usuarios-list-create"),
    path("usuarios/<int:uid>", views.usuario_detail, name="usuario-detail"),
]
