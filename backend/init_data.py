import os
import django
from django.utils import timezone
from datetime import timedelta

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import StudentProfile, TeacherProfile
from apps.courses.models import Course, Module, Content
from apps.academic.models import AcademicYear, Semester
from apps.community.models import Community, Tag

User = get_user_model()

def create_test_data():
    print("Création des données de test...")

    # Créer des utilisateurs
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@gabon-edu.com',
        password='admin123',
        first_name='Admin',
        last_name='System',
        role='ADMIN'
    )

    teacher1 = User.objects.create_user(
        username='prof1',
        email='prof1@gabon-edu.com',
        password='prof123',
        first_name='Jean',
        last_name='Dupont',
        role='TEACHER'
    )
    TeacherProfile.objects.create(
        user=teacher1,
        employee_id='TCH001',
        department='Informatique',
        specialization='Programmation',
        hire_date=timezone.now().date()
    )

    student1 = User.objects.create_user(
        username='etudiant1',
        email='etudiant1@gabon-edu.com',
        password='etudiant123',
        first_name='Marie',
        last_name='Claire',
        role='STUDENT'
    )
    StudentProfile.objects.create(
        user=student1,
        student_id='STD001',
        enrollment_date=timezone.now().date(),
        current_semester=1,
        major='Informatique'
    )

    # Créer une année académique et des semestres
    academic_year = AcademicYear.objects.create(
        year='2023-2024',
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=365),
        is_current=True
    )

    semester = Semester.objects.create(
        academic_year=academic_year,
        number=1,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=180),
        is_current=True
    )

    # Créer un cours
    course = Course.objects.create(
        title='Introduction à la Programmation Python',
        code='INF101',
        description='Cours d\'introduction à la programmation avec Python',
        credits=6,
        level='L1',
        language='fr'
    )
    course.teachers.add(TeacherProfile.objects.get(user=teacher1))

    # Créer des modules
    module1 = Module.objects.create(
        course=course,
        title='Les bases de Python',
        description='Introduction aux concepts de base',
        order=1
    )

    Content.objects.create(
        module=module1,
        title='Variables et Types',
        content_type='DOCUMENT',
        description='Introduction aux variables et types de données en Python',
        order=1
    )

    # Créer des tags pour la communauté
    tag_info = Tag.objects.create(
        name='Informatique',
        slug='informatique',
        description='Discussions sur l\'informatique'
    )

    tag_python = Tag.objects.create(
        name='Python',
        slug='python',
        description='Tout sur Python'
    )

    # Créer une communauté
    community = Community.objects.create(
        name='Club de Programmation',
        slug='club-programmation',
        description='Communauté des passionnés de programmation',
        creator=teacher1
    )
    community.tags.add(tag_info, tag_python)

    print("Données de test créées avec succès!")

if __name__ == '__main__':
    create_test_data()
