from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel

class Evenement(TimestampedModel):
    """Modèle pour gérer les événements universitaires"""
    TYPE_CHOICES = [
        ('CONFERENCE', 'Conférence'),
        ('SEMINAIRE', 'Séminaire'),
        ('ATELIER', 'Atelier'),
        ('CEREMONIE', 'Cérémonie'),
        ('REUNION', 'Réunion'),
        ('CULTUREL', 'Événement culturel'),
        ('SPORTIF', 'Événement sportif'),
        ('AUTRE', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]

    titre = models.CharField(max_length=200)
    type_evenement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    lieu = models.CharField(max_length=200)
    capacite = models.PositiveIntegerField(help_text="Nombre maximum de participants")
    organisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evenements_organises'
    )
    departements = models.ManyToManyField(
        'departements.Departement',
        related_name='evenements',
        blank=True
    )
    image = models.ImageField(upload_to='evenements/', blank=True)
    inscription_requise = models.BooleanField(default=True)
    places_disponibles = models.PositiveIntegerField()
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='PLANIFIE'
    )
    public_cible = models.TextField(help_text="Description du public visé")
    contact_email = models.EmailField()
    contact_telephone = models.CharField(max_length=20, blank=True)
    site_web = models.URLField(blank=True)
    cout = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Coût de participation"
    )

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.titre} ({self.get_type_evenement_display()})"

    def save(self, *args, **kwargs):
        if not self.places_disponibles:
            self.places_disponibles = self.capacite
        super().save(*args, **kwargs)

class Inscription(TimestampedModel):
    """Modèle pour gérer les inscriptions aux événements"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRMEE', 'Confirmée'),
        ('ANNULEE', 'Annulée'),
    ]

    evenement = models.ForeignKey(
        Evenement,
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inscriptions_evenements'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )
    date_inscription = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True)
    presence_confirmee = models.BooleanField(default=False)
    certificat_genere = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Inscription à un événement"
        verbose_name_plural = "Inscriptions aux événements"
        unique_together = ['evenement', 'participant']
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.participant.get_full_name()} - {self.evenement.titre}"

class Document(TimestampedModel):
    """Modèle pour gérer les documents liés aux événements"""
    TYPE_CHOICES = [
        ('PROGRAMME', 'Programme'),
        ('PRESENTATION', 'Présentation'),
        ('SUPPORT', 'Support de cours'),
        ('COMPTE_RENDU', 'Compte-rendu'),
        ('CERTIFICAT', 'Certificat'),
        ('AUTRE', 'Autre'),
    ]

    evenement = models.ForeignKey(
        Evenement,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    titre = models.CharField(max_length=200)
    type_document = models.CharField(max_length=20, choices=TYPE_CHOICES)
    fichier = models.FileField(upload_to='documents_evenements/')
    description = models.TextField(blank=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(
        default=False,
        help_text="Si coché, le document est accessible à tous"
    )

    class Meta:
        verbose_name = "Document d'événement"
        verbose_name_plural = "Documents d'événements"
        ordering = ['-date_publication']

    def __str__(self):
        return f"{self.titre} - {self.evenement.titre}"

class Feedback(TimestampedModel):
    """Modèle pour gérer les retours sur les événements"""
    evenement = models.ForeignKey(
        Evenement,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks_evenements'
    )
    note = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Note de 1 à 5"
    )
    commentaire = models.TextField()
    points_positifs = models.TextField(blank=True)
    points_amelioration = models.TextField(blank=True)
    date_feedback = models.DateTimeField(auto_now_add=True)
    anonyme = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        unique_together = ['evenement', 'participant']
        ordering = ['-date_feedback']

    def __str__(self):
        return f"Feedback de {self.participant.get_full_name()} - {self.evenement.titre}"
