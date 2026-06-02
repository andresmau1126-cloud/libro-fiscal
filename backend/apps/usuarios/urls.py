from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("register/", views.register, name="register"),
    path("register", views.register, name="register_no_slash"),
    path("login/", views.login, name="login"),
    path("login", views.login, name="login_no_slash"),
    path("verify-registration-code/", views.verify_registration_code, name="auth-verify-registration-code"),
    path("verify-registration-code", views.verify_registration_code, name="auth-verify-registration-code-no-slash"),
    path("resend-registration-code/", views.resend_registration_code, name="auth-resend-registration-code"),
    path("resend-registration-code", views.resend_registration_code, name="auth-resend-registration-code-no-slash"),
    path("logout/", views.logout, name="logout"),
    path("logout", views.logout, name="logout_no_slash"),
    path("me/", views.me, name="me"),
    path("me", views.me, name="me_no_slash"),
    path("request-otp/", views.request_otp, name="request_otp"),
    path("request-otp", views.request_otp, name="request_otp_no_slash"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("verify-otp", views.verify_otp, name="verify_otp_no_slash"),

    # Admin CRUD
    path("usuarios/", views.usuarios_list_create, name="usuarios_list_create"),
    path("usuarios/<int:uid>/", views.usuario_detail, name="usuario_detail"),
]
