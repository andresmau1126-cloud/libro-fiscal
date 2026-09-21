from django.urls import path
from . import views

urlpatterns = [
    path("stats", views.stats, name="seller-stats"),
    path("expenses", views.expenses, name="expenses"),
    path("expenses/<int:expense_id>", views.expense_detail, name="expense-detail"),
    path("expenses/<int:expense_id>/receipt", views.expense_receipt, name="expense-receipt"),
    path("providers", views.providers, name="providers"),
    path("providers/<int:provider_id>", views.provider_detail, name="provider-detail"),
    path("suppliers", views.providers, name="suppliers"),
    path("suppliers/<int:provider_id>", views.provider_detail, name="supplier-detail"),
]
