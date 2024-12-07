from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from .models import (
    Categorie,
    Ressource,
    Evaluation,
    Telechargement,
    Collection
)
from apps.departements.serializers import (
    DepartementSerializer,
    CoursSerializer
)

class CategorieListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des catégories"""
    nombre_ressources = serializers.IntegerField(
        source='ressources.count',
        read_only=True
    )
    
    class Meta:
        model = Categorie
        fields = [
            'id', 'nom', 'description', 'parent',
            'ordre', 'nombre_ressources'
        ]

class CategorieDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les catégories"""
    sous_categories = CategorieListSerializer(many=True, read_only=True)
    chemin = serializers.CharField(source='chemin_complet', read_only=True)
    
    class Meta:
        model = Categorie
        fields = [
            'id', 'nom', 'description', 'parent',
            'ordre', 'sous_categories', 'chemin'
        ]

class RessourceListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des ressources"""
    type_ressource_display = serializers.CharField(
        source='get_type_ressource_display',
        read_only=True
    )
    langue_display = serializers.CharField(
        source='get_langue_display',
        read_only=True
    )
    niveau_display = serializers.CharField(
        source='get_niveau_display',
        read_only=True
    )
    contributeur_nom = serializers.CharField(
        source='contributeur.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Ressource
        fields = [
            'id', 'titre', 'auteurs', 'type_ressource',
            'type_ressource_display', 'langue', 'langue_display',
            'niveau', 'niveau_display', 'est_public', 'est_valide',
            'contributeur_nom', 'note_moyenne', 'nombre_evaluations',
            'nombre_telechargements', 'created_at'
        ]

class RessourceDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les ressources"""
    categories = CategorieListSerializer(many=True, read_only=True)
    departements = DepartementSerializer(many=True, read_only=True)
    cours = CoursSerializer(many=True, read_only=True)
    type_ressource_display = serializers.CharField(
        source='get_type_ressource_display',
        read_only=True
    )
    langue_display = serializers.CharField(
        source='get_langue_display',
        read_only=True
    )
    niveau_display = serializers.CharField(
        source='get_niveau_display',
        read_only=True
    )
    contributeur_details = serializers.SerializerMethodField()
    mots_cles_list = serializers.SerializerMethodField()
    fichier = serializers.FileField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'mp4', 'mp3']
            )
        ]
    )
    
    class Meta:
        model = Ressource
        fields = '__all__'

    def get_contributeur_details(self, obj):
        """Retourne les détails du contributeur"""
        if obj.contributeur:
            return {
                'id': obj.contributeur.id,
                'nom_complet': obj.contributeur.get_full_name(),
                'email': obj.contributeur.email
            }
        return None

    def get_mots_cles_list(self, obj):
        """Convertit la chaîne de mots-clés en liste"""
        return [mot.strip() for mot in obj.mots_cles.split(',')]

    def validate_fichier(self, value):
        """Valide la taille du fichier"""
        max_size = 100 * 1024 * 1024  # 100MB
        if value.size > max_size:
            raise serializers.ValidationError(
                _("La taille du fichier ne doit pas dépasser 100MB")
            )
        return value

class EvaluationSerializer(serializers.ModelSerializer):
    """Serializer pour les évaluations"""
    utilisateur_nom = serializers.CharField(
        source='utilisateur.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Evaluation
        fields = '__all__'
        read_only_fields = ['utilisateur']

    def validate(self, data):
        """Validation personnalisée"""
        # Vérifie si l'utilisateur a déjà évalué cette ressource
        utilisateur = self.context['request'].user
        if (
            not self.instance and
            Evaluation.objects.filter(
                ressource=data['ressource'],
                utilisateur=utilisateur
            ).exists()
        ):
            raise serializers.ValidationError(
                _("Vous avez déjà évalué cette ressource")
            )
        return data

class TelechargementSerializer(serializers.ModelSerializer):
    """Serializer pour les téléchargements"""
    utilisateur_nom = serializers.CharField(
        source='utilisateur.get_full_name',
        read_only=True
    )
    ressource_titre = serializers.CharField(
        source='ressource.titre',
        read_only=True
    )
    
    class Meta:
        model = Telechargement
        fields = '__all__'
        read_only_fields = ['utilisateur', 'ip_address', 'user_agent']

class CollectionListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des collections"""
    utilisateur_nom = serializers.CharField(
        source='utilisateur.get_full_name',
        read_only=True
    )
    nombre_ressources = serializers.IntegerField(
        source='ressources.count',
        read_only=True
    )
    
    class Meta:
        model = Collection
        fields = [
            'id', 'nom', 'description', 'utilisateur',
            'utilisateur_nom', 'est_publique',
            'nombre_ressources', 'created_at'
        ]

class CollectionDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les collections"""
    ressources = RessourceListSerializer(many=True, read_only=True)
    utilisateur_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Collection
        fields = '__all__'
        read_only_fields = ['utilisateur']

    def get_utilisateur_details(self, obj):
        """Retourne les détails de l'utilisateur"""
        return {
            'id': obj.utilisateur.id,
            'nom_complet': obj.utilisateur.get_full_name(),
            'email': obj.utilisateur.email
        }
