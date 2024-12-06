from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcademicYearViewSet, SemesterViewSet,
    GradeViewSet, AttendanceViewSet, ScheduleViewSet
)

router = DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'semesters', SemesterViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'schedules', ScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
