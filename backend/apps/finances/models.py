from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel
from decimal import Decimal

class FraisScolarite(TimestampedModel):
    """Modèle pour définir les frais de scolarité par niveau et département"""
    CYCLE_CHOICES = [
        ('LICENCE', 'Licence'),
        ('MASTER', 'Master'),
        ('DOCTORAT', 'Doctorat'),
    ]

    departement = models.ForeignKey(
        'departements.Departement',
        on_delete=models.CASCADE,
        related_name='frais_scolarite'
    )
    cycle = models.CharField(max_length=20, choices=CYCLE_CHOICES)
    annee_academique = models.CharField(max_length=9)  # Format: 2023-2024
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_limite_paiement = models.DateField()
    
    class Meta:
        verbose_name = "Frais de scolarité"
        verbose_name_plural = "Frais de scolarité"
        unique_together = ['departement', 'cycle', 'annee_academique']

    def __str__(self):
        return f"{self.get_cycle_display()} - {self.departement} ({self.annee_academique})"

class Paiement(TimestampedModel):
    """Modèle pour gérer les paiements des étudiants"""
    TYPE_CHOICES = [
        ('SCOLARITE', 'Frais de scolarité'),
        ('INSCRIPTION', "Frais d'inscription"),
        ('EXAMEN', "Frais d'examen"),
        ('DOCUMENT', 'Frais de document'),
        ('AUTRE', 'Autre frais'),
    ]

    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDE', 'Validé'),
        ('REJETE', 'Rejeté'),
        ('REMBOURSE', 'Remboursé'),
    ]

    MODE_PAIEMENT_CHOICES = [
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CARTE_BANCAIRE', 'Carte Bancaire'),
        ('VIREMENT', 'Virement Bancaire'),
        ('ESPECES', 'Espèces'),
    ]

    etudiant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paiements'
    )
    dossier_inscription = models.ForeignKey(
        'inscriptions.DossierInscription',
        on_delete=models.CASCADE,
        related_name='paiements'
    )
    type_paiement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES)
    reference = models.CharField(max_length=50, unique=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )
    date_paiement = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire = models.TextField(blank=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']

    def __str__(self):
        return f"{self.reference} - {self.etudiant.get_full_name()}"

class Facture(TimestampedModel):
    """Modèle pour générer et gérer les factures"""
    paiement = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name='facture'
    )
    numero = models.CharField(max_length=50, unique=True)
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    fichier = models.FileField(upload_to='factures/', null=True, blank=True)

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-created_at']

    def __str__(self):
        return f"Facture {self.numero}"

    def save(self, *args, **kwargs):
        if not self.montant_ttc:
            self.montant_ttc = self.montant_ht * (1 + self.tva / 100)
        super().save(*args, **kwargs)

class RemboursementDemande(TimestampedModel):
    """Modèle pour gérer les demandes de remboursement"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de traitement'),
        ('EN_COURS', 'En cours de traitement'),
        ('APPROUVE', 'Approuvé'),
        ('REJETE', 'Rejeté'),
        ('COMPLETE', 'Remboursement effectué'),
    ]

    paiement = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name='demande_remboursement'
    )
    motif = models.TextField()
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )
    date_traitement = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(blank=True)
    documents_justificatifs = models.FileField(
        upload_to='remboursements/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Demande de remboursement"
        verbose_name_plural = "Demandes de remboursement"
        ordering = ['-created_at']

    def __str__(self):
        return f"Remboursement - {self.paiement.reference}"
