from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EvenementViewSet,
    DocumentViewSet,
    FeedbackViewSet
)

router = DefaultRouter()
router.register(r'evenements', EvenementViewSet, basename='evenement')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')

app_name = 'evenements'

urlpatterns = [
    path('', include(router.urls)),
]
