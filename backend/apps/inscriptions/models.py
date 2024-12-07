from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel

class DossierInscription(TimestampedModel):
    """Modèle pour gérer les dossiers d'inscription des étudiants"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de traitement'),
        ('EN_COURS', 'En cours de traitement'),
        ('INCOMPLET', 'Dossier incomplet'),
        ('VALIDE', 'Dossier validé'),
        ('REJETE', 'Dossier rejeté'),
    ]

    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dossiers_inscription'
    )
    annee_academique = models.CharField(max_length=9)  # Format: 2023-2024
    niveau_etude = models.CharField(max_length=50)
    departement = models.ForeignKey(
        'departements.Departement',
        on_delete=models.CASCADE,
        related_name='dossiers_inscription'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )
    commentaires = models.TextField(blank=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Dossier d'inscription"
        verbose_name_plural = "Dossiers d'inscription"
        ordering = ['-date_soumission']

    def __str__(self):
        return f"Dossier de {self.etudiant.get_full_name()} - {self.annee_academique}"

class Document(TimestampedModel):
    """Modèle pour gérer les documents requis pour l'inscription"""
    TYPE_CHOICES = [
        ('IDENTITE', "Pièce d'identité"),
        ('DIPLOME', 'Diplôme'),
        ('RELEVE', 'Relevé de notes'),
        ('MEDICAL', 'Certificat médical'),
        ('PHOTO', 'Photo d\'identité'),
        ('AUTRE', 'Autre document'),
    ]

    dossier = models.ForeignKey(
        DossierInscription,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    type_document = models.CharField(max_length=20, choices=TYPE_CHOICES)
    fichier = models.FileField(upload_to='documents_inscription/')
    valide = models.BooleanField(default=False)
    commentaire = models.TextField(blank=True)

    class Meta:
        verbose_name = "Document d'inscription"
        verbose_name_plural = "Documents d'inscription"

    def __str__(self):
        return f"{self.get_type_document_display()} - {self.dossier.etudiant.get_full_name()}"

class Certificat(TimestampedModel):
    """Modèle pour gérer les certificats générés après inscription"""
    TYPE_CHOICES = [
        ('SCOLARITE', 'Certificat de scolarité'),
        ('INSCRIPTION', "Attestation d'inscription"),
        ('CARTE', 'Carte étudiante'),
    ]

    dossier = models.ForeignKey(
        DossierInscription,
        on_delete=models.CASCADE,
        related_name='certificats'
    )
    type_certificat = models.CharField(max_length=20, choices=TYPE_CHOICES)
    numero = models.CharField(max_length=50, unique=True)
    date_generation = models.DateTimeField(auto_now_add=True)
    fichier = models.FileField(upload_to='certificats/')
    valide_jusqu_au = models.DateField()

    class Meta:
        verbose_name = "Certificat"
        verbose_name_plural = "Certificats"
        ordering = ['-date_generation']

    def __str__(self):
        return f"{self.get_type_certificat_display()} - {self.numero}"
