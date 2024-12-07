from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DossierInscriptionViewSet, DocumentViewSet, CertificatViewSet, documents

router = DefaultRouter()
router.register(r'dossiers', DossierInscriptionViewSet, basename='dossier')
router.register(r'documents', documents.DocumentViewSet, basename='documents')
router.register(r'certificats', CertificatViewSet, basename='certificat')

app_name = 'inscriptions'

urlpatterns = [
    path('', include(router.urls)),
    path(
        'verifier/<str:numero>/',
        documents.DocumentViewSet.as_view({'get': 'verifier'}),
        name='verifier-certificat'
    ),
]
