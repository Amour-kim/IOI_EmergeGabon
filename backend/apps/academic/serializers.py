from rest_framework import serializers
from .models import AcademicYear, Semester, Grade, Attendance, Schedule
from apps.users.serializers import UserSerializer
from apps.courses.serializers import CourseSerializer

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'

class SemesterSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        write_only=True,
        source='academic_year'
    )

    class Meta:
        model = Semester
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    semester = SemesterSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='student'
    )
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        write_only=True,
        source='course'
    )
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(),
        write_only=True,
        source='semester'
    )

    class Meta:
        model = Grade
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='student'
    )
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        write_only=True,
        source='course'
    )

    class Meta:
        model = Attendance
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    semester = SemesterSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        write_only=True,
        source='course'
    )
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(),
        write_only=True,
        source='semester'
    )
    day_of_week_display = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True
    )

    class Meta:
        model = Schedule
        fields = '__all__'

    def validate(self, data):
        """
        Check that start_time is before end_time
        """
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError(
                "L'heure de début doit être antérieure à l'heure de fin."
            )
        return data
