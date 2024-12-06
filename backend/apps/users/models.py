from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Modèle utilisateur personnalisé"""
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        TEACHER = 'TEACHER', _('Enseignant')
        STUDENT = 'STUDENT', _('Étudiant')
        STAFF = 'STAFF', _('Personnel')

    email = models.EmailField(_('adresse email'), unique=True)
    role = models.CharField(
        _('rôle'),
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )
    phone_number = models.CharField(_('numéro de téléphone'), max_length=20, blank=True)
    date_of_birth = models.DateField(_('date de naissance'), null=True, blank=True)
    address = models.TextField(_('adresse'), blank=True)
    profile_picture = models.ImageField(
        _('photo de profil'),
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    last_login_ip = models.GenericIPAddressField(
        _('dernière IP de connexion'),
        null=True,
        blank=True
    )
    failed_login_attempts = models.PositiveIntegerField(
        _('tentatives de connexion échouées'),
        default=0
    )
    account_locked_until = models.DateTimeField(
        _('compte bloqué jusqu\'à'),
        null=True,
        blank=True
    )
    must_change_password = models.BooleanField(
        _('doit changer le mot de passe'),
        default=False
    )
    password_changed_at = models.DateTimeField(
        _('mot de passe changé le'),
        null=True,
        blank=True
    )
    two_factor_enabled = models.BooleanField(
        _('authentification à deux facteurs activée'),
        default=False
    )
    two_factor_secret = models.CharField(
        max_length=32,
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')

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

    def lock_account(self, duration_minutes=30):
        """Verrouiller le compte temporairement"""
        from django.utils import timezone
        from datetime import timedelta
        
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save()

    def check_password_expiry(self, max_days=90):
        """Vérifier si le mot de passe a expiré"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.password_changed_at:
            return True
            
        expiry_date = self.password_changed_at + timedelta(days=max_days)
        return timezone.now() > expiry_date

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
