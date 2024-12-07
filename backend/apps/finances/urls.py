from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FraisScolariteViewSet,
    PaiementViewSet,
    FactureViewSet,
    RemboursementDemandeViewSet
)

router = DefaultRouter()
router.register(r'frais', FraisScolariteViewSet, basename='frais')
router.register(r'paiements', PaiementViewSet, basename='paiement')
router.register(r'factures', FactureViewSet, basename='facture')
router.register(r'remboursements', RemboursementDemandeViewSet, basename='remboursement')

app_name = 'finances'

urlpatterns = [
    path('', include(router.urls)),
]
