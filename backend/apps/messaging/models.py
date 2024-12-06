from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from apps.users.models import User

class Conversation(models.Model):
    """Model for conversations between users"""
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        verbose_name=_('participants')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_group = models.BooleanField(_('conversation de groupe'), default=False)
    name = models.CharField(_('nom'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('conversation')
        verbose_name_plural = _('conversations')
        ordering = ['-updated_at']

    def __str__(self):
        if self.is_group and self.name:
            return self.name
        return ", ".join([user.get_full_name() for user in self.participants.all()[:3]])

class Message(models.Model):
    """Model for messages in conversations"""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('conversation')
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('expéditeur')
    )
    content = models.TextField(_('contenu'))
    created_at = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(
        User,
        related_name='read_messages',
        verbose_name=_('lu par'),
        blank=True
    )
    file = models.FileField(
        _('fichier'),
        upload_to='message_files/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.get_full_name()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

class Notification(models.Model):
    """Model for system notifications"""
    class NotificationType(models.TextChoices):
        INFO = 'INFO', _('Information')
        SUCCESS = 'SUCCESS', _('Succès')
        WARNING = 'WARNING', _('Avertissement')
        ERROR = 'ERROR', _('Erreur')

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('destinataire')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO
    )
    title = models.CharField(_('titre'), max_length=255)
    message = models.TextField(_('message'))
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(_('lu'), default=False)
    read_at = models.DateTimeField(_('lu le'), null=True, blank=True)
    link = models.CharField(_('lien'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.get_full_name()} - {self.title}"

class Announcement(models.Model):
    """Model for system-wide announcements"""
    class AnnouncementPriority(models.TextChoices):
        LOW = 'LOW', _('Basse')
        MEDIUM = 'MEDIUM', _('Moyenne')
        HIGH = 'HIGH', _('Haute')
        URGENT = 'URGENT', _('Urgente')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name=_('auteur')
    )
    title = models.CharField(_('titre'), max_length=255)
    content = models.TextField(_('contenu'))
    priority = models.CharField(
        _('priorité'),
        max_length=20,
        choices=AnnouncementPriority.choices,
        default=AnnouncementPriority.MEDIUM
    )
    target_roles = ArrayField(
        models.CharField(max_length=20, choices=User.Role.choices),
        verbose_name=_('rôles ciblés')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(_('date de début'))
    end_date = models.DateTimeField(_('date de fin'))
    is_active = models.BooleanField(_('active'), default=True)
    attachment = models.FileField(
        _('pièce jointe'),
        upload_to='announcements/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('annonce')
        verbose_name_plural = _('annonces')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
