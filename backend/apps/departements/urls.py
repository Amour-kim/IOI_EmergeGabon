from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FaculteViewSet,
    DepartementViewSet,
    ProgrammeViewSet,
    CoursViewSet
)

router = DefaultRouter()
router.register(r'facultes', FaculteViewSet, basename='faculte')
router.register(r'departements', DepartementViewSet, basename='departement')
router.register(r'programmes', ProgrammeViewSet, basename='programme')
router.register(r'cours', CoursViewSet, basename='cours')

app_name = 'departements'

urlpatterns = [
    path('', include(router.urls)),
]
