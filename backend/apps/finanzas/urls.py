from django.urls import path
from . import views

urlpatterns = [
    path("stats", views.stats, name="seller-stats"),
    path("expenses", views.expenses, name="expenses"),
    path("expenses/<int:expense_id>", views.expense_detail, name="expense-detail"),
    path("providers", views.providers, name="providers"),
    path("providers/<int:provider_id>", views.provider_detail, name="provider-detail"),
]
