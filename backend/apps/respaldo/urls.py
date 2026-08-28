from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PuntoControlViewSet

router = DefaultRouter()
router.register(r'respaldos', PuntoControlViewSet, basename='punto-control')

urlpatterns = [
    path('', include(router.urls)),
]
