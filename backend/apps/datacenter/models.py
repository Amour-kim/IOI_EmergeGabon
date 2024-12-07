from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Datacenter(models.Model):
    """Datacenter virtuel d'une université"""
    universite = models.ForeignKey(
        'universite.Universite',
        on_delete=models.CASCADE,
        related_name='datacenters'
    )
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacite_totale = models.PositiveIntegerField(  # En Go
        help_text='Capacité totale en Go'
    )
    stockage_utilise = models.PositiveIntegerField(
        default=0,
        help_text='Stockage utilisé en Go'
    )
    
    # Paramètres avancés
    backup_actif = models.BooleanField(
        default=False,
        help_text='Backup automatique actif'
    )
    frequence_backup = models.CharField(
        max_length=50,
        blank=True,
        help_text='Fréquence des backups'
    )
    retention_backup = models.PositiveIntegerField(
        default=30,
        help_text='Durée de rétention des backups en jours'
    )
    
    # Métadonnées
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Datacenter {self.nom} - {self.universite.nom}'

class Abonnement(models.Model):
    """Abonnement au datacenter"""
    TYPES = [
        ('BASIC', 'Basic'),
        ('STANDARD', 'Standard'),
        ('PREMIUM', 'Premium'),
        ('ENTERPRISE', 'Enterprise')
    ]
    
    universite = models.OneToOneField(
        'universite.Universite',
        on_delete=models.CASCADE,
        related_name='abonnement_datacenter'
    )
    type_abonnement = models.CharField(
        max_length=20,
        choices=TYPES,
        default='BASIC'
    )
    stockage_total = models.PositiveIntegerField(  # En Go
        validators=[MinValueValidator(100)],
        help_text='Capacité totale de stockage en Go'
    )
    stockage_utilise = models.PositiveIntegerField(
        default=0,
        help_text='Stockage utilisé en Go'
    )
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField()
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return f'Abonnement {self.type_abonnement} - {self.universite.nom}'

class Bibliotheque(models.Model):
    """Bibliothèque numérique"""
    datacenter = models.ForeignKey(
        Datacenter,
        on_delete=models.CASCADE,
        related_name='bibliotheques'
    )
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacite_stockage = models.PositiveIntegerField(  # En Go
        help_text='Capacité de stockage allouée en Go'
    )
    stockage_utilise = models.PositiveIntegerField(
        default=0,
        help_text='Stockage utilisé en Go'
    )
    
    def __str__(self):
        return f'Bibliothèque {self.nom} - {self.datacenter.universite.nom}'

class Salle(models.Model):
    """Salle de la bibliothèque"""
    bibliotheque = models.ForeignKey(
        Bibliotheque,
        on_delete=models.CASCADE,
        related_name='salles'
    )
    nom = models.CharField(max_length=100)
    numero = models.CharField(max_length=20)
    etage = models.IntegerField()
    capacite = models.PositiveIntegerField(
        help_text='Capacité en nombre de couloirs'
    )
    
    def __str__(self):
        return f'{self.nom} ({self.numero})'

class Couloir(models.Model):
    """Couloir dans une salle"""
    salle = models.ForeignKey(
        Salle,
        on_delete=models.CASCADE,
        related_name='couloirs'
    )
    numero = models.CharField(max_length=20)
    capacite = models.PositiveIntegerField(
        help_text='Capacité en nombre d\'étagères'
    )
    
    def __str__(self):
        return f'Couloir {self.numero} - {self.salle}'

class Etagere(models.Model):
    """Étagère dans un couloir"""
    couloir = models.ForeignKey(
        Couloir,
        on_delete=models.CASCADE,
        related_name='etageres'
    )
    numero = models.CharField(max_length=20)
    capacite = models.PositiveIntegerField(
        help_text='Capacité en nombre de sections'
    )
    
    def __str__(self):
        return f'Étagère {self.numero} - {self.couloir}'

class Section(models.Model):
    """Section d'une étagère"""
    etagere = models.ForeignKey(
        Etagere,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    capacite = models.PositiveIntegerField(
        help_text='Capacité en nombre de livres'
    )
    
    def __str__(self):
        return f'{self.nom} ({self.code})'

class Livre(models.Model):
    """Livre dans une section"""
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='livres'
    )
    titre = models.CharField(max_length=255)
    auteurs = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    edition = models.CharField(max_length=100)
    annee_publication = models.IntegerField()
    langue = models.CharField(max_length=50)
    format = models.CharField(max_length=20)  # PDF, EPUB, etc.
    taille = models.PositiveIntegerField(help_text='Taille en Mo')
    fichier = models.FileField(upload_to='bibliotheque/livres/')
    mots_cles = models.TextField(blank=True)
    description = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.titre

class Documentation(models.Model):
    """Centre de documentation"""
    datacenter = models.ForeignKey(
        Datacenter,
        on_delete=models.CASCADE,
        related_name='documentations'
    )
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacite_stockage = models.PositiveIntegerField(  # En Go
        help_text='Capacité de stockage allouée en Go'
    )
    stockage_utilise = models.PositiveIntegerField(
        default=0,
        help_text='Stockage utilisé en Go'
    )
    
    def __str__(self):
        return f'Documentation {self.nom} - {self.datacenter.universite.nom}'

class Document(models.Model):
    """Document dans la documentation"""
    TYPES = [
        ('PROCEDURE', 'Procédure'),
        ('GUIDE', 'Guide'),
        ('MANUEL', 'Manuel'),
        ('RAPPORT', 'Rapport'),
        ('AUTRE', 'Autre')
    ]
    
    documentation = models.ForeignKey(
        Documentation,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    titre = models.CharField(max_length=255)
    type_document = models.CharField(max_length=20, choices=TYPES)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documents'
    )
    version = models.CharField(max_length=20)
    format = models.CharField(max_length=20)  # PDF, DOC, etc.
    taille = models.PositiveIntegerField(help_text='Taille en Mo')
    fichier = models.FileField(upload_to='documentation/documents/')
    mots_cles = models.TextField(blank=True)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.titre

class Mediatheque(models.Model):
    """Médiathèque multimédia"""
    datacenter = models.ForeignKey(
        Datacenter,
        on_delete=models.CASCADE,
        related_name='mediatheques'
    )
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacite_stockage = models.PositiveIntegerField(  # En Go
        help_text='Capacité de stockage allouée en Go'
    )
    stockage_utilise = models.PositiveIntegerField(
        default=0,
        help_text='Stockage utilisé en Go'
    )
    
    def __str__(self):
        return f'Médiathèque {self.nom} - {self.datacenter.universite.nom}'

class Media(models.Model):
    """Média dans la médiathèque"""
    TYPES = [
        ('VIDEO', 'Vidéo'),
        ('AUDIO', 'Audio'),
        ('IMAGE', 'Image'),
        ('AUTRE', 'Autre')
    ]
    
    mediatheque = models.ForeignKey(
        Mediatheque,
        on_delete=models.CASCADE,
        related_name='medias'
    )
    titre = models.CharField(max_length=255)
    type_media = models.CharField(max_length=20, choices=TYPES)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='medias'
    )
    duree = models.DurationField(null=True, blank=True)  # Pour audio/vidéo
    format = models.CharField(max_length=20)
    resolution = models.CharField(
        max_length=20,
        blank=True,
        help_text='Pour vidéos et images'
    )
    taille = models.PositiveIntegerField(help_text='Taille en Mo')
    fichier = models.FileField(upload_to='mediatheque/fichiers/')
    vignette = models.ImageField(
        upload_to='mediatheque/vignettes/',
        blank=True
    )
    mots_cles = models.TextField(blank=True)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.titre
