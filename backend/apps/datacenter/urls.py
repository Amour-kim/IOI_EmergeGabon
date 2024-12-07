from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DatacenterViewSet, BibliothequeViewSet,
    DocumentationViewSet, MediathequeViewSet
)

router = DefaultRouter()
router.register(r'datacenters', DatacenterViewSet, basename='datacenter')
router.register(r'bibliotheques', BibliothequeViewSet, basename='bibliotheque')
router.register(r'documentations', DocumentationViewSet, basename='documentation')
router.register(r'mediatheques', MediathequeViewSet, basename='mediatheque')

urlpatterns = [
    path('', include(router.urls)),
]
