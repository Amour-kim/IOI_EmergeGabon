from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Course(models.Model):
    """Modèle pour les cours"""
    title = models.CharField(_('titre'), max_length=200)
    code = models.CharField(_('code'), max_length=20, unique=True)
    description = models.TextField(_('description'))
    credits = models.IntegerField(
        _('crédits'),
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    teachers = models.ManyToManyField(
        'users.TeacherProfile',
        related_name='teaching_courses',
        verbose_name=_('enseignants')
    )
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name=_('prérequis'),
        related_name='is_prerequisite_for'
    )
    capacity = models.PositiveIntegerField(
        _('capacité'),
        default=50,
        validators=[MinValueValidator(1)]
    )
    start_date = models.DateField(_('date de début'), null=True, blank=True)
    end_date = models.DateField(_('date de fin'), null=True, blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    language = models.CharField(
        _('langue'),
        max_length=10,
        choices=[('fr', 'Français'), ('en', 'Anglais')],
        default='fr'
    )
    level = models.CharField(
        _('niveau'),
        max_length=20,
        choices=[
            ('L1', 'Licence 1'),
            ('L2', 'Licence 2'),
            ('L3', 'Licence 3'),
            ('M1', 'Master 1'),
            ('M2', 'Master 2'),
            ('D', 'Doctorat')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('cours')
        verbose_name_plural = _('cours')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['level']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"

    def is_full(self):
        """Vérifier si le cours est complet"""
        return self.enrollments.filter(is_active=True).count() >= self.capacity

    def get_current_enrollment_count(self):
        """Obtenir le nombre d'inscriptions actives"""
        return self.enrollments.filter(is_active=True).count()

    def get_completion_rate(self):
        """Calculer le taux de complétion du cours"""
        total_enrollments = self.enrollments.filter(is_active=True).count()
        if total_enrollments == 0:
            return 0
        completed = self.enrollments.filter(is_active=True, completed=True).count()
        return (completed / total_enrollments) * 100

class Module(models.Model):
    """Modèle pour les modules de cours"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name=_('cours')
    )
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    order = models.PositiveIntegerField(_('ordre'))
    duration = models.DurationField(
        _('durée'),
        null=True,
        blank=True,
        help_text=_('Durée estimée du module')
    )
    is_required = models.BooleanField(_('obligatoire'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('module')
        verbose_name_plural = _('modules')
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    def get_next_module(self):
        """Obtenir le module suivant dans le cours"""
        return Module.objects.filter(
            course=self.course,
            order__gt=self.order
        ).order_by('order').first()

    def get_previous_module(self):
        """Obtenir le module précédent dans le cours"""
        return Module.objects.filter(
            course=self.course,
            order__lt=self.order
        ).order_by('-order').first()

class Content(models.Model):
    """Modèle pour le contenu des modules"""
    class ContentType(models.TextChoices):
        VIDEO = 'VIDEO', _('Vidéo')
        DOCUMENT = 'DOCUMENT', _('Document')
        QUIZ = 'QUIZ', _('Quiz')
        ASSIGNMENT = 'ASSIGNMENT', _('Devoir')
        LINK = 'LINK', _('Lien externe')
        CODE = 'CODE', _('Code source')

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name=_('module')
    )
    title = models.CharField(_('titre'), max_length=200)
    content_type = models.CharField(
        _('type de contenu'),
        max_length=20,
        choices=ContentType.choices
    )
    description = models.TextField(_('description'))
    file = models.FileField(
        _('fichier'),
        upload_to='course_contents/',
        null=True,
        blank=True
    )
    url = models.URLField(_('URL'), null=True, blank=True)
    duration = models.DurationField(
        _('durée'),
        null=True,
        blank=True,
        help_text=_('Durée estimée du contenu')
    )
    order = models.PositiveIntegerField(_('ordre'))
    is_required = models.BooleanField(_('obligatoire'), default=True)
    points = models.PositiveIntegerField(
        _('points'),
        default=0,
        help_text=_('Points attribués pour ce contenu')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('contenu')
        verbose_name_plural = _('contenus')
        ordering = ['module', 'order']
        unique_together = ['module', 'order']
        indexes = [
            models.Index(fields=['module', 'order']),
            models.Index(fields=['content_type']),
        ]

    def __str__(self):
        return f"{self.module.title} - {self.title}"

    def get_file_extension(self):
        """Obtenir l'extension du fichier"""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return None

class Enrollment(models.Model):
    """Modèle pour les inscriptions aux cours"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('étudiant')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('cours')
    )
    enrollment_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(_('actif'), default=True)
    completed = models.BooleanField(_('terminé'), default=False)
    completion_date = models.DateTimeField(
        _('date de fin'),
        null=True,
        blank=True
    )
    progress = models.FloatField(
        _('progression'),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    last_accessed = models.DateTimeField(
        _('dernier accès'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('inscription')
        verbose_name_plural = _('inscriptions')
        unique_together = ['student', 'course']
        ordering = ['-enrollment_date']
        indexes = [
            models.Index(fields=['student', 'course']),
            models.Index(fields=['is_active']),
            models.Index(fields=['completed']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title}"

    def update_progress(self):
        """Mettre à jour la progression de l'étudiant"""
        # TODO: Implémenter la logique de calcul de progression
        pass
