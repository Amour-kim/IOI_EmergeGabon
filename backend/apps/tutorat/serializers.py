from rest_framework import serializers
from django.utils import timezone
from .models import Tuteur, SeanceTutorat, Inscription, Evaluation, Support
from apps.departements.serializers import CoursListSerializer, DepartementSerializer

class TuteurListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des tuteurs"""
    nom_complet = serializers.CharField(
        source='utilisateur.get_full_name',
        read_only=True
    )
    niveau_display = serializers.CharField(
        source='get_niveau_display',
        read_only=True
    )
    departement_nom = serializers.CharField(
        source='departement.nom',
        read_only=True
    )
    nombre_seances = serializers.IntegerField(
        source='seances.count',
        read_only=True
    )

    class Meta:
        model = Tuteur
        fields = [
            'id', 'utilisateur', 'nom_complet', 'niveau',
            'niveau_display', 'departement', 'departement_nom',
            'note_moyenne', 'nombre_evaluations', 'nombre_seances',
            'statut'
        ]

class TuteurDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les tuteurs"""
    utilisateur_details = serializers.SerializerMethodField()
    niveau_display = serializers.CharField(
        source='get_niveau_display',
        read_only=True
    )
    departement_details = DepartementSerializer(
        source='departement',
        read_only=True
    )
    specialites_details = CoursListSerializer(
        source='specialites',
        many=True,
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )

    class Meta:
        model = Tuteur
        fields = [
            'id', 'utilisateur', 'utilisateur_details', 'niveau',
            'niveau_display', 'departement', 'departement_details',
            'specialites', 'specialites_details', 'cv', 'biographie',
            'disponibilites', 'statut', 'statut_display',
            'note_moyenne', 'nombre_evaluations', 'date_validation',
            'commentaire_admin'
        ]
        read_only_fields = [
            'note_moyenne', 'nombre_evaluations',
            'date_validation', 'commentaire_admin'
        ]

    def get_utilisateur_details(self, obj):
        """Retourne les détails de l'utilisateur"""
        return {
            'id': obj.utilisateur.id,
            'nom_complet': obj.utilisateur.get_full_name(),
            'email': obj.utilisateur.email
        }

    def validate_cv(self, value):
        """Valide le fichier CV"""
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise serializers.ValidationError(
                "La taille du CV ne doit pas dépasser 5MB"
            )
        return value

class SeanceTutoratListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des séances de tutorat"""
    tuteur_nom = serializers.CharField(
        source='tuteur.utilisateur.get_full_name',
        read_only=True
    )
    cours_nom = serializers.CharField(
        source='cours.intitule',
        read_only=True
    )
    type_seance_display = serializers.CharField(
        source='get_type_seance_display',
        read_only=True
    )
    modalite_display = serializers.CharField(
        source='get_modalite_display',
        read_only=True
    )
    places_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = SeanceTutorat
        fields = [
            'id', 'tuteur', 'tuteur_nom', 'cours', 'cours_nom',
            'type_seance', 'type_seance_display', 'modalite',
            'modalite_display', 'date_debut', 'date_fin', 'lieu',
            'capacite_max', 'places_disponibles', 'tarif_horaire',
            'statut'
        ]

    def get_places_disponibles(self, obj):
        """Calcule le nombre de places disponibles"""
        return obj.capacite_max - obj.inscriptions.filter(
            statut='CONFIRMEE'
        ).count()

class SeanceTutoratDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les séances de tutorat"""
    tuteur_details = TuteurListSerializer(source='tuteur', read_only=True)
    cours_details = CoursListSerializer(source='cours', read_only=True)
    type_seance_display = serializers.CharField(
        source='get_type_seance_display',
        read_only=True
    )
    modalite_display = serializers.CharField(
        source='get_modalite_display',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    inscrits = serializers.SerializerMethodField()
    supports_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = SeanceTutorat
        fields = '__all__'

    def get_inscrits(self, obj):
        """Retourne la liste des inscrits confirmés"""
        return [{
            'id': insc.etudiant.id,
            'nom_complet': insc.etudiant.get_full_name(),
            'presence_confirmee': insc.presence_confirmee,
            'date_inscription': insc.date_inscription
        } for insc in obj.inscriptions.filter(statut='CONFIRMEE')]

    def get_supports_disponibles(self, obj):
        """Retourne la liste des supports disponibles"""
        return [{
            'id': support.id,
            'titre': support.titre,
            'type': support.get_type_support_display(),
            'description': support.description
        } for support in obj.supports.all()]

    def validate(self, data):
        """Validation personnalisée"""
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

class InscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour les inscriptions aux séances"""
    etudiant_nom = serializers.CharField(
        source='etudiant.get_full_name',
        read_only=True
    )
    seance_details = SeanceTutoratListSerializer(
        source='seance',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )

    class Meta:
        model = Inscription
        fields = '__all__'
        read_only_fields = ['etudiant', 'date_inscription', 'presence_confirmee']

class EvaluationSerializer(serializers.ModelSerializer):
    """Serializer pour les évaluations"""
    etudiant_nom = serializers.CharField(
        source='etudiant.get_full_name',
        read_only=True
    )
    seance_details = SeanceTutoratListSerializer(
        source='seance',
        read_only=True
    )

    class Meta:
        model = Evaluation
        fields = '__all__'
        read_only_fields = ['etudiant', 'date_evaluation']

    def validate_note(self, value):
        """Vérifie que la note est entre 1 et 5"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "La note doit être comprise entre 1 et 5"
            )
        return value

class SupportSerializer(serializers.ModelSerializer):
    """Serializer pour les supports de cours"""
    type_support_display = serializers.CharField(
        source='get_type_support_display',
        read_only=True
    )

    class Meta:
        model = Support
        fields = '__all__'
        read_only_fields = ['date_publication']

    def validate_fichier(self, value):
        """Valide la taille du fichier"""
        max_size = 20 * 1024 * 1024  # 20MB
        if value.size > max_size:
            raise serializers.ValidationError(
                "La taille du fichier ne doit pas dépasser 20MB"
            )
        return value
