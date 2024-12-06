from rest_framework import serializers
from .models import Course, Module, Content, Enrollment
from apps.users.serializers import UserSerializer, TeacherProfileSerializer

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    teachers = TeacherProfileSerializer(many=True, read_only=True)
    prerequisites = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Course.objects.all(),
        required=False
    )

    class Meta:
        model = Course
        fields = '__all__'

    def validate_prerequisites(self, value):
        """
        Check that a course is not a prerequisite for itself
        """
        if self.instance in value:
            raise serializers.ValidationError(
                "Un cours ne peut pas être son propre prérequis."
            )
        return value

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = '__all__'
        read_only_fields = ('enrollment_date', 'completion_date')
