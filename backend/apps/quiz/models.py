from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimestampedModel

class Quiz(TimestampedModel):
    """Modèle pour gérer les quiz"""
    TYPE_CHOICES = [
        ('EVALUATION', 'Quiz d\'évaluation'),
        ('ENTRAINEMENT', 'Quiz d\'entraînement'),
        ('EXAMEN', 'Quiz d\'examen'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cours = models.ForeignKey(
        'departements.Cours',
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    type_quiz = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='ENTRAINEMENT'
    )
    duree = models.PositiveIntegerField(
        help_text='Durée en minutes',
        validators=[MinValueValidator(1)]
    )
    nombre_tentatives = models.PositiveIntegerField(
        default=1,
        help_text='Nombre de tentatives autorisées'
    )
    note_passage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Note minimale pour réussir (en pourcentage)'
    )
    actif = models.BooleanField(default=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    aleatoire = models.BooleanField(
        default=False,
        help_text='Mélanger les questions'
    )
    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_crees'
    )

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} ({self.cours.intitule})"

class Question(TimestampedModel):
    """Modèle pour gérer les questions de quiz"""
    TYPE_CHOICES = [
        ('QCM', 'Question à choix multiples'),
        ('QCU', 'Question à choix unique'),
        ('TEXTE', 'Réponse textuelle'),
        ('VRAI_FAUX', 'Vrai ou Faux'),
    ]

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    texte = models.TextField()
    type_question = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )
    points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=1.00
    )
    explication = models.TextField(
        blank=True,
        help_text='Explication de la réponse correcte'
    )
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['quiz', 'ordre']

    def __str__(self):
        return f"Question {self.ordre} - {self.quiz.titre}"

class Reponse(TimestampedModel):
    """Modèle pour gérer les réponses possibles aux questions"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='reponses'
    )
    texte = models.TextField()
    correcte = models.BooleanField(default=False)
    explication = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
        ordering = ['question', 'ordre']

    def __str__(self):
        return f"Réponse {self.ordre} - Question {self.question.ordre}"

class Tentative(TimestampedModel):
    """Modèle pour gérer les tentatives de quiz des étudiants"""
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('ABANDONNEE', 'Abandonnée'),
        ('EXPIREE', 'Expirée'),
    ]

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='tentatives'
    )
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tentatives_quiz'
    )
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_COURS'
    )
    note = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    temps_passe = models.DurationField(null=True, blank=True)
    numero_tentative = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Tentative"
        verbose_name_plural = "Tentatives"
        ordering = ['-date_debut']
        unique_together = ['quiz', 'etudiant', 'numero_tentative']

    def __str__(self):
        return f"Tentative {self.numero_tentative} - {self.etudiant.get_full_name()}"

class ReponseEtudiant(TimestampedModel):
    """Modèle pour gérer les réponses des étudiants aux questions"""
    tentative = models.ForeignKey(
        Tentative,
        on_delete=models.CASCADE,
        related_name='reponses_etudiant'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='reponses_etudiant'
    )
    reponses = models.ManyToManyField(
        Reponse,
        related_name='reponses_etudiant',
        blank=True
    )
    texte_reponse = models.TextField(
        blank=True,
        help_text='Pour les questions à réponse textuelle'
    )
    correcte = models.BooleanField(default=False)
    points_obtenus = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0.00
    )
    commentaire = models.TextField(blank=True)

    class Meta:
        verbose_name = "Réponse étudiant"
        verbose_name_plural = "Réponses étudiants"
        ordering = ['tentative', 'question__ordre']
        unique_together = ['tentative', 'question']

    def __str__(self):
        return f"Réponse de {self.tentative.etudiant.get_full_name()} - Question {self.question.ordre}"
