from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    Community, CommunityMembership, MembershipRequest,
    Discussion, Comment, Report
)
from apps.messaging.models import Notification

@receiver(post_save, sender=Community)
def create_community_membership(sender, instance, created, **kwargs):
    """Créer automatiquement une adhésion pour le créateur"""
    if created and instance.creator:
        CommunityMembership.objects.create(
            user=instance.creator,
            community=instance,
            role=CommunityMembership.Role.ADMIN
        )

@receiver(post_save, sender=MembershipRequest)
def handle_membership_request(sender, instance, created, **kwargs):
    """Gérer les notifications pour les demandes d'adhésion"""
    if created:
        # Notifier les administrateurs
        admins = instance.community.memberships.filter(
            role=CommunityMembership.Role.ADMIN
        )
        for admin in admins:
            Notification.objects.create(
                recipient=admin.user,
                title=f"Nouvelle demande d'adhésion",
                message=(
                    f"{instance.user.get_full_name()} souhaite rejoindre "
                    f"la communauté {instance.community.name}"
                )
            )
    elif instance.status != 'PENDING':
        # Notifier le demandeur
        status_message = (
            "acceptée" if instance.status == 'APPROVED'
            else "rejetée"
        )
        Notification.objects.create(
            recipient=instance.user,
            title=f"Demande d'adhésion {status_message}",
            message=(
                f"Votre demande d'adhésion à la communauté "
                f"{instance.community.name} a été {status_message}."
            )
        )

@receiver(post_save, sender=Discussion)
def notify_new_discussion(sender, instance, created, **kwargs):
    """Notifier les membres de la communauté d'une nouvelle discussion"""
    if created:
        members = instance.community.members.exclude(
            id=instance.author.id
        )
        notifications = [
            Notification(
                recipient=member,
                title=f"Nouvelle discussion dans {instance.community.name}",
                message=(
                    f"{instance.author.get_full_name()} a créé une nouvelle "
                    f"discussion : {instance.title}"
                )
            )
            for member in members
        ]
        Notification.objects.bulk_create(notifications)

@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    """Notifier les personnes concernées par un nouveau commentaire"""
    if created:
        # Notifier l'auteur de la discussion
        if instance.author != instance.discussion.author:
            Notification.objects.create(
                recipient=instance.discussion.author,
                title="Nouveau commentaire sur votre discussion",
                message=(
                    f"{instance.author.get_full_name()} a commenté votre "
                    f"discussion : {instance.discussion.title}"
                )
            )
        
        # Notifier l'auteur du commentaire parent
        if instance.parent and instance.parent.author != instance.author:
            Notification.objects.create(
                recipient=instance.parent.author,
                title="Nouvelle réponse à votre commentaire",
                message=(
                    f"{instance.author.get_full_name()} a répondu à votre "
                    f"commentaire dans la discussion : {instance.discussion.title}"
                )
            )

@receiver(post_save, sender=Report)
def handle_report(sender, instance, created, **kwargs):
    """Notifier les modérateurs des nouveaux signalements"""
    if created:
        moderators = instance.community.memberships.filter(
            role__in=[
                CommunityMembership.Role.MODERATOR,
                CommunityMembership.Role.ADMIN
            ]
        )
        notifications = [
            Notification(
                recipient=mod.user,
                title=f"Nouveau signalement dans {instance.community.name}",
                message=(
                    f"Un contenu a été signalé par {instance.reporter.get_full_name()}. "
                    f"Raison : {instance.reason[:100]}..."
                )
            )
            for mod in moderators
        ]
        Notification.objects.bulk_create(notifications)

@receiver(pre_save, sender=CommunityMembership)
def handle_member_ban(sender, instance, **kwargs):
    """Gérer les notifications de bannissement"""
    try:
        old_instance = CommunityMembership.objects.get(pk=instance.pk)
        if not old_instance.is_banned and instance.is_banned:
            Notification.objects.create(
                recipient=instance.user,
                title=f"Banni de {instance.community.name}",
                message=(
                    f"Vous avez été banni de la communauté. "
                    f"Raison : {instance.ban_reason}"
                )
            )
    except CommunityMembership.DoesNotExist:
        pass  # Nouvelle instance
