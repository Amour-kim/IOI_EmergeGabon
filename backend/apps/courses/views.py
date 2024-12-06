from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Course, Module, Content, Enrollment
from .serializers import (
    CourseSerializer, ModuleSerializer,
    ContentSerializer, EnrollmentSerializer
)
from .permissions import IsTeacherOrReadOnly, IsEnrolledOrTeacher

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['teachers', 'credits']
    search_fields = ['title', 'code', 'description']
    ordering_fields = ['created_at', 'title']

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        course = self.get_object()
        user = request.user
        
        if Enrollment.objects.filter(student=user, course=course).exists():
            return Response(
                {"detail": "Déjà inscrit à ce cours."},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment = Enrollment.objects.create(student=user, course=course)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        course = self.get_object()
        try:
            enrollment = Enrollment.objects.get(
                student=request.user,
                course=course,
                is_active=True
            )
            enrollment.completed = True
            enrollment.completion_date = timezone.now()
            enrollment.save()
            return Response({"detail": "Cours marqué comme terminé."})
        except Enrollment.DoesNotExist:
            return Response(
                {"detail": "Inscription non trouvée."},
                status=status.HTTP_404_NOT_FOUND
            )

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['course']
    search_fields = ['title', 'description']
    ordering_fields = ['order']

class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    filterset_fields = ['module', 'content_type']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'created_at']

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsEnrolledOrTeacher]
    filterset_fields = ['course', 'is_active', 'completed']
    ordering_fields = ['enrollment_date', 'completion_date']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == user.Role.TEACHER:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=user)
