"""
URL configuration for Libro Fiscal project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.usuarios.urls")),
    path("api/", include("apps.libros.urls")),
    path("api/", include("apps.movimientos.urls")),
    path("api/", include("apps.dashboard.urls")),
    path("api/", include("apps.exportacion.urls")),
    path("api/", include("apps.auditoria.urls")),
    path("api/", include("apps.inventario.urls")),
    # Serve frontend for all non-API routes
    re_path(r"^(?!api/|admin/).*$", TemplateView.as_view(template_name="index.html")),
]
