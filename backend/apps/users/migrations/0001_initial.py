# Generated by Django 4.2.7 on 2024-12-06 21:08

from django.conf import settings
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="adresse email"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("ADMIN", "Administrateur"),
                            ("TEACHER", "Enseignant"),
                            ("STUDENT", "Étudiant"),
                        ],
                        default="STUDENT",
                        max_length=10,
                        verbose_name="rôle",
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        max_length=17,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Le numéro de téléphone doit être au format: '+999999999'.",
                                regex="^\\+?1?\\d{9,15}$",
                            )
                        ],
                        verbose_name="numéro de téléphone",
                    ),
                ),
                (
                    "profile_picture",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="profile_pictures/",
                        verbose_name="photo de profil",
                    ),
                ),
                (
                    "date_of_birth",
                    models.DateField(
                        blank=True, null=True, verbose_name="date de naissance"
                    ),
                ),
                ("address", models.TextField(blank=True, verbose_name="adresse")),
                ("bio", models.TextField(blank=True, verbose_name="biographie")),
                (
                    "failed_login_attempts",
                    models.PositiveIntegerField(
                        default=0, verbose_name="tentatives de connexion échouées"
                    ),
                ),
                (
                    "last_failed_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="dernière tentative échouée"
                    ),
                ),
                (
                    "account_locked_until",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="compte verrouillé jusqu'à"
                    ),
                ),
                (
                    "password_changed_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="dernier changement de mot de passe",
                    ),
                ),
                (
                    "two_factor_enabled",
                    models.BooleanField(
                        default=False,
                        verbose_name="authentification à deux facteurs activée",
                    ),
                ),
                (
                    "last_login_ip",
                    models.GenericIPAddressField(
                        blank=True, null=True, verbose_name="dernière IP de connexion"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "utilisateur",
                "verbose_name_plural": "utilisateurs",
                "ordering": ["-date_joined"],
            },
        ),
        migrations.CreateModel(
            name="TeacherProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "employee_id",
                    models.CharField(
                        max_length=20, unique=True, verbose_name="numéro employé"
                    ),
                ),
                (
                    "department",
                    models.CharField(max_length=100, verbose_name="département"),
                ),
                (
                    "specialization",
                    models.CharField(max_length=200, verbose_name="spécialisation"),
                ),
                ("hire_date", models.DateField(verbose_name="date d'embauche")),
                (
                    "office_location",
                    models.CharField(blank=True, max_length=100, verbose_name="bureau"),
                ),
                (
                    "office_hours",
                    models.TextField(blank=True, verbose_name="heures de bureau"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="teacher_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="utilisateur",
                    ),
                ),
            ],
            options={
                "verbose_name": "profil enseignant",
                "verbose_name_plural": "profils enseignants",
            },
        ),
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "student_id",
                    models.CharField(
                        max_length=20, unique=True, verbose_name="numéro étudiant"
                    ),
                ),
                (
                    "enrollment_date",
                    models.DateField(verbose_name="date d'inscription"),
                ),
                (
                    "current_semester",
                    models.PositiveIntegerField(verbose_name="semestre actuel"),
                ),
                ("major", models.CharField(max_length=100, verbose_name="filière")),
                (
                    "gpa",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=3,
                        null=True,
                        verbose_name="moyenne générale",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="utilisateur",
                    ),
                ),
            ],
            options={
                "verbose_name": "profil étudiant",
                "verbose_name_plural": "profils étudiants",
            },
        ),
    ]