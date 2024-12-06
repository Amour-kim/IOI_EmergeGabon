from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Announcement
from .models import Notification

@receiver(post_save, sender=Message)
def notify_new_message(sender, instance, created, **kwargs):
    """
    Signal to create notifications for new messages
    """
    if created:
        # Create notifications for all participants except sender
        for participant in instance.conversation.participants.exclude(id=instance.sender.id):
            Notification.objects.create(
                recipient=participant,
                type=Notification.NotificationType.INFO,
                title='Nouveau message',
                message=f'Nouveau message de {instance.sender.get_full_name()} dans {instance.conversation}',
                link=f'/conversations/{instance.conversation.id}'
            )

@receiver(post_save, sender=Announcement)
def notify_announcement(sender, instance, created, **kwargs):
    """
    Signal to create notifications for new announcements
    """
    if created:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Create notifications for all users with matching roles
        users = User.objects.filter(role__in=instance.target_roles)
        
        notifications = [
            Notification(
                recipient=user,
                type=Notification.NotificationType.INFO,
                title=f'Nouvelle annonce : {instance.title}',
                message=instance.content[:100] + '...' if len(instance.content) > 100 else instance.content,
                link=f'/announcements/{instance.id}'
            )
            for user in users
        ]
        
        Notification.objects.bulk_create(notifications)
