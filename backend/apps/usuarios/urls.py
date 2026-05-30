from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),
    path("auth/verify-registration-code", views.verify_registration_code, name="auth-verify-registration-code"),
    path("auth/resend-registration-code", views.resend_registration_code, name="auth-resend-registration-code"),
    path("auth/logout/", views.logout, name="logout"),
    path("auth/me/", views.me, name="me"),
    path("auth/request-otp/", views.request_otp, name="request_otp"),
    path("auth/verify-otp/", views.verify_otp, name="verify_otp"),

    # Admin CRUD
    path("auth/usuarios/", views.usuarios_list_create, name="usuarios_list_create"),
    path("auth/usuarios/<int:uid>/", views.usuario_detail, name="usuario_detail"),
]
