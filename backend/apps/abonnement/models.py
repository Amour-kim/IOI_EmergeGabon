from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class PlanAbonnement(models.Model):
    """Plan d'abonnement disponible"""
    TYPES = [
        ('BASIC', 'Basic'),
        ('STANDARD', 'Standard'),
        ('PREMIUM', 'Premium'),
        ('ENTERPRISE', 'Enterprise')
    ]
    
    nom = models.CharField(max_length=50)
    type_plan = models.CharField(max_length=20, choices=TYPES)
    description = models.TextField()
    prix_mensuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    prix_annuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Limites des datacenters
    nb_max_datacenters = models.PositiveIntegerField(
        help_text='Nombre maximum de datacenters'
    )
    capacite_datacenter = models.PositiveIntegerField(  # En Go
        help_text='Capacité de chaque datacenter en Go'
    )
    
    # Limites des bibliothèques
    nb_max_bibliotheques = models.PositiveIntegerField(
        help_text='Nombre maximum de bibliothèques'
    )
    capacite_bibliotheque = models.PositiveIntegerField(  # En Go
        help_text='Capacité de chaque bibliothèque en Go'
    )
    
    # Limites des documentations
    nb_max_documentations = models.PositiveIntegerField(
        help_text='Nombre maximum de centres de documentation'
    )
    capacite_documentation = models.PositiveIntegerField(  # En Go
        help_text='Capacité de chaque documentation en Go'
    )
    
    # Limites des serveurs mail
    nb_max_serveurs_mail = models.PositiveIntegerField(
        help_text='Nombre maximum de serveurs mail'
    )
    capacite_mail = models.PositiveIntegerField(  # En Go
        help_text='Capacité de stockage mail par utilisateur en Go'
    )
    nb_max_utilisateurs_mail = models.PositiveIntegerField(
        help_text='Nombre maximum d\'utilisateurs mail'
    )
    
    # Limites des gestionnaires média
    nb_max_mediatheques = models.PositiveIntegerField(
        help_text='Nombre maximum de médiathèques'
    )
    capacite_mediatheque = models.PositiveIntegerField(  # En Go
        help_text='Capacité de chaque médiathèque en Go'
    )
    
    # Fonctionnalités avancées
    backup_auto = models.BooleanField(
        default=False,
        help_text='Backup automatique'
    )
    frequence_backup = models.CharField(
        max_length=50,
        blank=True,
        help_text='Fréquence des backups (quotidien, hebdomadaire, etc.)'
    )
    support_24_7 = models.BooleanField(
        default=False,
        help_text='Support technique 24/7'
    )
    temps_reponse_support = models.CharField(
        max_length=50,
        blank=True,
        help_text='Temps de réponse garanti du support'
    )
    
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plan d\'abonnement'
        verbose_name_plural = 'Plans d\'abonnement'
    
    def __str__(self):
        return f'{self.nom} ({self.type_plan})'

class Abonnement(models.Model):
    """Abonnement d'une université"""
    ETATS = [
        ('ACTIF', 'Actif'),
        ('SUSPENDU', 'Suspendu'),
        ('EXPIRE', 'Expiré'),
        ('RESILIE', 'Résilié')
    ]
    
    PERIODICITES = [
        ('MENSUEL', 'Mensuel'),
        ('ANNUEL', 'Annuel')
    ]
    
    universite = models.OneToOneField(
        'universite.Universite',
        on_delete=models.CASCADE,
        related_name='abonnement'
    )
    plan = models.ForeignKey(
        PlanAbonnement,
        on_delete=models.PROTECT,
        related_name='abonnements'
    )
    periodicite = models.CharField(
        max_length=20,
        choices=PERIODICITES,
        default='ANNUEL'
    )
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    etat = models.CharField(
        max_length=20,
        choices=ETATS,
        default='ACTIF'
    )
    renouvellement_auto = models.BooleanField(default=True)
    
    # Suivi de l'utilisation
    nb_datacenters_utilises = models.PositiveIntegerField(default=0)
    nb_bibliotheques_utilisees = models.PositiveIntegerField(default=0)
    nb_documentations_utilisees = models.PositiveIntegerField(default=0)
    nb_serveurs_mail_utilises = models.PositiveIntegerField(default=0)
    nb_mediatheques_utilisees = models.PositiveIntegerField(default=0)
    
    date_dernier_paiement = models.DateTimeField(null=True)
    date_prochain_paiement = models.DateTimeField(null=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
    
    def __str__(self):
        return f'Abonnement {self.plan.nom} - {self.universite.nom}'
    
    def est_actif(self):
        """Vérifie si l'abonnement est actif"""
        return (
            self.etat == 'ACTIF' and
            self.date_debut <= timezone.now() <= self.date_fin
        )
    
    def peut_ajouter_datacenter(self):
        """Vérifie si on peut ajouter un datacenter"""
        return self.nb_datacenters_utilises < self.plan.nb_max_datacenters
    
    def peut_ajouter_bibliotheque(self):
        """Vérifie si on peut ajouter une bibliothèque"""
        return self.nb_bibliotheques_utilisees < self.plan.nb_max_bibliotheques
    
    def peut_ajouter_documentation(self):
        """Vérifie si on peut ajouter une documentation"""
        return (
            self.nb_documentations_utilisees < self.plan.nb_max_documentations
        )
    
    def peut_ajouter_serveur_mail(self):
        """Vérifie si on peut ajouter un serveur mail"""
        return self.nb_serveurs_mail_utilises < self.plan.nb_max_serveurs_mail
    
    def peut_ajouter_mediatheque(self):
        """Vérifie si on peut ajouter une médiathèque"""
        return self.nb_mediatheques_utilisees < self.plan.nb_max_mediatheques

class HistoriquePaiement(models.Model):
    """Historique des paiements d'abonnement"""
    STATUTS = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDE', 'Validé'),
        ('ECHOUE', 'Échoué'),
        ('REMBOURSE', 'Remboursé')
    ]
    
    abonnement = models.ForeignKey(
        Abonnement,
        on_delete=models.CASCADE,
        related_name='paiements'
    )
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField()
    methode_paiement = models.CharField(max_length=50)
    reference_transaction = models.CharField(max_length=100)
    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='EN_ATTENTE'
    )
    details = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Historique de paiement'
        verbose_name_plural = 'Historique des paiements'
        ordering = ['-date_paiement']
    
    def __str__(self):
        return (
            f'Paiement de {self.montant}€ - '
            f'{self.abonnement.universite.nom}'
        )
