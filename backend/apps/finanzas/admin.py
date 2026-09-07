from django.contrib import admin
from .models import Expense, Provider, SellerStats

admin.site.register((Expense, Provider, SellerStats))
