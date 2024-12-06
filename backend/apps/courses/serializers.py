from rest_framework import serializers
from django.utils import timezone
from .models import Course, Module, Content, Enrollment
from apps.users.serializers import UserSerializer, TeacherProfileSerializer

class ContentSerializer(serializers.ModelSerializer):
    file_extension = serializers.SerializerMethodField()
    
    class Meta:
        model = Content
        fields = '__all__'
        
    def get_file_extension(self, obj):
        return obj.get_file_extension()

    def validate(self, data):
        """Validation personnalisée pour le contenu"""
        if data['content_type'] == Content.ContentType.VIDEO and not (data.get('file') or data.get('url')):
            raise serializers.ValidationError(
                "Une vidéo doit avoir soit un fichier, soit une URL."
            )
            
        if data['content_type'] == Content.ContentType.LINK and not data.get('url'):
            raise serializers.ValidationError(
                "Un lien externe doit avoir une URL."
            )
            
        if data['content_type'] == Content.ContentType.DOCUMENT and not data.get('file'):
            raise serializers.ValidationError(
                "Un document doit avoir un fichier."
            )
            
        return data

class ModuleSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)
    next_module = serializers.SerializerMethodField()
    previous_module = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = '__all__'
        
    def get_next_module(self, obj):
        next_module = obj.get_next_module()
        if next_module:
            return {'id': next_module.id, 'title': next_module.title}
        return None
        
    def get_previous_module(self, obj):
        prev_module = obj.get_previous_module()
        if prev_module:
            return {'id': prev_module.id, 'title': prev_module.title}
        return None
        
    def get_total_duration(self, obj):
        total = timezone.timedelta()
        for content in obj.contents.all():
            if content.duration:
                total += content.duration
        return str(total)

    def validate_order(self, value):
        """Validation de l'ordre du module"""
        if self.instance:  # En cas de mise à jour
            if Module.objects.filter(
                course=self.instance.course,
                order=value
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                    "Un module avec cet ordre existe déjà dans ce cours."
                )
        return value

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    teachers = TeacherProfileSerializer(many=True, read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
        
    def get_enrollment_count(self, obj):
        return obj.get_current_enrollment_count()
        
    def get_completion_rate(self, obj):
        return obj.get_completion_rate()
        
    def get_is_full(self, obj):
        return obj.is_full()
        
    def get_total_duration(self, obj):
        total = timezone.timedelta()
        for module in obj.modules.all():
            for content in module.contents.all():
                if content.duration:
                    total += content.duration
        return str(total)

    def validate(self, data):
        """Validation personnalisée pour le cours"""
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] and data['end_date']:
                if data['start_date'] >= data['end_date']:
                    raise serializers.ValidationError(
                        "La date de début doit être antérieure à la date de fin."
                    )
                    
        if 'prerequisites' in data:
            if self.instance and self.instance in data['prerequisites']:
                raise serializers.ValidationError(
                    "Un cours ne peut pas être son propre prérequis."
                )
                
        return data

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    days_since_enrollment = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = '__all__'
        read_only_fields = (
            'enrollment_date', 'completion_date',
            'progress', 'last_accessed'
        )
        
    def get_days_since_enrollment(self, obj):
        return (timezone.now() - obj.enrollment_date).days

    def validate(self, data):
        """Validation personnalisée pour l'inscription"""
        course = self.context['course']
        student = self.context['request'].user
        
        if course.is_full():
            raise serializers.ValidationError(
                "Ce cours est complet."
            )
            
        if Enrollment.objects.filter(
            student=student,
            course=course,
            is_active=True
        ).exists():
            raise serializers.ValidationError(
                "Vous êtes déjà inscrit à ce cours."
            )
            
        # Vérifier les prérequis
        prerequisites = course.prerequisites.all()
        for prerequisite in prerequisites:
            if not Enrollment.objects.filter(
                student=student,
                course=prerequisite,
                is_active=True,
                completed=True
            ).exists():
                raise serializers.ValidationError(
                    f"Vous devez d'abord compléter le cours {prerequisite.title}."
                )
                
        return data
