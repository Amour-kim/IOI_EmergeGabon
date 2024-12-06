from rest_framework import serializers
from django.utils import timezone
from .models import AcademicYear, Semester, Grade, Attendance, Schedule
from apps.users.serializers import UserSerializer
from apps.courses.serializers import CourseSerializer

class AcademicYearSerializer(serializers.ModelSerializer):
    is_registration_open = serializers.BooleanField(read_only=True)
    current_semester = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicYear
        fields = '__all__'
        
    def get_current_semester(self, obj):
        current = obj.get_current_semester()
        if current:
            return SemesterSerializer(current).data
        return None

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin."
            )
            
        if 'registration_start' in data and 'registration_end' in data:
            if data['registration_start'] and data['registration_end']:
                if data['registration_start'] >= data['registration_end']:
                    raise serializers.ValidationError(
                        "La date de début d'inscription doit être antérieure à la date de fin."
                    )
                    
        return data

class SemesterSerializer(serializers.ModelSerializer):
    is_exam_period = serializers.BooleanField(read_only=True)
    weeks_remaining = serializers.IntegerField(source='get_weeks_remaining', read_only=True)
    academic_year = AcademicYearSerializer(read_only=True)
    
    class Meta:
        model = Semester
        fields = '__all__'
        
    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin."
            )
            
        if 'exam_start_date' in data and 'exam_end_date' in data:
            if data['exam_start_date'] and data['exam_end_date']:
                if data['exam_start_date'] >= data['exam_end_date']:
                    raise serializers.ValidationError(
                        "La date de début des examens doit être antérieure à la date de fin."
                    )
                if data['exam_start_date'] < data['start_date']:
                    raise serializers.ValidationError(
                        "La période d'examen ne peut pas commencer avant le semestre."
                    )
                if data['exam_end_date'] > data['end_date']:
                    raise serializers.ValidationError(
                        "La période d'examen ne peut pas finir après le semestre."
                    )
                    
        return data

class GradeSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    semester = SemesterSerializer(read_only=True)
    graded_by = UserSerializer(read_only=True)
    mention = serializers.CharField(read_only=True)
    weighted_score = serializers.DecimalField(
        source='get_weighted_score',
        read_only=True,
        max_digits=5,
        decimal_places=2
    )
    
    class Meta:
        model = Grade
        fields = '__all__'
        
    def validate(self, data):
        if self.context['request'].user.role not in ['ADMIN', 'TEACHER']:
            raise serializers.ValidationError(
                "Seuls les enseignants et administrateurs peuvent noter."
            )
            
        # Vérifier si le semestre est actif
        semester = self.context.get('semester')
        if semester and not semester.is_current:
            raise serializers.ValidationError(
                "Impossible de noter en dehors du semestre actif."
            )
            
        return data

    def create(self, validated_data):
        validated_data['graded_by'] = self.context['request'].user
        return super().create(validated_data)

class AttendanceSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    validated_by = UserSerializer(read_only=True)
    duration = serializers.DurationField(source='get_duration', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'
        
    def validate(self, data):
        if data.get('time_out') and data['time_in'] >= data['time_out']:
            raise serializers.ValidationError(
                "L'heure d'arrivée doit être antérieure à l'heure de sortie."
            )
            
        if data.get('validated') and not self.context['request'].user.role in ['ADMIN', 'TEACHER']:
            raise serializers.ValidationError(
                "Seuls les enseignants et administrateurs peuvent valider les présences."
            )
            
        return data

    def create(self, validated_data):
        if validated_data.get('validated'):
            validated_data['validated_by'] = self.context['request'].user
        return super().create(validated_data)

class ScheduleSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    semester = SemesterSerializer(read_only=True)
    duration = serializers.DurationField(source='get_duration', read_only=True)
    has_conflicts = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Schedule
        fields = '__all__'
        
    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError(
                "L'heure de début doit être antérieure à l'heure de fin."
            )
            
        # Vérifier la capacité de la salle
        if data['capacity'] < data['course'].get_current_enrollment_count():
            raise serializers.ValidationError(
                "La capacité de la salle est insuffisante pour ce cours."
            )
            
        # Vérifier les conflits d'horaires
        instance = self.instance
        if Schedule.objects.filter(
            semester=data['semester'],
            day_of_week=data['day_of_week'],
            room=data['room']
        ).exclude(id=instance.id if instance else None).filter(
            models.Q(
                start_time__lt=data['end_time'],
                end_time__gt=data['start_time']
            )
        ).exists():
            raise serializers.ValidationError(
                "Il y a un conflit d'horaire avec un autre cours."
            )
            
        return data
