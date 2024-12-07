from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimestampedModel
from apps.departements.models import Departement, Cours

class Categorie(TimestampedModel):
    """Modèle pour les catégories de ressources"""
    nom = models.CharField(_("Nom"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    parent = models.ForeignKey(
        'self',
        verbose_name=_("Catégorie parente"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sous_categories'
    )
    ordre = models.PositiveIntegerField(_("Ordre d'affichage"), default=0)

    class Meta:
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom

    @property
    def chemin_complet(self):
        """Retourne le chemin complet de la catégorie"""
        if self.parent:
            return f"{self.parent.chemin_complet} > {self.nom}"
        return self.nom

class Ressource(TimestampedModel):
    """Modèle pour les ressources numériques"""
    TYPES = (
        ('LIVRE', _('Livre')),
        ('ARTICLE', _('Article')),
        ('THESE', _('Thèse')),
        ('MEMOIRE', _('Mémoire')),
        ('COURS', _('Support de cours')),
        ('VIDEO', _('Vidéo')),
        ('AUDIO', _('Audio')),
        ('AUTRE', _('Autre'))
    )

    LANGUES = (
        ('FR', _('Français')),
        ('EN', _('Anglais')),
        ('ES', _('Espagnol')),
        ('AR', _('Arabe')),
        ('AUTRE', _('Autre'))
    )

    NIVEAUX = (
        ('L1', _('Licence 1')),
        ('L2', _('Licence 2')),
        ('L3', _('Licence 3')),
        ('M1', _('Master 1')),
        ('M2', _('Master 2')),
        ('DOC', _('Doctorat')),
        ('TOUS', _('Tous niveaux'))
    )

    titre = models.CharField(_("Titre"), max_length=255)
    auteurs = models.CharField(_("Auteurs"), max_length=255)
    annee_publication = models.PositiveIntegerField(
        _("Année de publication"),
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)
        ]
    )
    description = models.TextField(_("Description"))
    type_ressource = models.CharField(
        _("Type de ressource"),
        max_length=20,
        choices=TYPES
    )
    langue = models.CharField(
        _("Langue"),
        max_length=10,
        choices=LANGUES,
        default='FR'
    )
    niveau = models.CharField(
        _("Niveau"),
        max_length=10,
        choices=NIVEAUX,
        default='TOUS'
    )
    categories = models.ManyToManyField(
        Categorie,
        verbose_name=_("Catégories"),
        related_name='ressources'
    )
    departements = models.ManyToManyField(
        Departement,
        verbose_name=_("Départements"),
        related_name='ressources',
        blank=True
    )
    cours = models.ManyToManyField(
        Cours,
        verbose_name=_("Cours associés"),
        related_name='ressources',
        blank=True
    )
    mots_cles = models.CharField(
        _("Mots-clés"),
        max_length=255,
        help_text=_("Séparez les mots-clés par des virgules")
    )
    fichier = models.FileField(
        _("Fichier"),
        upload_to='bibliotheque/ressources/%Y/%m/'
    )
    url_externe = models.URLField(
        _("URL externe"),
        blank=True,
        help_text=_("URL vers une ressource externe")
    )
    est_public = models.BooleanField(
        _("Public"),
        default=True,
        help_text=_("La ressource est-elle accessible à tous ?")
    )
    est_valide = models.BooleanField(
        _("Validé"),
        default=False,
        help_text=_("La ressource a-t-elle été validée par un administrateur ?")
    )
    contributeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Contributeur"),
        on_delete=models.SET_NULL,
        null=True,
        related_name='ressources_contribuees'
    )
    nombre_telechargements = models.PositiveIntegerField(
        _("Nombre de téléchargements"),
        default=0
    )
    note_moyenne = models.DecimalField(
        _("Note moyenne"),
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    nombre_evaluations = models.PositiveIntegerField(
        _("Nombre d'évaluations"),
        default=0
    )

    class Meta:
        verbose_name = _("Ressource")
        verbose_name_plural = _("Ressources")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['titre']),
            models.Index(fields=['type_ressource']),
            models.Index(fields=['langue']),
            models.Index(fields=['niveau']),
            models.Index(fields=['est_public']),
            models.Index(fields=['est_valide'])
        ]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        """Mise à jour des statistiques lors de la sauvegarde"""
        if not self.pk:  # Nouvelle ressource
            super().save(*args, **kwargs)
        else:
            evaluations = self.evaluations.all()
            if evaluations.exists():
                self.note_moyenne = evaluations.aggregate(
                    models.Avg('note')
                )['note__avg']
                self.nombre_evaluations = evaluations.count()
            super().save(*args, **kwargs)

class Evaluation(TimestampedModel):
    """Modèle pour les évaluations des ressources"""
    ressource = models.ForeignKey(
        Ressource,
        verbose_name=_("Ressource"),
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Utilisateur"),
        on_delete=models.CASCADE,
        related_name='evaluations_bibliotheque'
    )
    note = models.PositiveSmallIntegerField(
        _("Note"),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    commentaire = models.TextField(_("Commentaire"), blank=True)

    class Meta:
        verbose_name = _("Évaluation")
        verbose_name_plural = _("Évaluations")
        unique_together = ['ressource', 'utilisateur']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.utilisateur} - {self.ressource} ({self.note}/5)"

    def save(self, *args, **kwargs):
        """Mise à jour des statistiques de la ressource"""
        super().save(*args, **kwargs)
        self.ressource.save()  # Déclenche la mise à jour des stats

class Telechargement(TimestampedModel):
    """Modèle pour suivre les téléchargements"""
    ressource = models.ForeignKey(
        Ressource,
        verbose_name=_("Ressource"),
        on_delete=models.CASCADE,
        related_name='telechargements'
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Utilisateur"),
        on_delete=models.CASCADE,
        related_name='telechargements_bibliotheque'
    )
    ip_address = models.GenericIPAddressField(_("Adresse IP"))
    user_agent = models.CharField(_("User Agent"), max_length=255)

    class Meta:
        verbose_name = _("Téléchargement")
        verbose_name_plural = _("Téléchargements")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.utilisateur} - {self.ressource}"

    def save(self, *args, **kwargs):
        """Mise à jour du compteur de téléchargements"""
        if not self.pk:  # Nouveau téléchargement
            self.ressource.nombre_telechargements += 1
            self.ressource.save()
        super().save(*args, **kwargs)

class Collection(TimestampedModel):
    """Modèle pour les collections personnelles"""
    nom = models.CharField(_("Nom"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Utilisateur"),
        on_delete=models.CASCADE,
        related_name='collections_bibliotheque'
    )
    ressources = models.ManyToManyField(
        Ressource,
        verbose_name=_("Ressources"),
        related_name='collections'
    )
    est_publique = models.BooleanField(
        _("Publique"),
        default=False,
        help_text=_("La collection est-elle visible par les autres utilisateurs ?")
    )

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")
        ordering = ['-created_at']
        unique_together = ['utilisateur', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.utilisateur})"
