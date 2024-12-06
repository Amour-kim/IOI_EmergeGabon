from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.courses.models import Course

class AcademicYear(models.Model):
    """Modèle pour les années académiques"""
    year = models.CharField(_('année'), max_length=9)  # Format: 2023-2024
    start_date = models.DateField(_('date de début'))
    end_date = models.DateField(_('date de fin'))
    is_current = models.BooleanField(_('année en cours'), default=False)
    description = models.TextField(_('description'), blank=True)
    registration_start = models.DateField(
        _('début des inscriptions'),
        null=True,
        blank=True
    )
    registration_end = models.DateField(
        _('fin des inscriptions'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('année académique')
        verbose_name_plural = _('années académiques')
        ordering = ['-year']
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['is_current']),
        ]

    def __str__(self):
        return self.year

    def save(self, *args, **kwargs):
        if self.is_current:
            # Désactiver is_current pour les autres années
            AcademicYear.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

    def is_registration_open(self):
        """Vérifier si la période d'inscription est ouverte"""
        today = timezone.now().date()
        if not (self.registration_start and self.registration_end):
            return False
        return self.registration_start <= today <= self.registration_end

    def get_current_semester(self):
        """Obtenir le semestre actuel"""
        today = timezone.now().date()
        return self.semesters.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_current=True
        ).first()

class Semester(models.Model):
    """Modèle pour les semestres"""
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
    exam_start_date = models.DateField(
        _('début des examens'),
        null=True,
        blank=True
    )
    exam_end_date = models.DateField(
        _('fin des examens'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('semestre')
        verbose_name_plural = _('semestres')
        unique_together = ['academic_year', 'number']
        ordering = ['academic_year', 'number']
        indexes = [
            models.Index(fields=['academic_year', 'number']),
            models.Index(fields=['is_current']),
        ]

    def __str__(self):
        return f"{self.academic_year} - Semestre {self.number}"

    def save(self, *args, **kwargs):
        if self.is_current:
            # Désactiver is_current pour les autres semestres
            Semester.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

    def is_exam_period(self):
        """Vérifier si c'est la période des examens"""
        today = timezone.now().date()
        if not (self.exam_start_date and self.exam_end_date):
            return False
        return self.exam_start_date <= today <= self.exam_end_date

    def get_weeks_remaining(self):
        """Obtenir le nombre de semaines restantes"""
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        remaining = self.end_date - today
        return remaining.days // 7

class Grade(models.Model):
    """Modèle pour les notes"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
    coefficient = models.PositiveIntegerField(
        _('coefficient'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    grade_type = models.CharField(
        _('type d\'évaluation'),
        max_length=20,
        choices=[
            ('EXAM', _('Examen')),
            ('CC', _('Contrôle Continu')),
            ('TP', _('Travaux Pratiques')),
            ('PROJECT', _('Projet')),
        ]
    )
    comment = models.TextField(_('commentaire'), blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='grades_given',
        verbose_name=_('noté par')
    )
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')
        unique_together = ['student', 'course', 'semester', 'grade_type']
        ordering = ['-graded_at']
        indexes = [
            models.Index(fields=['student', 'course', 'semester']),
            models.Index(fields=['grade_type']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title} - {self.score}/20"

    def get_weighted_score(self):
        """Obtenir la note pondérée"""
        return self.score * self.coefficient

    @property
    def mention(self):
        """Obtenir la mention correspondant à la note"""
        if self.score >= 16:
            return _('Très Bien')
        elif self.score >= 14:
            return _('Bien')
        elif self.score >= 12:
            return _('Assez Bien')
        elif self.score >= 10:
            return _('Passable')
        else:
            return _('Insuffisant')

class Attendance(models.Model):
    """Modèle pour les présences"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
    time_in = models.TimeField(_('heure d\'arrivée'))
    time_out = models.TimeField(
        _('heure de sortie'),
        null=True,
        blank=True
    )
    is_present = models.BooleanField(_('présent'), default=False)
    is_late = models.BooleanField(_('en retard'), default=False)
    excuse = models.TextField(_('justification'), blank=True)
    excuse_document = models.FileField(
        _('document justificatif'),
        upload_to='excuses/',
        null=True,
        blank=True
    )
    validated = models.BooleanField(_('validé'), default=False)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attendances_validated',
        verbose_name=_('validé par')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('présence')
        verbose_name_plural = _('présences')
        unique_together = ['student', 'course', 'date']
        ordering = ['-date', '-time_in']
        indexes = [
            models.Index(fields=['student', 'course', 'date']),
            models.Index(fields=['is_present']),
            models.Index(fields=['validated']),
        ]

    def __str__(self):
        status = _('Présent') if self.is_present else _('Absent')
        return f"{self.student.get_full_name()} - {self.course.title} - {self.date} - {status}"

    def save(self, *args, **kwargs):
        if self.time_in and not self.is_late:
            # Vérifier si l'étudiant est en retard (plus de 15 minutes)
            course_start = self.course.start_time
            if course_start:
                late_threshold = timedelta(minutes=15)
                time_diff = timedelta(
                    hours=self.time_in.hour - course_start.hour,
                    minutes=self.time_in.minute - course_start.minute
                )
                self.is_late = time_diff > late_threshold
        super().save(*args, **kwargs)

    def get_duration(self):
        """Calculer la durée de présence"""
        if not (self.time_in and self.time_out):
            return None
        time_in = timezone.datetime.combine(
            timezone.now().date(),
            self.time_in
        )
        time_out = timezone.datetime.combine(
            timezone.now().date(),
            self.time_out
        )
        return time_out - time_in

class Schedule(models.Model):
    """Modèle pour les emplois du temps"""
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
    building = models.CharField(_('bâtiment'), max_length=50)
    floor = models.CharField(_('étage'), max_length=10)
    capacity = models.PositiveIntegerField(
        _('capacité'),
        validators=[MinValueValidator(1)]
    )
    is_recurring = models.BooleanField(_('récurrent'), default=True)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('horaire')
        verbose_name_plural = _('horaires')
        ordering = ['semester', 'day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['semester', 'day_of_week']),
            models.Index(fields=['course']),
            models.Index(fields=['room']),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    def save(self, *args, **kwargs):
        # Vérifier les conflits d'horaires avant la sauvegarde
        if self.has_conflicts():
            raise ValueError(_("Il y a un conflit d'horaire avec un autre cours."))
        super().save(*args, **kwargs)

    def has_conflicts(self):
        """Vérifier s'il y a des conflits d'horaires"""
        return Schedule.objects.filter(
            semester=self.semester,
            day_of_week=self.day_of_week,
            room=self.room
        ).exclude(id=self.id).filter(
            models.Q(
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )
        ).exists()

    def get_duration(self):
        """Calculer la durée du cours"""
        start = timezone.datetime.combine(
            timezone.now().date(),
            self.start_time
        )
        end = timezone.datetime.combine(
            timezone.now().date(),
            self.end_time
        )
        return end - start
