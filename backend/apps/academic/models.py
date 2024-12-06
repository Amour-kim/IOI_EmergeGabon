from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User
from apps.courses.models import Course

class AcademicYear(models.Model):
    """Model for academic years"""
    year = models.CharField(_('année'), max_length=9)  # Format: 2023-2024
    start_date = models.DateField(_('date de début'))
    end_date = models.DateField(_('date de fin'))
    is_current = models.BooleanField(_('année en cours'), default=False)

    class Meta:
        verbose_name = _('année académique')
        verbose_name_plural = _('années académiques')
        ordering = ['-year']

    def __str__(self):
        return self.year

    def save(self, *args, **kwargs):
        if self.is_current:
            # Set is_current=False for all other instances
            AcademicYear.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

class Semester(models.Model):
    """Model for semesters"""
    class SemesterNumber(models.IntegerChoices):
        FIRST = 1, _('Premier semestre')
        SECOND = 2, _('Deuxième semestre')

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='semesters',
        verbose_name=_('année académique')
    )
    number = models.IntegerField(
        _('numéro'),
        choices=SemesterNumber.choices
    )
    start_date = models.DateField(_('date de début'))
    end_date = models.DateField(_('date de fin'))
    is_current = models.BooleanField(_('semestre en cours'), default=False)

    class Meta:
        verbose_name = _('semestre')
        verbose_name_plural = _('semestres')
        unique_together = ['academic_year', 'number']
        ordering = ['academic_year', 'number']

    def __str__(self):
        return f"{self.academic_year} - Semestre {self.number}"

    def save(self, *args, **kwargs):
        if self.is_current:
            # Set is_current=False for all other instances
            Semester.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

class Grade(models.Model):
    """Model for student grades"""
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name=_('étudiant')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name=_('cours')
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name=_('semestre')
    )
    score = models.DecimalField(
        _('note'),
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20)
        ]
    )
    comment = models.TextField(_('commentaire'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')
        unique_together = ['student', 'course', 'semester']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title} - {self.score}/20"

class Attendance(models.Model):
    """Model for student attendance"""
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('étudiant')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('cours')
    )
    date = models.DateField(_('date'))
    is_present = models.BooleanField(_('présent'), default=False)
    excuse = models.TextField(_('justification'), blank=True)
    validated = models.BooleanField(_('validé'), default=False)

    class Meta:
        verbose_name = _('présence')
        verbose_name_plural = _('présences')
        unique_together = ['student', 'course', 'date']
        ordering = ['-date']

    def __str__(self):
        status = _('Présent') if self.is_present else _('Absent')
        return f"{self.student.get_full_name()} - {self.course.title} - {self.date} - {status}"

class Schedule(models.Model):
    """Model for course schedules"""
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, _('Lundi')
        TUESDAY = 2, _('Mardi')
        WEDNESDAY = 3, _('Mercredi')
        THURSDAY = 4, _('Jeudi')
        FRIDAY = 5, _('Vendredi')
        SATURDAY = 6, _('Samedi')

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('cours')
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('semestre')
    )
    day_of_week = models.IntegerField(
        _('jour'),
        choices=DayOfWeek.choices
    )
    start_time = models.TimeField(_('heure de début'))
    end_time = models.TimeField(_('heure de fin'))
    room = models.CharField(_('salle'), max_length=50)
    recurring = models.BooleanField(_('récurrent'), default=True)

    class Meta:
        verbose_name = _('horaire')
        verbose_name_plural = _('horaires')
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.course.title} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
