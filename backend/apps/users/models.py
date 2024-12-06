from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superuser doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        TEACHER = 'TEACHER', _('Enseignant')
        STUDENT = 'STUDENT', _('Étudiant')

    email = models.EmailField(_('adresse email'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_('rôle')
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        verbose_name=_('numéro de téléphone')
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        verbose_name=_('photo de profil')
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('date de naissance')
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('adresse')
    )
    bio = models.TextField(
        blank=True,
        verbose_name=_('biographie')
    )
    
    # Champs de sécurité
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('tentatives de connexion échouées')
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('dernière tentative échouée')
    )
    account_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('compte verrouillé jusqu\'à')
    )
    password_changed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('dernier changement de mot de passe')
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        verbose_name=_('authentification à deux facteurs activée')
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('dernière IP de connexion')
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    def increment_failed_login(self):
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        if self.failed_login_attempts >= 5:  # Verrouillage après 5 tentatives
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()

    def reset_failed_login(self):
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.account_locked_until = None
        self.save()

    def is_account_locked(self):
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        return False

    def should_change_password(self):
        # Demander le changement de mot de passe après 90 jours
        password_age = timezone.now() - self.password_changed_at
        return password_age.days >= 90

class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name=_('utilisateur')
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('numéro étudiant')
    )
    enrollment_date = models.DateField(
        verbose_name=_('date d\'inscription')
    )
    current_semester = models.PositiveIntegerField(
        verbose_name=_('semestre actuel')
    )
    major = models.CharField(
        max_length=100,
        verbose_name=_('filière')
    )
    gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('moyenne générale')
    )

    class Meta:
        verbose_name = _('profil étudiant')
        verbose_name_plural = _('profils étudiants')

    def __str__(self):
        return f"Profil étudiant de {self.user.get_full_name()}"

class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name=_('utilisateur')
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('numéro employé')
    )
    department = models.CharField(
        max_length=100,
        verbose_name=_('département')
    )
    specialization = models.CharField(
        max_length=200,
        verbose_name=_('spécialisation')
    )
    hire_date = models.DateField(
        verbose_name=_('date d\'embauche')
    )
    office_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('bureau')
    )
    office_hours = models.TextField(
        blank=True,
        verbose_name=_('heures de bureau')
    )

    class Meta:
        verbose_name = _('profil enseignant')
        verbose_name_plural = _('profils enseignants')

    def __str__(self):
        return f"Profil enseignant de {self.user.get_full_name()}"
