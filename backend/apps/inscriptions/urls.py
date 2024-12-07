from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DossierInscriptionViewSet, DocumentViewSet, CertificatViewSet

router = DefaultRouter()
router.register(r'dossiers', DossierInscriptionViewSet, basename='dossier')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'certificats', CertificatViewSet, basename='certificat')

app_name = 'inscriptions'

urlpatterns = [
    path('', include(router.urls)),
]
