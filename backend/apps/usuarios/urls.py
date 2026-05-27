from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),  # Login simplificado (opcional)
    path("auth/request-otp/", views.request_otp, name="request_otp"),  # Nuevo: Paso 1
    path("auth/verify-otp/", views.verify_otp, name="verify_otp"),      # Nuevo: Paso 2
    path("auth/logout/", views.logout, name="logout"),
    path("auth/me/", views.me, name="me"),
    
    # Admin CRUD
    path("auth/usuarios/", views.usuarios_list_create, name="usuarios_list_create"),
    path("auth/usuarios/<int:uid>/", views.usuario_detail, name="usuario_detail"),
]
