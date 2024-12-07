from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategorieViewSet,
    RessourceViewSet,
    EvaluationViewSet,
    TelechargementViewSet,
    CollectionViewSet
)

router = DefaultRouter()
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'ressources', RessourceViewSet, basename='ressource')
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')
router.register(r'telechargements', TelechargementViewSet, basename='telechargement')
router.register(r'collections', CollectionViewSet, basename='collection')

app_name = 'bibliotheque'

urlpatterns = [
    path('', include(router.urls)),
]
