from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg
from .models import AcademicYear, Semester, Grade, Attendance, Schedule
from .serializers import (
    AcademicYearSerializer, SemesterSerializer,
    GradeSerializer, AttendanceSerializer, ScheduleSerializer
)
from .permissions import IsTeacherOrReadOnly, IsTeacherOrAdmin

class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    filterset_fields = ['is_current']
    search_fields = ['year']
    ordering_fields = ['year', 'start_date']

    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        academic_year = self.get_object()
        academic_year.is_current = True
        academic_year.save()
        return Response({'status': 'academic year set as current'})

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrAdmin]
    filterset_fields = ['academic_year', 'number', 'is_current']
    ordering_fields = ['academic_year', 'number', 'start_date']

    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        semester = self.get_object()
        semester.is_current = True
        semester.save()
        return Response({'status': 'semester set as current'})

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['student', 'course', 'semester']
    search_fields = ['comment']
    ordering_fields = ['created_at', 'score']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == user.Role.TEACHER:
            return Grade.objects.all()
        return Grade.objects.filter(student=user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        user = request.user
        if user.role == user.Role.STUDENT:
            grades = Grade.objects.filter(student=user)
        else:
            grades = Grade.objects.all()

        stats = {
            'average': grades.aggregate(Avg('score'))['score__avg'],
            'total_grades': grades.count(),
        }
        return Response(stats)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['student', 'course', 'date', 'is_present', 'validated']
    ordering_fields = ['date']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == user.Role.TEACHER:
            return Attendance.objects.all()
        return Attendance.objects.filter(student=user)

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        attendance = self.get_object()
        attendance.validated = True
        attendance.save()
        return Response({'status': 'attendance validated'})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        user = request.user
        if user.role == user.Role.STUDENT:
            attendances = Attendance.objects.filter(student=user)
        else:
            attendances = Attendance.objects.all()

        total = attendances.count()
        present = attendances.filter(is_present=True).count()
        
        stats = {
            'total_sessions': total,
            'present': present,
            'absent': total - present,
            'presence_rate': (present / total * 100) if total > 0 else 0
        }
        return Response(stats)

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['course', 'semester', 'day_of_week', 'recurring']
    ordering_fields = ['day_of_week', 'start_time']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == user.Role.TEACHER:
            return Schedule.objects.all()
        return Schedule.objects.filter(
            course__enrollments__student=user,
            course__enrollments__is_active=True
        )
