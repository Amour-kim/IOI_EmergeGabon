from rest_framework import serializers
from .models import FraisScolarite, Paiement, Facture, RemboursementDemande
from django.utils import timezone

class FraisScolariteSerializer(serializers.ModelSerializer):
    """Serializer pour les frais de scolarité"""
    cycle_display = serializers.CharField(source='get_cycle_display', read_only=True)
    departement_nom = serializers.CharField(source='departement.nom', read_only=True)

    class Meta:
        model = FraisScolarite
        fields = [
            'id', 'departement', 'departement_nom', 'cycle', 'cycle_display',
            'annee_academique', 'montant', 'date_limite_paiement'
        ]

    def validate_date_limite_paiement(self, value):
        """Vérifie que la date limite est dans le futur"""
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "La date limite de paiement doit être dans le futur"
            )
        return value

class PaiementSerializer(serializers.ModelSerializer):
    """Serializer pour les paiements"""
    type_paiement_display = serializers.CharField(
        source='get_type_paiement_display',
        read_only=True
    )
    mode_paiement_display = serializers.CharField(
        source='get_mode_paiement_display',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    etudiant_nom = serializers.CharField(
        source='etudiant.get_full_name',
        read_only=True
    )

    class Meta:
        model = Paiement
        fields = [
            'id', 'etudiant', 'etudiant_nom', 'dossier_inscription',
            'type_paiement', 'type_paiement_display', 'montant',
            'mode_paiement', 'mode_paiement_display', 'reference',
            'statut', 'statut_display', 'date_paiement',
            'date_validation', 'commentaire'
        ]
        read_only_fields = ['etudiant', 'reference', 'date_validation']

    def create(self, validated_data):
        # Génération automatique de la référence
        validated_data['reference'] = f"PAY-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        return super().create(validated_data)

class FactureSerializer(serializers.ModelSerializer):
    """Serializer pour les factures"""
    paiement_reference = serializers.CharField(source='paiement.reference', read_only=True)
    etudiant_nom = serializers.CharField(
        source='paiement.etudiant.get_full_name',
        read_only=True
    )

    class Meta:
        model = Facture
        fields = [
            'id', 'paiement', 'paiement_reference', 'etudiant_nom',
            'numero', 'montant_ht', 'tva', 'montant_ttc', 'fichier'
        ]
        read_only_fields = ['numero', 'montant_ttc']

    def create(self, validated_data):
        # Génération automatique du numéro de facture
        validated_data['numero'] = f"FAC-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        return super().create(validated_data)

class RemboursementDemandeSerializer(serializers.ModelSerializer):
    """Serializer pour les demandes de remboursement"""
    paiement_reference = serializers.CharField(source='paiement.reference', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    etudiant_nom = serializers.CharField(
        source='paiement.etudiant.get_full_name',
        read_only=True
    )

    class Meta:
        model = RemboursementDemande
        fields = [
            'id', 'paiement', 'paiement_reference', 'etudiant_nom',
            'motif', 'statut', 'statut_display', 'date_traitement',
            'commentaire_admin', 'documents_justificatifs'
        ]
        read_only_fields = ['date_traitement', 'commentaire_admin']

    def validate_paiement(self, value):
        """Vérifie que le paiement peut être remboursé"""
        if value.statut not in ['VALIDE', 'EN_ATTENTE']:
            raise serializers.ValidationError(
                "Seuls les paiements validés ou en attente peuvent faire l'objet d'un remboursement"
            )
        if hasattr(value, 'demande_remboursement'):
            raise serializers.ValidationError(
                "Une demande de remboursement existe déjà pour ce paiement"
            )
        return value
