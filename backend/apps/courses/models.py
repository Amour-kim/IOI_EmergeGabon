from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User, TeacherProfile

class Course(models.Model):
    """Model for courses"""
    title = models.CharField(_('titre'), max_length=200)
    code = models.CharField(_('code'), max_length=20, unique=True)
    description = models.TextField(_('description'))
    credits = models.IntegerField(_('crédits'))
    teachers = models.ManyToManyField(
        TeacherProfile,
        verbose_name=_('enseignants'),
        related_name='teaching_courses'
    )
    prerequisites = models.ManyToManyField(
        'self',
        verbose_name=_('prérequis'),
        blank=True,
        symmetrical=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('cours')
        verbose_name_plural = _('cours')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.title}"

class Module(models.Model):
    """Model for course modules"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name=_('cours')
    )
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    order = models.IntegerField(_('ordre'))

    class Meta:
        verbose_name = _('module')
        verbose_name_plural = _('modules')
        ordering = ['order']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

class Content(models.Model):
    """Model for module content"""
    class ContentType(models.TextChoices):
        VIDEO = 'VIDEO', _('Vidéo')
        DOCUMENT = 'DOCUMENT', _('Document')
        QUIZ = 'QUIZ', _('Quiz')
        ASSIGNMENT = 'ASSIGNMENT', _('Devoir')

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
    file = models.FileField(
        _('fichier'),
        upload_to='course_contents/',
        null=True,
        blank=True
    )
    url = models.URLField(_('URL'), null=True, blank=True)
    description = models.TextField(_('description'))
    order = models.IntegerField(_('ordre'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('contenu')
        verbose_name_plural = _('contenus')
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

class Enrollment(models.Model):
    """Model for course enrollments"""
    student = models.ForeignKey(
        User,
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
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('inscription')
        verbose_name_plural = _('inscriptions')
        unique_together = ['student', 'course']
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title}"
