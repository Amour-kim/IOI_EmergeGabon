from django.db import models
from django.conf import settings
from django.core.validators import (
    validate_email, MinLengthValidator, RegexValidator
)

class ConfigurationEmail(models.Model):
    """Configuration du service email pour une université"""
    nom_domaine = models.CharField(
        max_length=255,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$',
                message='Entrez un nom de domaine valide (ex: univ-masuku.ga)'
            )
        ],
        help_text='Nom de domaine pour les emails (ex: univ-masuku.ga)'
    )
    
    # Configuration SMTP
    smtp_host = models.CharField(
        max_length=255,
        help_text='Serveur SMTP (ex: smtp.gmail.com)'
    )
    smtp_port = models.PositiveIntegerField(
        default=587,
        help_text='Port SMTP (par défaut: 587 pour TLS)'
    )
    smtp_user = models.CharField(
        max_length=255,
        help_text='Nom d\'utilisateur SMTP'
    )
    smtp_password = models.CharField(
        max_length=255,
        help_text='Mot de passe SMTP'
    )
    smtp_use_tls = models.BooleanField(
        default=True,
        help_text='Utiliser TLS pour la connexion SMTP'
    )
    smtp_use_ssl = models.BooleanField(
        default=False,
        help_text='Utiliser SSL pour la connexion SMTP'
    )
    
    # Configuration IMAP
    imap_host = models.CharField(
        max_length=255,
        help_text='Serveur IMAP (ex: imap.gmail.com)'
    )
    imap_port = models.PositiveIntegerField(
        default=993,
        help_text='Port IMAP (par défaut: 993 pour SSL)'
    )
    imap_user = models.CharField(
        max_length=255,
        help_text='Nom d\'utilisateur IMAP'
    )
    imap_password = models.CharField(
        max_length=255,
        help_text='Mot de passe IMAP'
    )
    imap_use_ssl = models.BooleanField(
        default=True,
        help_text='Utiliser SSL pour la connexion IMAP'
    )
    
    # Paramètres des emails
    from_email = models.EmailField(
        help_text='Adresse email d\'envoi par défaut'
    )
    from_name = models.CharField(
        max_length=255,
        help_text='Nom d\'affichage de l\'expéditeur'
    )
    signature_defaut = models.TextField(
        blank=True,
        help_text='Signature par défaut pour les emails'
    )
    
    # Paramètres de quota
    quota_boite = models.PositiveIntegerField(
        default=1024,
        help_text='Quota de la boîte mail en Mo'
    )
    taille_max_piece_jointe = models.PositiveIntegerField(
        default=10,
        help_text='Taille maximale des pièces jointes en Mo'
    )
    
    # Paramètres de sécurité
    dkim_active = models.BooleanField(
        default=False,
        help_text='Activer la signature DKIM'
    )
    dkim_domain = models.CharField(
        max_length=255,
        blank=True,
        help_text='Domaine DKIM'
    )
    dkim_selector = models.CharField(
        max_length=255,
        blank=True,
        help_text='Sélecteur DKIM'
    )
    dkim_private_key = models.TextField(
        blank=True,
        help_text='Clé privée DKIM'
    )
    
    spf_active = models.BooleanField(
        default=False,
        help_text='Activer SPF'
    )
    spf_record = models.CharField(
        max_length=255,
        blank=True,
        help_text='Enregistrement SPF'
    )
    
    dmarc_active = models.BooleanField(
        default=False,
        help_text='Activer DMARC'
    )
    dmarc_record = models.CharField(
        max_length=255,
        blank=True,
        help_text='Enregistrement DMARC'
    )
    
    # Métadonnées
    actif = models.BooleanField(
        default=True,
        help_text='Configuration active'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuration email'
        verbose_name_plural = 'Configurations email'
    
    def __str__(self):
        return f'Configuration email pour {self.nom_domaine}'

class CompteEmail(models.Model):
    """Compte email d'un utilisateur"""
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='compte_email'
    )
    configuration = models.ForeignKey(
        ConfigurationEmail,
        on_delete=models.PROTECT,
        related_name='comptes'
    )
    
    adresse_email = models.EmailField(
        unique=True,
        validators=[validate_email],
        help_text='Adresse email complète'
    )
    mot_de_passe = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(8)],
        help_text='Mot de passe du compte email'
    )
    
    quota_utilise = models.PositiveIntegerField(
        default=0,
        help_text='Quota utilisé en Mo'
    )
    signature_personnalisee = models.TextField(
        blank=True,
        help_text='Signature personnalisée'
    )
    
    # Paramètres du compte
    transfert_actif = models.BooleanField(
        default=False,
        help_text='Activer le transfert des emails'
    )
    adresse_transfert = models.EmailField(
        blank=True,
        help_text='Adresse email de transfert'
    )
    reponse_auto_active = models.BooleanField(
        default=False,
        help_text='Activer la réponse automatique'
    )
    message_reponse_auto = models.TextField(
        blank=True,
        help_text='Message de réponse automatique'
    )
    date_debut_reponse_auto = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date de début de la réponse automatique'
    )
    date_fin_reponse_auto = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date de fin de la réponse automatique'
    )
    
    # Métadonnées
    actif = models.BooleanField(
        default=True,
        help_text='Compte actif'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    derniere_connexion = models.DateTimeField(
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Compte email'
        verbose_name_plural = 'Comptes email'
        
    def __str__(self):
        return self.adresse_email
    
    def save(self, *args, **kwargs):
        # Générer l'adresse email si elle n'existe pas
        if not self.adresse_email:
            username = self.utilisateur.email.split('@')[0]
            self.adresse_email = f'{username}@{self.configuration.nom_domaine}'
        super().save(*args, **kwargs)

class Alias(models.Model):
    """Alias email pour un compte"""
    compte = models.ForeignKey(
        CompteEmail,
        on_delete=models.CASCADE,
        related_name='alias'
    )
    adresse_alias = models.EmailField(
        unique=True,
        validators=[validate_email],
        help_text='Adresse email de l\'alias'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Description de l\'alias'
    )
    actif = models.BooleanField(
        default=True,
        help_text='Alias actif'
    )
    
    class Meta:
        verbose_name = 'Alias email'
        verbose_name_plural = 'Alias email'
        
    def __str__(self):
        return f'{self.adresse_alias} -> {self.compte.adresse_email}'

class ListeDiffusion(models.Model):
    """Liste de diffusion email"""
    configuration = models.ForeignKey(
        ConfigurationEmail,
        on_delete=models.CASCADE,
        related_name='listes_diffusion'
    )
    
    nom = models.CharField(
        max_length=255,
        help_text='Nom de la liste'
    )
    adresse_email = models.EmailField(
        unique=True,
        validators=[validate_email],
        help_text='Adresse email de la liste'
    )
    description = models.TextField(
        blank=True,
        help_text='Description de la liste'
    )
    
    moderateurs = models.ManyToManyField(
        CompteEmail,
        related_name='listes_moderees',
        blank=True,
        help_text='Modérateurs de la liste'
    )
    membres = models.ManyToManyField(
        CompteEmail,
        related_name='listes_abonnees',
        blank=True,
        help_text='Membres de la liste'
    )
    
    moderation_active = models.BooleanField(
        default=False,
        help_text='Activer la modération des messages'
    )
    inscription_libre = models.BooleanField(
        default=False,
        help_text='Permettre l\'inscription libre'
    )
    archive_active = models.BooleanField(
        default=True,
        help_text='Activer l\'archivage des messages'
    )
    
    actif = models.BooleanField(
        default=True,
        help_text='Liste active'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Liste de diffusion'
        verbose_name_plural = 'Listes de diffusion'
        
    def __str__(self):
        return self.adresse_email
