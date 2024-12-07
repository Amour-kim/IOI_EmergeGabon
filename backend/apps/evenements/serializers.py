from rest_framework import serializers
from django.utils import timezone
from .models import Evenement, Inscription, Document, Feedback
from apps.departements.serializers import DepartementSerializer

class DocumentSerializer(serializers.ModelSerializer):
    """Serializer pour les documents d'événements"""
    type_document_display = serializers.CharField(
        source='get_type_document_display',
        read_only=True
    )

    class Meta:
        model = Document
        fields = [
            'id', 'evenement', 'titre', 'type_document',
            'type_document_display', 'fichier', 'description',
            'date_publication', 'public'
        ]
        read_only_fields = ['date_publication']

    def validate_fichier(self, value):
        """Valide la taille et le type du fichier"""
        max_size = 20 * 1024 * 1024  # 20MB
        if value.size > max_size:
            raise serializers.ValidationError(
                "La taille du fichier ne doit pas dépasser 20MB"
            )
        return value

class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer pour les feedbacks"""
    participant_nom = serializers.CharField(
        source='participant.get_full_name',
        read_only=True
    )

    class Meta:
        model = Feedback
        fields = [
            'id', 'evenement', 'participant', 'participant_nom',
            'note', 'commentaire', 'points_positifs',
            'points_amelioration', 'date_feedback', 'anonyme'
        ]
        read_only_fields = ['participant', 'date_feedback']

    def validate_note(self, value):
        """Vérifie que la note est entre 1 et 5"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "La note doit être comprise entre 1 et 5"
            )
        return value

class InscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour les inscriptions aux événements"""
    participant_nom = serializers.CharField(
        source='participant.get_full_name',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )

    class Meta:
        model = Inscription
        fields = [
            'id', 'evenement', 'participant', 'participant_nom',
            'statut', 'statut_display', 'date_inscription',
            'commentaire', 'presence_confirmee', 'certificat_genere'
        ]
        read_only_fields = [
            'participant', 'date_inscription',
            'presence_confirmee', 'certificat_genere'
        ]

class EvenementListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des événements"""
    type_evenement_display = serializers.CharField(
        source='get_type_evenement_display',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    organisateur_nom = serializers.CharField(
        source='organisateur.get_full_name',
        read_only=True
    )
    nombre_inscrits = serializers.IntegerField(
        source='inscriptions.count',
        read_only=True
    )

    class Meta:
        model = Evenement
        fields = [
            'id', 'titre', 'type_evenement', 'type_evenement_display',
            'date_debut', 'date_fin', 'lieu', 'image', 'statut',
            'statut_display', 'places_disponibles', 'organisateur_nom',
            'nombre_inscrits', 'cout'
        ]

class EvenementDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les événements"""
    type_evenement_display = serializers.CharField(
        source='get_type_evenement_display',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    organisateur_details = serializers.SerializerMethodField()
    departements_details = DepartementSerializer(
        source='departements',
        many=True,
        read_only=True
    )
    documents_publics = serializers.SerializerMethodField()
    nombre_inscrits = serializers.IntegerField(
        source='inscriptions.count',
        read_only=True
    )
    note_moyenne = serializers.SerializerMethodField()

    class Meta:
        model = Evenement
        fields = [
            'id', 'titre', 'type_evenement', 'type_evenement_display',
            'description', 'date_debut', 'date_fin', 'lieu', 'capacite',
            'organisateur', 'organisateur_details', 'departements',
            'departements_details', 'image', 'inscription_requise',
            'places_disponibles', 'statut', 'statut_display',
            'public_cible', 'contact_email', 'contact_telephone',
            'site_web', 'cout', 'documents_publics', 'nombre_inscrits',
            'note_moyenne'
        ]
        read_only_fields = ['places_disponibles']

    def get_organisateur_details(self, obj):
        """Retourne les détails de l'organisateur"""
        return {
            'id': obj.organisateur.id,
            'nom': obj.organisateur.get_full_name(),
            'email': obj.organisateur.email
        }

    def get_documents_publics(self, obj):
        """Retourne la liste des documents publics"""
        documents = obj.documents.filter(public=True)
        return DocumentSerializer(documents, many=True).data

    def get_note_moyenne(self, obj):
        """Calcule la note moyenne des feedbacks"""
        feedbacks = obj.feedbacks.all()
        if not feedbacks:
            return None
        return sum(f.note for f in feedbacks) / len(feedbacks)

    def validate(self, data):
        """Validation personnalisée pour les dates"""
        if data.get('date_debut') and data.get('date_fin'):
            if data['date_debut'] >= data['date_fin']:
                raise serializers.ValidationError(
                    "La date de fin doit être postérieure à la date de début"
                )
            if data['date_debut'] < timezone.now():
                raise serializers.ValidationError(
                    "La date de début doit être dans le futur"
                )
        return data
