from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommunityViewSet, MembershipRequestViewSet,
    DiscussionViewSet, CommentViewSet,
    TagViewSet, ReportViewSet
)

router = DefaultRouter()
router.register(r'communities', CommunityViewSet, basename='community')
router.register(r'membership-requests', MembershipRequestViewSet, basename='membership-request')
router.register(r'discussions', DiscussionViewSet, basename='discussion')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
