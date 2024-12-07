from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TuteurViewSet,
    SeanceTutoratViewSet,
    InscriptionViewSet,
    EvaluationViewSet,
    SupportViewSet
)

router = DefaultRouter()
router.register(r'tuteurs', TuteurViewSet, basename='tuteur')
router.register(r'seances', SeanceTutoratViewSet, basename='seance')
router.register(r'inscriptions', InscriptionViewSet, basename='inscription')
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')
router.register(r'supports', SupportViewSet, basename='support')

app_name = 'tutorat'

urlpatterns = [
    path('', include(router.urls)),
]
