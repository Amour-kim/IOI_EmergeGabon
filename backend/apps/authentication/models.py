from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    """Modèle utilisateur personnalisé"""
    
    CATEGORIES = [
        ('ENSEIGNANT', 'Enseignant'),
        ('ETUDIANT', 'Étudiant'),
        ('PROFESSIONNEL', 'Professionnel'),
        ('PARENT', 'Parent')
    ]
    
    STATUTS = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('SUSPENDU', 'Suspendu')
    ]
    
    # Informations de base
    email = models.EmailField(_('adresse email'), unique=True)
    matricule = models.CharField(max_length=50, unique=True)
    categorie = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        default='ETUDIANT'
    )
    
    # Informations personnelles
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    
    # Informations académiques/professionnelles
    universite = models.ForeignKey(
        'universite.Universite',
        on_delete=models.SET_NULL,
        null=True,
        related_name='utilisateurs'
    )
    departement = models.ForeignKey(
        'pedagogie.Departement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs'
    )
    
    # Informations spécifiques par catégorie
    specialite = models.CharField(
        max_length=100,
        blank=True,
        help_text='Spécialité pour les enseignants'
    )
    niveau_etude = models.CharField(
        max_length=50,
        blank=True,
        help_text='Niveau d\'étude pour les étudiants'
    )
    profession = models.CharField(
        max_length=100,
        blank=True,
        help_text='Profession pour les professionnels'
    )
    enfants = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='parents',
        help_text='Enfants pour les parents'
    )
    
    # Métadonnées
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='ACTIF'
    )
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)
    
    # Configuration
    langue = models.CharField(
        max_length=10,
        default='fr',
        help_text='Langue préférée de l\'utilisateur'
    )
    notifications_email = models.BooleanField(
        default=True,
        help_text='Recevoir les notifications par email'
    )
    notifications_sms = models.BooleanField(
        default=False,
        help_text='Recevoir les notifications par SMS'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['matricule', 'nom', 'prenoms', 'categorie']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['nom', 'prenoms']
    
    def __str__(self):
        return f'{self.nom} {self.prenoms} ({self.get_categorie_display()})'
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return f'{self.nom} {self.prenoms}'
    
    def get_short_name(self):
        """Retourne le prénom de l'utilisateur"""
        return self.prenoms
    
    @property
    def est_enseignant(self):
        """Vérifie si l'utilisateur est un enseignant"""
        return self.categorie == 'ENSEIGNANT'
    
    @property
    def est_etudiant(self):
        """Vérifie si l'utilisateur est un étudiant"""
        return self.categorie == 'ETUDIANT'
    
    @property
    def est_professionnel(self):
        """Vérifie si l'utilisateur est un professionnel"""
        return self.categorie == 'PROFESSIONNEL'
    
    @property
    def est_parent(self):
        """Vérifie si l'utilisateur est un parent"""
        return self.categorie == 'PARENT'
    
    def activer(self):
        """Active le compte utilisateur"""
        self.is_active = True
        self.statut = 'ACTIF'
        self.save()
    
    def desactiver(self):
        """Désactive le compte utilisateur"""
        self.is_active = False
        self.statut = 'INACTIF'
        self.save()
    
    def suspendre(self):
        """Suspend le compte utilisateur"""
        self.is_active = False
        self.statut = 'SUSPENDU'
        self.save()
