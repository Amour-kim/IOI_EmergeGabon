from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom User model"""
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        TEACHER = 'TEACHER', _('Enseignant')
        STUDENT = 'STUDENT', _('Étudiant')
        STAFF = 'STAFF', _('Personnel')

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_staff_member(self):
        return self.role == self.Role.STAFF

class StudentProfile(models.Model):
    """Profile for students"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    current_semester = models.IntegerField()
    major = models.CharField(max_length=100)

    def __str__(self):
        return f"Profile étudiant de {self.user.get_full_name()}"

class TeacherProfile(models.Model):
    """Profile for teachers"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    hire_date = models.DateField()

    def __str__(self):
        return f"Profile enseignant de {self.user.get_full_name()}"
