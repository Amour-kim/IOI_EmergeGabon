from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departements', views.DepartementViewSet, basename='departement')
router.register(r'cycles', views.CycleViewSet, basename='cycle')
router.register(r'filieres', views.FiliereViewSet, basename='filiere')
router.register(r'ues', views.UEViewSet, basename='ue')
router.register(r'ecues', views.ECUEViewSet, basename='ecue')
router.register(r'programmes', views.ProgrammeViewSet, basename='programme')
router.register(r'seances', views.SeanceViewSet, basename='seance')

app_name = 'pedagogie'

urlpatterns = [
    path('', include(router.urls)),
]
