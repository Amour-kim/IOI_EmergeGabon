from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StudentProfile, TeacherProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                 'role', 'phone_number', 'date_of_birth', 'address',
                 'profile_picture')
        read_only_fields = ('id',)

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'first_name',
                 'last_name', 'role', 'phone_number', 'date_of_birth',
                 'address', 'profile_picture')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ('id', 'user', 'student_id', 'enrollment_date',
                 'current_semester', 'major')
        read_only_fields = ('id',)

class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ('id', 'user', 'employee_id', 'department',
                 'specialization', 'hire_date')
        read_only_fields = ('id',)
