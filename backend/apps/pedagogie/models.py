from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel

class Departement(TimestampedModel):
    """Modèle pour gérer les départements de l'université"""
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='departements_diriges'
    )
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"

class Cycle(TimestampedModel):
    """Modèle pour gérer les cycles d'études"""
    NIVEAU_CHOICES = [
        ('LICENCE', 'Licence'),
        ('MASTER', 'Master'),
        ('DOCTORAT', 'Doctorat'),
    ]
    
    nom = models.CharField(max_length=100)
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    duree = models.PositiveSmallIntegerField(help_text="Durée en semestres")
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Cycle"
        verbose_name_plural = "Cycles"
        ordering = ['niveau', 'nom']
    
    def __str__(self):
        return f"{self.niveau} - {self.nom}"

class Filiere(TimestampedModel):
    """Modèle pour gérer les filières d'études"""
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    departement = models.ForeignKey(
        Departement,
        on_delete=models.CASCADE,
        related_name='filieres'
    )
    cycle = models.ForeignKey(
        Cycle,
        on_delete=models.CASCADE,
        related_name='filieres'
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='filieres_dirigees'
    )
    
    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"
        ordering = ['departement', 'cycle', 'nom']
        unique_together = ['departement', 'cycle', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"

class UE(TimestampedModel):
    """Modèle pour gérer les Unités d'Enseignement"""
    code = models.CharField(max_length=10)
    intitule = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.PositiveSmallIntegerField()
    volume_horaire_cm = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Volume horaire CM"
    )
    volume_horaire_td = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Volume horaire TD"
    )
    volume_horaire_tp = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Volume horaire TP"
    )
    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        related_name='ues'
    )
    semestre = models.PositiveSmallIntegerField()
    prerequis = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='requis_pour'
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ues_dirigees'
    )
    
    class Meta:
        verbose_name = "UE"
        verbose_name_plural = "UEs"
        ordering = ['filiere', 'semestre', 'code']
        unique_together = ['filiere', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.intitule}"
    
    @property
    def volume_horaire_total(self):
        return self.volume_horaire_cm + self.volume_horaire_td + self.volume_horaire_tp

class ECUE(TimestampedModel):
    """Modèle pour gérer les Éléments Constitutifs d'UE"""
    code = models.CharField(max_length=10)
    intitule = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.PositiveSmallIntegerField()
    coefficient = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00
    )
    volume_horaire_cm = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Volume horaire CM"
    )
    volume_horaire_td = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Volume horaire TD"
    )
    volume_horaire_tp = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Volume horaire TP"
    )
    ue = models.ForeignKey(
        UE,
        on_delete=models.CASCADE,
        related_name='ecues'
    )
    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ecues_enseignees'
    )
    
    class Meta:
        verbose_name = "ECUE"
        verbose_name_plural = "ECUEs"
        ordering = ['ue', 'code']
        unique_together = ['ue', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.intitule}"
    
    @property
    def volume_horaire_total(self):
        return self.volume_horaire_cm + self.volume_horaire_td + self.volume_horaire_tp

class Programme(TimestampedModel):
    """Modèle pour gérer les programmes d'enseignement"""
    ecue = models.ForeignKey(
        ECUE,
        on_delete=models.CASCADE,
        related_name='programmes'
    )
    titre = models.CharField(max_length=200)
    description = models.TextField()
    objectifs = models.TextField()
    prerequis = models.TextField(blank=True)
    contenu = models.TextField()
    bibliographie = models.TextField(blank=True)
    methode_evaluation = models.TextField()
    
    class Meta:
        verbose_name = "Programme"
        verbose_name_plural = "Programmes"
        ordering = ['ecue', 'titre']
    
    def __str__(self):
        return f"{self.ecue.code} - {self.titre}"

class Seance(TimestampedModel):
    """Modèle pour gérer les séances de cours"""
    TYPE_CHOICES = [
        ('CM', 'Cours Magistral'),
        ('TD', 'Travaux Dirigés'),
        ('TP', 'Travaux Pratiques'),
    ]
    
    STATUT_CHOICES = [
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]
    
    ecue = models.ForeignKey(
        ECUE,
        on_delete=models.CASCADE,
        related_name='seances'
    )
    type_seance = models.CharField(max_length=2, choices=TYPE_CHOICES)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    salle = models.CharField(max_length=50)
    enseignant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='seances_enseignees'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='PLANIFIE'
    )
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Séance"
        verbose_name_plural = "Séances"
        ordering = ['date_debut']
    
    def __str__(self):
        return f"{self.ecue.code} - {self.get_type_seance_display()} du {self.date_debut}"
    
    @property
    def duree(self):
        return self.date_fin - self.date_debut
