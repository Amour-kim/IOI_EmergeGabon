from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel

class Faculte(TimestampedModel):
    """Modèle pour gérer les facultés de l'université"""
    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    doyen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='facultes_dirigees'
    )
    date_creation = models.DateField()
    site_web = models.URLField(blank=True)
    email_contact = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)

    class Meta:
        verbose_name = "Faculté"
        verbose_name_plural = "Facultés"
        ordering = ['nom']

    def __str__(self):
        return f"{self.code} - {self.nom}"

class Departement(TimestampedModel):
    """Modèle pour gérer les départements au sein des facultés"""
    faculte = models.ForeignKey(
        Faculte,
        on_delete=models.CASCADE,
        related_name='departements'
    )
    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    chef_departement = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='departements_diriges'
    )
    date_creation = models.DateField()
    capacite_accueil = models.PositiveIntegerField(help_text="Nombre maximum d'étudiants")
    email_contact = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    bureau = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['faculte__nom', 'nom']

    def __str__(self):
        return f"{self.code} - {self.nom}"

class Programme(TimestampedModel):
    """Modèle pour gérer les programmes d'études"""
    NIVEAU_CHOICES = [
        ('LICENCE', 'Licence'),
        ('MASTER', 'Master'),
        ('DOCTORAT', 'Doctorat'),
    ]

    departement = models.ForeignKey(
        Departement,
        on_delete=models.CASCADE,
        related_name='programmes'
    )
    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    description = models.TextField()
    duree = models.PositiveIntegerField(help_text="Durée en semestres")
    credits_requis = models.PositiveIntegerField(help_text="Nombre de crédits requis")
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='programmes_diriges'
    )
    conditions_admission = models.TextField()
    debouches = models.TextField(verbose_name="Débouchés")
    est_actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Programme"
        verbose_name_plural = "Programmes"
        ordering = ['departement__nom', 'niveau', 'nom']

    def __str__(self):
        return f"{self.code} - {self.nom} ({self.get_niveau_display()})"

class Cours(TimestampedModel):
    """Modèle pour gérer les cours offerts dans les programmes"""
    TYPE_CHOICES = [
        ('OBLIGATOIRE', 'Cours obligatoire'),
        ('OPTIONNEL', 'Cours optionnel'),
    ]

    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='cours'
    )
    code = models.CharField(max_length=10, unique=True)
    intitule = models.CharField(max_length=200)
    description = models.TextField()
    credits = models.PositiveIntegerField()
    volume_horaire = models.PositiveIntegerField(help_text="Nombre d'heures total")
    type_cours = models.CharField(max_length=20, choices=TYPE_CHOICES)
    prerequis = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='cours_suivants'
    )
    enseignant_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cours_enseignes'
    )
    semestre = models.PositiveIntegerField()
    objectifs = models.TextField()
    contenu = models.TextField()
    methode_evaluation = models.TextField()
    est_actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['programme__nom', 'semestre', 'intitule']
        unique_together = ['programme', 'code']

    def __str__(self):
        return f"{self.code} - {self.intitule}"
