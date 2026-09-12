"""
URL configuration for Libro Fiscal project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.http import FileResponse, JsonResponse, Http404
from pathlib import Path
from apps.inventario.views import test_mail_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("test-mail", test_mail_page, name="test-mail-page"),
    path("test-mail/", test_mail_page, name="test-mail-page-slash"),
    # Health check endpoint for uptime/monitoring
    path("healthz/", lambda request: JsonResponse({"status": "ok"})),
    path("docs/<str:filename>", lambda request, filename: serve_manual(filename)),
    path("api/auth/", include("apps.usuarios.urls")),
    path("api/", include("apps.libros.urls")),
    path("api/", include("apps.movimientos.urls")),
    path("api/", include("apps.dashboard.urls")),
    path("api/", include("apps.exportacion.urls")),
    path("api/", include("apps.auditoria.urls")),
    path("api/", include("apps.inventario.urls")),
    path("api/", include("apps.respaldo.urls")),
    path("api/", include("apps.finanzas.urls")),
    # Serve frontend for all non-API routes
    re_path(r"^(?!api/|admin/).*$", TemplateView.as_view(template_name="index.html")),
]


def serve_manual(filename):
    if filename not in {"manual_usuario.md", "manual_tecnico.md"}:
        raise Http404
    path = Path(__file__).resolve().parents[2] / "docs" / filename
    if not path.exists():
        raise Http404
    return FileResponse(path.open("rb"), content_type="text/markdown")
