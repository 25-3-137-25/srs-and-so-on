from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'equipment', views.EquipmentViewSet, basename='equipment')
router.register(r'requests', views.EquipmentRequestViewSet, basename='requests')

urlpatterns = [
    path('', include(router.urls)),
]