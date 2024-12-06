from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile, TeacherProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create the appropriate profile when a user is created
    """
    if created:
        if instance.role == User.Role.STUDENT:
            StudentProfile.objects.create(
                user=instance,
                student_id=f"STD{instance.id:06d}",
                enrollment_date=instance.date_joined.date(),
                current_semester=1
            )
        elif instance.role == User.Role.TEACHER:
            TeacherProfile.objects.create(
                user=instance,
                employee_id=f"TCH{instance.id:06d}",
                hire_date=instance.date_joined.date()
            )
