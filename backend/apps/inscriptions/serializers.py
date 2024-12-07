from rest_framework import serializers
from .models import DossierInscription, Document, Certificat

class DocumentSerializer(serializers.ModelSerializer):
    """Serializer pour les documents d'inscription"""
    type_document_display = serializers.CharField(source='get_type_document_display', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'type_document', 'type_document_display', 'fichier',
            'valide', 'commentaire', 'created_at', 'updated_at'
        ]

class CertificatSerializer(serializers.ModelSerializer):
    """Serializer pour les certificats"""
    type_certificat_display = serializers.CharField(source='get_type_certificat_display', read_only=True)

    class Meta:
        model = Certificat
        fields = [
            'id', 'type_certificat', 'type_certificat_display', 'numero',
            'date_generation', 'fichier', 'valide_jusqu_au'
        ]

class DossierInscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour les dossiers d'inscription"""
    documents = DocumentSerializer(many=True, read_only=True)
    certificats = CertificatSerializer(many=True, read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    etudiant_nom = serializers.CharField(source='etudiant.get_full_name', read_only=True)

    class Meta:
        model = DossierInscription
        fields = [
            'id', 'etudiant', 'etudiant_nom', 'annee_academique',
            'niveau_etude', 'departement', 'statut', 'statut_display',
            'commentaires', 'date_soumission', 'date_validation',
            'documents', 'certificats', 'created_at', 'updated_at'
        ]
        read_only_fields = ['etudiant', 'date_soumission', 'date_validation']

    def validate_annee_academique(self, value):
        """Valide le format de l'année académique (YYYY-YYYY)"""
        try:
            debut, fin = map(int, value.split('-'))
            if fin != debut + 1:
                raise serializers.ValidationError(
                    "L'année de fin doit être l'année suivante de l'année de début"
                )
            if len(str(debut)) != 4 or len(str(fin)) != 4:
                raise serializers.ValidationError(
                    "Le format de l'année doit être YYYY-YYYY"
                )
        except ValueError:
            raise serializers.ValidationError(
                "Le format de l'année académique doit être YYYY-YYYY"
            )
        return value

class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de documents"""
    class Meta:
        model = Document
        fields = ['type_document', 'fichier', 'dossier']

    def validate_fichier(self, value):
        """Valide la taille et le type du fichier"""
        # Limite de 5MB
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                "La taille du fichier ne doit pas dépasser 5MB"
            )
        # Vérification des extensions autorisées
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        ext = str(value.name).lower()[-4:]
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Le type de fichier doit être parmi : {', '.join(allowed_extensions)}"
            )
        return value
