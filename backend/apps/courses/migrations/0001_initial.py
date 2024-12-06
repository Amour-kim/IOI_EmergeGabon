# Generated by Django 4.2.7 on 2024-12-06 21:08

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
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
                ("title", models.CharField(max_length=200, verbose_name="titre")),
                (
                    "code",
                    models.CharField(max_length=20, unique=True, verbose_name="code"),
                ),
                ("description", models.TextField(verbose_name="description")),
                (
                    "credits",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(30),
                        ],
                        verbose_name="crédits",
                    ),
                ),
                (
                    "capacity",
                    models.PositiveIntegerField(
                        default=50,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="capacité",
                    ),
                ),
                (
                    "start_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="date de début"
                    ),
                ),
                (
                    "end_date",
                    models.DateField(blank=True, null=True, verbose_name="date de fin"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="actif")),
                (
                    "language",
                    models.CharField(
                        choices=[("fr", "Français"), ("en", "Anglais")],
                        default="fr",
                        max_length=10,
                        verbose_name="langue",
                    ),
                ),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("L1", "Licence 1"),
                            ("L2", "Licence 2"),
                            ("L3", "Licence 3"),
                            ("M1", "Master 1"),
                            ("M2", "Master 2"),
                            ("D", "Doctorat"),
                        ],
                        max_length=20,
                        verbose_name="niveau",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "prerequisites",
                    models.ManyToManyField(
                        blank=True,
                        related_name="is_prerequisite_for",
                        to="courses.course",
                        verbose_name="prérequis",
                    ),
                ),
                (
                    "teachers",
                    models.ManyToManyField(
                        related_name="teaching_courses",
                        to="users.teacherprofile",
                        verbose_name="enseignants",
                    ),
                ),
            ],
            options={
                "verbose_name": "cours",
                "verbose_name_plural": "cours",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Module",
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
                ("title", models.CharField(max_length=200, verbose_name="titre")),
                ("description", models.TextField(verbose_name="description")),
                ("order", models.PositiveIntegerField(verbose_name="ordre")),
                (
                    "duration",
                    models.DurationField(
                        blank=True,
                        help_text="Durée estimée du module",
                        null=True,
                        verbose_name="durée",
                    ),
                ),
                (
                    "is_required",
                    models.BooleanField(default=True, verbose_name="obligatoire"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="modules",
                        to="courses.course",
                        verbose_name="cours",
                    ),
                ),
            ],
            options={
                "verbose_name": "module",
                "verbose_name_plural": "modules",
                "ordering": ["course", "order"],
            },
        ),
        migrations.CreateModel(
            name="Enrollment",
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
                ("enrollment_date", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True, verbose_name="actif")),
                (
                    "completed",
                    models.BooleanField(default=False, verbose_name="terminé"),
                ),
                (
                    "completion_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="date de fin"
                    ),
                ),
                (
                    "progress",
                    models.FloatField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="progression",
                    ),
                ),
                (
                    "last_accessed",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="dernier accès"
                    ),
                ),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="courses.course",
                        verbose_name="cours",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="étudiant",
                    ),
                ),
            ],
            options={
                "verbose_name": "inscription",
                "verbose_name_plural": "inscriptions",
                "ordering": ["-enrollment_date"],
            },
        ),
        migrations.CreateModel(
            name="Content",
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
                ("title", models.CharField(max_length=200, verbose_name="titre")),
                (
                    "content_type",
                    models.CharField(
                        choices=[
                            ("VIDEO", "Vidéo"),
                            ("DOCUMENT", "Document"),
                            ("QUIZ", "Quiz"),
                            ("ASSIGNMENT", "Devoir"),
                            ("LINK", "Lien externe"),
                            ("CODE", "Code source"),
                        ],
                        max_length=20,
                        verbose_name="type de contenu",
                    ),
                ),
                ("description", models.TextField(verbose_name="description")),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="course_contents/",
                        verbose_name="fichier",
                    ),
                ),
                ("url", models.URLField(blank=True, null=True, verbose_name="URL")),
                (
                    "duration",
                    models.DurationField(
                        blank=True,
                        help_text="Durée estimée du contenu",
                        null=True,
                        verbose_name="durée",
                    ),
                ),
                ("order", models.PositiveIntegerField(verbose_name="ordre")),
                (
                    "is_required",
                    models.BooleanField(default=True, verbose_name="obligatoire"),
                ),
                (
                    "points",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Points attribués pour ce contenu",
                        verbose_name="points",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contents",
                        to="courses.module",
                        verbose_name="module",
                    ),
                ),
            ],
            options={
                "verbose_name": "contenu",
                "verbose_name_plural": "contenus",
                "ordering": ["module", "order"],
            },
        ),
        migrations.AddIndex(
            model_name="module",
            index=models.Index(
                fields=["course", "order"], name="courses_mod_course__20183c_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="module",
            unique_together={("course", "order")},
        ),
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(
                fields=["student", "course"], name="courses_enr_student_774ec5_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(
                fields=["is_active"], name="courses_enr_is_acti_b4e128_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="enrollment",
            index=models.Index(
                fields=["completed"], name="courses_enr_complet_93b8c9_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="enrollment",
            unique_together={("student", "course")},
        ),
        migrations.AddIndex(
            model_name="course",
            index=models.Index(fields=["code"], name="courses_cou_code_612388_idx"),
        ),
        migrations.AddIndex(
            model_name="course",
            index=models.Index(fields=["level"], name="courses_cou_level_bf0a39_idx"),
        ),
        migrations.AddIndex(
            model_name="course",
            index=models.Index(
                fields=["is_active"], name="courses_cou_is_acti_3c7e41_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="content",
            index=models.Index(
                fields=["module", "order"], name="courses_con_module__93918d_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="content",
            index=models.Index(
                fields=["content_type"], name="courses_con_content_9ee56a_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="content",
            unique_together={("module", "order")},
        ),
    ]