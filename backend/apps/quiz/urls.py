from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuizViewSet, QuestionViewSet,
    TentativeViewSet, ReponseEtudiantViewSet
)

router = DefaultRouter()
router.register(r'quiz', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'tentatives', TentativeViewSet)
router.register(r'reponses', ReponseEtudiantViewSet)

app_name = 'quiz'

urlpatterns = [
    path('', include(router.urls)),
]
