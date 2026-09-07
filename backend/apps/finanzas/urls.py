from django.urls import path
from . import views

urlpatterns = [
    path("stats", views.stats, name="seller-stats"),
    path("expenses", views.expenses, name="expenses"),
    path("providers", views.providers, name="providers"),
]
