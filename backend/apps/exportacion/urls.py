from django.urls import path
from . import views

urlpatterns = [
    path("export", views.export_excel, name="export-excel"),
]
