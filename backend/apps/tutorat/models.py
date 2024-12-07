from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel

class Tuteur(TimestampedModel):
    """Modèle pour gérer les tuteurs"""
    NIVEAU_CHOICES = [
        ('LICENCE', 'Licence'),
        ('MASTER', 'Master'),
        ('DOCTORAT', 'Doctorat'),
        ('ENSEIGNANT', 'Enseignant'),
    ]

    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de validation'),
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('SUSPENDU', 'Suspendu'),
    ]

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profil_tuteur'
    )
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    departement = models.ForeignKey(
        'departements.Departement',
        on_delete=models.CASCADE,
        related_name='tuteurs'
    )
    specialites = models.ManyToManyField(
        'departements.Cours',
        related_name='tuteurs',
        help_text="Cours que le tuteur peut enseigner"
    )
    cv = models.FileField(upload_to='tuteurs/cv/')
    biographie = models.TextField()
    disponibilites = models.TextField(
        help_text="Description des disponibilités du tuteur"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )
    note_moyenne = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    nombre_evaluations = models.PositiveIntegerField(default=0)
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(blank=True)

    class Meta:
        verbose_name = "Tuteur"
        verbose_name_plural = "Tuteurs"
        ordering = ['-note_moyenne', 'utilisateur__last_name']

    def __str__(self):
        return f"{self.utilisateur.get_full_name()} - {self.get_niveau_display()}"

    def mettre_a_jour_note(self, nouvelle_note):
        """Mise à jour de la note moyenne"""
        total = self.note_moyenne * self.nombre_evaluations
        self.nombre_evaluations += 1
        self.note_moyenne = (total + nouvelle_note) / self.nombre_evaluations
        self.save()

class SeanceTutorat(TimestampedModel):
    """Modèle pour gérer les séances de tutorat"""
    TYPE_CHOICES = [
        ('INDIVIDUEL', 'Cours individuel'),
        ('GROUPE', 'Cours en groupe'),
        ('REVISION', 'Séance de révision'),
        ('METHODOLOGIE', 'Aide méthodologique'),
    ]

    STATUT_CHOICES = [
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
    ]

    MODALITE_CHOICES = [
        ('PRESENTIEL', 'En présentiel'),
        ('DISTANCIEL', 'À distance'),
        ('HYBRIDE', 'Hybride'),
    ]

    tuteur = models.ForeignKey(
        Tuteur,
        on_delete=models.CASCADE,
        related_name='seances'
    )
    cours = models.ForeignKey(
        'departements.Cours',
        on_delete=models.CASCADE,
        related_name='seances_tutorat'
    )
    type_seance = models.CharField(max_length=20, choices=TYPE_CHOICES)
    modalite = models.CharField(max_length=20, choices=MODALITE_CHOICES)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    lieu = models.CharField(
        max_length=200,
        blank=True,
        help_text="Lieu physique ou lien de visioconférence"
    )
    capacite_max = models.PositiveIntegerField(
        default=1,
        help_text="Nombre maximum de participants"
    )
    description = models.TextField()
    objectifs = models.TextField()
    prerequis = models.TextField(blank=True)
    materiel_necessaire = models.TextField(blank=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='PLANIFIEE'
    )
    tarif_horaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Tarif horaire en FCFA"
    )

    class Meta:
        verbose_name = "Séance de tutorat"
        verbose_name_plural = "Séances de tutorat"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.cours.intitule} - {self.tuteur.utilisateur.get_full_name()}"

class Inscription(TimestampedModel):
    """Modèle pour gérer les inscriptions aux séances de tutorat"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRMEE', 'Confirmée'),
        ('ANNULEE', 'Annulée'),
    ]

    seance = models.ForeignKey(
        SeanceTutorat,
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inscriptions_tutorat'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )
    date_inscription = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True)
    presence_confirmee = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Inscription au tutorat"
        verbose_name_plural = "Inscriptions au tutorat"
        unique_together = ['seance', 'etudiant']
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.etudiant.get_full_name()} - {self.seance}"

class Evaluation(TimestampedModel):
    """Modèle pour gérer les évaluations des séances de tutorat"""
    seance = models.ForeignKey(
        SeanceTutorat,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations_tutorat'
    )
    note = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Note de 1 à 5"
    )
    commentaire = models.TextField()
    points_forts = models.TextField(blank=True)
    points_amelioration = models.TextField(blank=True)
    date_evaluation = models.DateTimeField(auto_now_add=True)
    anonyme = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
        unique_together = ['seance', 'etudiant']
        ordering = ['-date_evaluation']

    def __str__(self):
        return f"Évaluation de {self.etudiant.get_full_name()} - {self.seance}"

    def save(self, *args, **kwargs):
        """Mise à jour de la note moyenne du tuteur lors de l'évaluation"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.seance.tuteur.mettre_a_jour_note(self.note)

class Support(TimestampedModel):
    """Modèle pour gérer les supports de cours"""
    TYPE_CHOICES = [
        ('COURS', 'Support de cours'),
        ('EXERCICE', 'Exercices'),
        ('CORRECTION', 'Correction'),
        ('RESSOURCE', 'Ressource complémentaire'),
    ]

    seance = models.ForeignKey(
        SeanceTutorat,
        on_delete=models.CASCADE,
        related_name='supports'
    )
    titre = models.CharField(max_length=200)
    type_support = models.CharField(max_length=20, choices=TYPE_CHOICES)
    fichier = models.FileField(upload_to='supports_tutorat/')
    description = models.TextField(blank=True)
    date_publication = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Support de cours"
        verbose_name_plural = "Supports de cours"
        ordering = ['-date_publication']

    def __str__(self):
        return f"{self.titre} - {self.seance}"
