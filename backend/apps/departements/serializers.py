from rest_framework import serializers
from .models import Faculte, Departement, Programme, Cours
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer basique pour les informations d'utilisateur"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']

class FaculteSerializer(serializers.ModelSerializer):
    """Serializer pour les facultés"""
    doyen_details = UserBasicSerializer(source='doyen', read_only=True)
    nombre_departements = serializers.IntegerField(
        source='departements.count',
        read_only=True
    )

    class Meta:
        model = Faculte
        fields = [
            'id', 'nom', 'code', 'description', 'doyen', 'doyen_details',
            'date_creation', 'site_web', 'email_contact', 'telephone',
            'adresse', 'nombre_departements'
        ]

class DepartementSerializer(serializers.ModelSerializer):
    """Serializer pour les départements"""
    faculte_nom = serializers.CharField(source='faculte.nom', read_only=True)
    chef_departement_details = UserBasicSerializer(
        source='chef_departement',
        read_only=True
    )
    nombre_programmes = serializers.IntegerField(
        source='programmes.count',
        read_only=True
    )

    class Meta:
        model = Departement
        fields = [
            'id', 'faculte', 'faculte_nom', 'nom', 'code', 'description',
            'chef_departement', 'chef_departement_details', 'date_creation',
            'capacite_accueil', 'email_contact', 'telephone', 'bureau',
            'nombre_programmes'
        ]

    def validate_capacite_accueil(self, value):
        """Vérifie que la capacité d'accueil est raisonnable"""
        if value < 1:
            raise serializers.ValidationError(
                "La capacité d'accueil doit être supérieure à 0"
            )
        if value > 1000:  # À ajuster selon les besoins
            raise serializers.ValidationError(
                "La capacité d'accueil semble trop élevée"
            )
        return value

class ProgrammeListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des programmes"""
    departement_nom = serializers.CharField(source='departement.nom', read_only=True)
    niveau_display = serializers.CharField(source='get_niveau_display', read_only=True)
    nombre_cours = serializers.IntegerField(source='cours.count', read_only=True)

    class Meta:
        model = Programme
        fields = [
            'id', 'departement', 'departement_nom', 'nom', 'code',
            'niveau', 'niveau_display', 'duree', 'credits_requis',
            'est_actif', 'nombre_cours'
        ]

class ProgrammeDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les programmes"""
    departement_details = DepartementSerializer(source='departement', read_only=True)
    responsable_details = UserBasicSerializer(source='responsable', read_only=True)
    niveau_display = serializers.CharField(source='get_niveau_display', read_only=True)

    class Meta:
        model = Programme
        fields = [
            'id', 'departement', 'departement_details', 'nom', 'code',
            'niveau', 'niveau_display', 'description', 'duree',
            'credits_requis', 'responsable', 'responsable_details',
            'conditions_admission', 'debouches', 'est_actif'
        ]

class CoursListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des cours"""
    programme_nom = serializers.CharField(source='programme.nom', read_only=True)
    type_cours_display = serializers.CharField(
        source='get_type_cours_display',
        read_only=True
    )

    class Meta:
        model = Cours
        fields = [
            'id', 'programme', 'programme_nom', 'code', 'intitule',
            'credits', 'type_cours', 'type_cours_display', 'semestre',
            'est_actif'
        ]

class CoursDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les cours"""
    programme_details = ProgrammeListSerializer(source='programme', read_only=True)
    enseignant_details = UserBasicSerializer(
        source='enseignant_responsable',
        read_only=True
    )
    type_cours_display = serializers.CharField(
        source='get_type_cours_display',
        read_only=True
    )
    prerequis_details = CoursListSerializer(many=True, read_only=True)

    class Meta:
        model = Cours
        fields = [
            'id', 'programme', 'programme_details', 'code', 'intitule',
            'description', 'credits', 'volume_horaire', 'type_cours',
            'type_cours_display', 'prerequis', 'prerequis_details',
            'enseignant_responsable', 'enseignant_details', 'semestre',
            'objectifs', 'contenu', 'methode_evaluation', 'est_actif'
        ]

    def validate_credits(self, value):
        """Vérifie que le nombre de crédits est valide"""
        if value < 1:
            raise serializers.ValidationError(
                "Le nombre de crédits doit être supérieur à 0"
            )
        if value > 30:  # À ajuster selon les normes de l'université
            raise serializers.ValidationError(
                "Le nombre de crédits semble trop élevé"
            )
        return value

    def validate_semestre(self, value):
        """Vérifie que le numéro du semestre est valide"""
        if value < 1:
            raise serializers.ValidationError(
                "Le numéro du semestre doit être supérieur à 0"
            )
        if value > 10:  # Pour couvrir jusqu'au doctorat
            raise serializers.ValidationError(
                "Le numéro du semestre semble trop élevé"
            )
        return value
