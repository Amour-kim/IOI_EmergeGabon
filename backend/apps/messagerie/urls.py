from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(
    r'configurations',
    views.ConfigurationEmailViewSet,
    basename='configuration-email'
)
router.register(
    r'comptes',
    views.CompteEmailViewSet,
    basename='compte-email'
)
router.register(
    r'alias',
    views.AliasViewSet,
    basename='alias'
)
router.register(
    r'listes',
    views.ListeDiffusionViewSet,
    basename='liste-diffusion'
)

app_name = 'messagerie'

urlpatterns = [
    path('', include(router.urls)),
]
