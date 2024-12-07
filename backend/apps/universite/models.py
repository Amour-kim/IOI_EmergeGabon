from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel

class Universite(TimestampedModel):
    """Modèle pour gérer les universités"""
    TYPE_ETABLISSEMENT_CHOICES = [
        ('PUBLIC', 'Public'),
        ('PRIVE', 'Privé'),
    ]
    
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
    ]
    
    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    type_etablissement = models.CharField(
        max_length=10,
        choices=TYPE_ETABLISSEMENT_CHOICES,
        default='PUBLIC'
    )
    ville = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='ACTIF'
    )
    date_creation = models.DateField()
    
    class Meta:
        verbose_name = "Université"
        verbose_name_plural = "Universités"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class Campus(TimestampedModel):
    """Modèle pour gérer les campus universitaires"""
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
    ]
    
    nom = models.CharField(max_length=200)
    universite = models.ForeignKey(
        Universite,
        on_delete=models.CASCADE,
        related_name='campus'
    )
    description = models.TextField(blank=True)
    ville = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='ACTIF'
    )
    date_creation = models.DateField()
    
    class Meta:
        verbose_name = "Campus"
        verbose_name_plural = "Campus"
        ordering = ['universite', 'nom']
    
    def __str__(self):
        return f"{self.nom} - {self.universite}"

class Faculte(TimestampedModel):
    """Modèle pour gérer les facultés"""
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
    ]
    
    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    universite = models.ForeignKey(
        Universite,
        on_delete=models.CASCADE,
        related_name='facultes'
    )
    campus = models.ForeignKey(
        Campus,
        on_delete=models.CASCADE,
        related_name='facultes'
    )
    description = models.TextField(blank=True)
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='ACTIF'
    )
    date_creation = models.DateField()
    
    class Meta:
        verbose_name = "Faculté"
        verbose_name_plural = "Facultés"
        ordering = ['universite', 'campus', 'nom']
        unique_together = ['universite', 'code']
    
    def __str__(self):
        return f"{self.nom} - {self.universite}"

class Departement(TimestampedModel):
    """Modèle pour gérer les départements"""
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
    ]
    
    nom = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    faculte = models.ForeignKey(
        Faculte,
        on_delete=models.CASCADE,
        related_name='departements'
    )
    description = models.TextField(blank=True)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='departements_diriges'
    )
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='ACTIF'
    )
    date_creation = models.DateField()
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['faculte', 'nom']
        unique_together = ['faculte', 'code']
    
    def __str__(self):
        return f"{self.nom} - {self.faculte}"
