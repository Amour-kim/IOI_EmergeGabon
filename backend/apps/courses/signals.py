from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment
from apps.messaging.models import Notification

@receiver(post_save, sender=Enrollment)
def notify_enrollment(sender, instance, created, **kwargs):
    """
    Signal to create notifications when a student enrolls in a course
    """
    if created:
        # Notify student
        Notification.objects.create(
            recipient=instance.student,
            title=f"Inscription au cours {instance.course.title}",
            message=f"Vous êtes maintenant inscrit au cours {instance.course.title}."
        )
        
        # Notify teachers
        for teacher in instance.course.teachers.all():
            Notification.objects.create(
                recipient=teacher.user,
                title=f"Nouvel étudiant inscrit",
                message=f"{instance.student.get_full_name()} s'est inscrit à votre cours {instance.course.title}."
            )
