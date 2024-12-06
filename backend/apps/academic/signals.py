from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Grade, Attendance
from apps.messaging.models import Notification

@receiver(post_save, sender=Grade)
def notify_grade(sender, instance, created, **kwargs):
    """
    Signal to create notifications when a grade is added or updated
    """
    if created:
        action = "ajoutée"
    else:
        action = "modifiée"

    # Notify student
    Notification.objects.create(
        recipient=instance.student,
        title=f"Note {action} en {instance.course.title}",
        message=f"Une note de {instance.score}/20 a été {action} pour le cours {instance.course.title}."
    )

@receiver(post_save, sender=Attendance)
def notify_attendance(sender, instance, created, **kwargs):
    """
    Signal to create notifications when attendance is marked
    """
    if created and not instance.is_present:
        # Notify student of absence
        Notification.objects.create(
            recipient=instance.student,
            title=f"Absence en {instance.course.title}",
            message=f"Vous avez été marqué absent au cours de {instance.course.title} du {instance.date}."
        )

    if instance.validated:
        # Notify student of validation
        Notification.objects.create(
            recipient=instance.student,
            title=f"Absence justifiée en {instance.course.title}",
            message=f"Votre absence au cours de {instance.course.title} du {instance.date} a été justifiée."
        )
