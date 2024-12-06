from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Community(models.Model):
    """Modèle pour les communautés"""
    name = models.CharField(_('nom'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True)
    description = models.TextField(_('description'))
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_communities',
        verbose_name=_('créateur')
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CommunityMembership',
        through_fields=('community', 'user'),
        related_name='joined_communities',
        verbose_name=_('membres')
    )
    cover_image = models.ImageField(
        _('image de couverture'),
        upload_to='community_covers/',
        null=True,
        blank=True
    )
    is_private = models.BooleanField(_('privée'), default=False)
    requires_approval = models.BooleanField(
        _('nécessite une approbation'),
        default=False
    )
    rules = models.TextField(_('règles'), blank=True)
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='communities',
        verbose_name=_('tags')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('communauté')
        verbose_name_plural = _('communautés')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_private']),
        ]

    def __str__(self):
        return self.name

    def get_member_count(self):
        """Obtenir le nombre de membres"""
        return self.members.count()

    def is_member(self, user):
        """Vérifier si un utilisateur est membre"""
        return self.members.filter(id=user.id).exists()

    def get_pending_requests(self):
        """Obtenir les demandes d'adhésion en attente"""
        return self.membership_requests.filter(status='PENDING')

class CommunityMembership(models.Model):
    """Modèle pour l'adhésion aux communautés"""
    class Role(models.TextChoices):
        MEMBER = 'MEMBER', _('Membre')
        MODERATOR = 'MODERATOR', _('Modérateur')
        ADMIN = 'ADMIN', _('Administrateur')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_memberships',
        verbose_name=_('utilisateur')
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('communauté')
    )
    role = models.CharField(
        _('rôle'),
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='community_invitations',
        verbose_name=_('invité par')
    )
    is_banned = models.BooleanField(_('banni'), default=False)
    ban_reason = models.TextField(_('raison du bannissement'), blank=True)
    ban_expiry = models.DateTimeField(
        _('expiration du bannissement'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('adhésion')
        verbose_name_plural = _('adhésions')
        unique_together = ['user', 'community']
        indexes = [
            models.Index(fields=['user', 'community']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.community.name}"

    def is_ban_expired(self):
        """Vérifier si le bannissement a expiré"""
        if not self.is_banned or not self.ban_expiry:
            return True
        return timezone.now() > self.ban_expiry

class MembershipRequest(models.Model):
    """Modèle pour les demandes d'adhésion"""
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('En attente')
        APPROVED = 'APPROVED', _('Approuvée')
        REJECTED = 'REJECTED', _('Rejetée')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_requests',
        verbose_name=_('utilisateur')
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='membership_requests',
        verbose_name=_('communauté')
    )
    message = models.TextField(_('message'), blank=True)
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='handled_requests',
        verbose_name=_('traité par')
    )
    handled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('demande d\'adhésion')
        verbose_name_plural = _('demandes d\'adhésion')
        ordering = ['-created_at']
        unique_together = ['user', 'community']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user', 'community']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} → {self.community.name}"

class Discussion(models.Model):
    """Modèle pour les discussions"""
    title = models.CharField(_('titre'), max_length=200)
    content = models.TextField(_('contenu'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_discussions',
        verbose_name=_('auteur')
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='discussions',
        verbose_name=_('communauté')
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='discussions',
        verbose_name=_('tags')
    )
    is_pinned = models.BooleanField(_('épinglée'), default=False)
    is_locked = models.BooleanField(_('verrouillée'), default=False)
    views_count = models.PositiveIntegerField(_('vues'), default=0)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('discussion')
        verbose_name_plural = _('discussions')
        ordering = ['-is_pinned', '-last_activity']
        indexes = [
            models.Index(fields=['community', '-last_activity']),
            models.Index(fields=['is_pinned']),
            models.Index(fields=['is_locked']),
        ]

    def __str__(self):
        return self.title

    def increment_views(self):
        """Incrémenter le compteur de vues"""
        self.views_count += 1
        self.save()

class Comment(models.Model):
    """Modèle pour les commentaires"""
    content = models.TextField(_('contenu'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_comments',
        verbose_name=_('auteur')
    )
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('discussion')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('commentaire parent')
    )
    is_edited = models.BooleanField(_('modifié'), default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('commentaire')
        verbose_name_plural = _('commentaires')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['discussion', 'created_at']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"Commentaire de {self.author.get_full_name()}"

    def save(self, *args, **kwargs):
        if self.pk:  # Si le commentaire existe déjà
            self.is_edited = True
            self.edited_at = timezone.now()
        super().save(*args, **kwargs)

class Tag(models.Model):
    """Modèle pour les tags"""
    name = models.CharField(_('nom'), max_length=50, unique=True)
    slug = models.SlugField(_('slug'), unique=True)
    description = models.TextField(_('description'), blank=True)
    color = models.CharField(_('couleur'), max_length=7, default='#000000')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def get_usage_count(self):
        """Obtenir le nombre d'utilisations du tag"""
        return (
            self.communities.count() +
            self.discussions.count()
        )

class Report(models.Model):
    """Modèle pour les signalements"""
    class ReportType(models.TextChoices):
        DISCUSSION = 'DISCUSSION', _('Discussion')
        COMMENT = 'COMMENT', _('Commentaire')
        USER = 'USER', _('Utilisateur')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('En attente')
        RESOLVED = 'RESOLVED', _('Résolu')
        REJECTED = 'REJECTED', _('Rejeté')

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_made',
        verbose_name=_('signaleur')
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('communauté')
    )
    report_type = models.CharField(
        _('type'),
        max_length=20,
        choices=ReportType.choices
    )
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    reason = models.TextField(_('raison'))
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports_handled',
        verbose_name=_('traité par')
    )
    handled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('signalement')
        verbose_name_plural = _('signalements')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['report_type']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"Signalement par {self.reporter.get_full_name()}"
