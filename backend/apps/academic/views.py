from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from .models import AcademicYear, Semester, Grade, Attendance, Schedule
from .serializers import (
    AcademicYearSerializer, SemesterSerializer,
    GradeSerializer, AttendanceSerializer, ScheduleSerializer
)
from apps.users.permissions import IsTeacherOrReadOnly

class AcademicYearViewSet(viewsets.ModelViewSet):
    """Gestion des années académiques"""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['is_current']
    search_fields = ['year', 'description']
    ordering_fields = ['year', 'start_date']

    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """Définir l'année académique courante"""
        academic_year = self.get_object()
        academic_year.is_current = True
        academic_year.save()
        return Response({'status': 'année académique définie comme courante'})

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Obtenir les statistiques de l'année académique"""
        academic_year = self.get_object()
        stats = {
            'total_students': academic_year.enrollments.values('student').distinct().count(),
            'total_courses': academic_year.courses.count(),
            'average_grade': Grade.objects.filter(
                semester__academic_year=academic_year
            ).aggregate(Avg('score'))['score__avg'],
            'semesters': academic_year.semesters.count(),
            'is_registration_open': academic_year.is_registration_open(),
        }
        return Response(stats)

class SemesterViewSet(viewsets.ModelViewSet):
    """Gestion des semestres"""
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['academic_year', 'number', 'is_current']
    search_fields = ['academic_year__year']
    ordering_fields = ['academic_year', 'number', 'start_date']

    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """Définir le semestre courant"""
        semester = self.get_object()
        semester.is_current = True
        semester.save()
        return Response({'status': 'semestre défini comme courant'})

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Obtenir les statistiques du semestre"""
        semester = self.get_object()
        stats = {
            'total_courses': semester.courses.count(),
            'total_students': semester.enrollments.values('student').distinct().count(),
            'average_grade': Grade.objects.filter(
                semester=semester
            ).aggregate(Avg('score'))['score__avg'],
            'weeks_remaining': semester.get_weeks_remaining(),
            'is_exam_period': semester.is_exam_period(),
        }
        return Response(stats)

class GradeViewSet(viewsets.ModelViewSet):
    """Gestion des notes"""
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['student', 'course', 'semester', 'grade_type']
    search_fields = ['student__email', 'course__title', 'comment']
    ordering_fields = ['graded_at', 'score']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == user.Role.TEACHER:
            return Grade.objects.all()
        return Grade.objects.filter(student=user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtenir les statistiques des notes"""
        user = request.user
        if user.role == user.Role.STUDENT:
            grades = Grade.objects.filter(student=user)
        else:
            course_id = request.query_params.get('course')
            semester_id = request.query_params.get('semester')
            grades = Grade.objects.all()
            if course_id:
                grades = grades.filter(course_id=course_id)
            if semester_id:
                grades = grades.filter(semester_id=semester_id)

        stats = {
            'average': grades.aggregate(Avg('score'))['score__avg'],
            'total_grades': grades.count(),
            'distribution': {
                'très_bien': grades.filter(score__gte=16).count(),
                'bien': grades.filter(score__range=(14, 15.99)).count(),
                'assez_bien': grades.filter(score__range=(12, 13.99)).count(),
                'passable': grades.filter(score__range=(10, 11.99)).count(),
                'insuffisant': grades.filter(score__lt=10).count(),
            }
        }
        return Response(stats)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Créer plusieurs notes en une seule requête"""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        serializer.save(graded_by=self.request.user)

class AttendanceViewSet(viewsets.ModelViewSet):
    """Gestion des présences"""
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['student', 'course', 'date', 'is_present', 'validated']
    search_fields = ['student__email', 'course__title', 'excuse']
    ordering_fields = ['date', 'time_in']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == user.Role.TEACHER:
            return Attendance.objects.all()
        return Attendance.objects.filter(student=user)

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Valider une absence"""
        attendance = self.get_object()
        attendance.validated = True
        attendance.validated_by = request.user
        attendance.save()
        return Response({'status': 'présence validée'})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Obtenir les statistiques de présence"""
        user = request.user
        if user.role == user.Role.STUDENT:
            attendances = Attendance.objects.filter(student=user)
        else:
            course_id = request.query_params.get('course')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            attendances = Attendance.objects.all()
            if course_id:
                attendances = attendances.filter(course_id=course_id)
            if start_date and end_date:
                attendances = attendances.filter(date__range=[start_date, end_date])

        total = attendances.count()
        stats = {
            'total_sessions': total,
            'present': attendances.filter(is_present=True).count(),
            'absent': attendances.filter(is_present=False).count(),
            'late': attendances.filter(is_late=True).count(),
            'excused': attendances.filter(validated=True).count(),
            'presence_rate': (attendances.filter(is_present=True).count() / total * 100) if total > 0 else 0
        }
        return Response(stats)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Créer plusieurs présences en une seule requête"""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        serializer.save()

class ScheduleViewSet(viewsets.ModelViewSet):
    """Gestion des emplois du temps"""
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['course', 'semester', 'day_of_week', 'room', 'is_recurring']
    search_fields = ['course__title', 'room', 'building']
    ordering_fields = ['semester', 'day_of_week', 'start_time']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == user.Role.TEACHER:
            return Schedule.objects.all()
        return Schedule.objects.filter(
            course__enrollments__student=user,
            course__enrollments__is_active=True
        ).distinct()

    @action(detail=False, methods=['get'])
    def conflicts(self, request):
        """Vérifier les conflits d'horaires"""
        semester_id = request.query_params.get('semester')
        room = request.query_params.get('room')
        if not semester_id or not room:
            return Response(
                {'error': 'Les paramètres semester et room sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        conflicts = []
        schedules = Schedule.objects.filter(semester_id=semester_id, room=room)
        for schedule in schedules:
            other_schedules = schedules.exclude(id=schedule.id)
            for other in other_schedules:
                if (
                    schedule.day_of_week == other.day_of_week and
                    schedule.start_time < other.end_time and
                    schedule.end_time > other.start_time
                ):
                    conflicts.append({
                        'schedule1': self.get_serializer(schedule).data,
                        'schedule2': self.get_serializer(other).data
                    })

        return Response(conflicts)

    @action(detail=False, methods=['get'])
    def available_rooms(self, request):
        """Trouver les salles disponibles pour un créneau donné"""
        semester_id = request.query_params.get('semester')
        day_of_week = request.query_params.get('day_of_week')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        capacity = request.query_params.get('capacity')

        if not all([semester_id, day_of_week, start_time, end_time]):
            return Response(
                {'error': 'Tous les paramètres sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Trouver les salles occupées
        busy_rooms = Schedule.objects.filter(
            semester_id=semester_id,
            day_of_week=day_of_week
        ).filter(
            Q(start_time__lt=end_time) &
            Q(end_time__gt=start_time)
        ).values_list('room', flat=True)

        # Filtrer les salles disponibles
        available_rooms = Schedule.objects.exclude(
            room__in=busy_rooms
        ).filter(
            capacity__gte=capacity if capacity else 0
        ).values('room', 'building', 'floor', 'capacity').distinct()

        return Response(available_rooms)
