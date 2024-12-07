from rest_framework import serializers
from .models import (
    Datacenter, Bibliotheque, Documentation,
    Mediatheque, Livre, Document, Media
)

class DatacenterSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Datacenter"""
    stockage_utilise_pourcentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Datacenter
        fields = [
            'id', 'universite', 'nom', 'description',
            'capacite_totale', 'stockage_utilise',
            'stockage_utilise_pourcentage',
            'backup_actif', 'frequence_backup',
            'retention_backup', 'actif',
            'date_creation', 'date_modification'
        ]
        read_only_fields = [
            'stockage_utilise', 'date_creation',
            'date_modification'
        ]
    
    def get_stockage_utilise_pourcentage(self, obj):
        """Calcule le pourcentage de stockage utilisé"""
        if obj.capacite_totale == 0:
            return 0
        return (obj.stockage_utilise / obj.capacite_totale) * 100

class BibliothequeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Bibliothèque"""
    stockage_utilise_pourcentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Bibliotheque
        fields = [
            'id', 'datacenter', 'nom', 'description',
            'capacite_stockage', 'stockage_utilise',
            'stockage_utilise_pourcentage'
        ]
        read_only_fields = ['stockage_utilise']
    
    def get_stockage_utilise_pourcentage(self, obj):
        """Calcule le pourcentage de stockage utilisé"""
        if obj.capacite_stockage == 0:
            return 0
        return (obj.stockage_utilise / obj.capacite_stockage) * 100

class DocumentationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Documentation"""
    stockage_utilise_pourcentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Documentation
        fields = [
            'id', 'datacenter', 'nom', 'description',
            'capacite_stockage', 'stockage_utilise',
            'stockage_utilise_pourcentage'
        ]
        read_only_fields = ['stockage_utilise']
    
    def get_stockage_utilise_pourcentage(self, obj):
        """Calcule le pourcentage de stockage utilisé"""
        if obj.capacite_stockage == 0:
            return 0
        return (obj.stockage_utilise / obj.capacite_stockage) * 100

class MediathequeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Médiathèque"""
    stockage_utilise_pourcentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Mediatheque
        fields = [
            'id', 'datacenter', 'nom', 'description',
            'capacite_stockage', 'stockage_utilise',
            'stockage_utilise_pourcentage'
        ]
        read_only_fields = ['stockage_utilise']
    
    def get_stockage_utilise_pourcentage(self, obj):
        """Calcule le pourcentage de stockage utilisé"""
        if obj.capacite_stockage == 0:
            return 0
        return (obj.stockage_utilise / obj.capacite_stockage) * 100

class LivreSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Livre"""
    class Meta:
        model = Livre
        fields = [
            'id', 'section', 'titre', 'auteurs',
            'isbn', 'edition', 'annee_publication',
            'langue', 'format', 'taille', 'fichier',
            'mots_cles', 'description', 'date_ajout'
        ]
        read_only_fields = ['date_ajout']

class DocumentSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Document"""
    class Meta:
        model = Document
        fields = [
            'id', 'documentation', 'titre',
            'type_document', 'auteur', 'version',
            'format', 'taille', 'fichier',
            'mots_cles', 'description',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['date_creation', 'date_modification']

class MediaSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Media"""
    class Meta:
        model = Media
        fields = [
            'id', 'mediatheque', 'titre',
            'type_media', 'auteur', 'duree',
            'format', 'resolution', 'taille',
            'fichier', 'vignette', 'mots_cles',
            'description', 'date_creation',
            'date_modification'
        ]
        read_only_fields = ['date_creation', 'date_modification']
