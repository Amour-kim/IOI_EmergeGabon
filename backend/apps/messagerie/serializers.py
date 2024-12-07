from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ConfigurationEmail, CompteEmail, Alias, ListeDiffusion
)

User = get_user_model()

class ConfigurationEmailSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la configuration email"""
    class Meta:
        model = ConfigurationEmail
        fields = [
            'id', 'nom_domaine',
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password',
            'smtp_use_tls', 'smtp_use_ssl',
            'imap_host', 'imap_port', 'imap_user', 'imap_password',
            'imap_use_ssl',
            'from_email', 'from_name', 'signature_defaut',
            'quota_boite', 'taille_max_piece_jointe',
            'dkim_active', 'dkim_domain', 'dkim_selector', 'dkim_private_key',
            'spf_active', 'spf_record',
            'dmarc_active', 'dmarc_record',
            'actif', 'date_creation', 'date_modification'
        ]
        extra_kwargs = {
            'smtp_password': {'write_only': True},
            'imap_password': {'write_only': True},
            'dkim_private_key': {'write_only': True}
        }

class CompteEmailSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les comptes email"""
    utilisateur = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    configuration = serializers.PrimaryKeyRelatedField(
        queryset=ConfigurationEmail.objects.all()
    )
    
    class Meta:
        model = CompteEmail
        fields = [
            'id', 'utilisateur', 'configuration',
            'adresse_email', 'mot_de_passe',
            'quota_utilise', 'signature_personnalisee',
            'transfert_actif', 'adresse_transfert',
            'reponse_auto_active', 'message_reponse_auto',
            'date_debut_reponse_auto', 'date_fin_reponse_auto',
            'actif', 'date_creation', 'date_modification',
            'derniere_connexion'
        ]
        extra_kwargs = {
            'mot_de_passe': {'write_only': True}
        }
    
    def validate_adresse_email(self, value):
        """Valide que l'adresse email correspond au domaine"""
        configuration = self.initial_data.get('configuration')
        if configuration:
            config = ConfigurationEmail.objects.get(id=configuration)
            domaine = value.split('@')[1]
            if domaine != config.nom_domaine:
                raise serializers.ValidationError(
                    'L\'adresse email doit utiliser le domaine de la configuration'
                )
        return value

class AliasSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les alias email"""
    compte = serializers.PrimaryKeyRelatedField(
        queryset=CompteEmail.objects.all()
    )
    
    class Meta:
        model = Alias
        fields = [
            'id', 'compte', 'adresse_alias',
            'description', 'actif'
        ]
    
    def validate_adresse_alias(self, value):
        """Valide que l'alias correspond au domaine"""
        compte = self.initial_data.get('compte')
        if compte:
            compte_obj = CompteEmail.objects.get(id=compte)
            domaine = value.split('@')[1]
            if domaine != compte_obj.configuration.nom_domaine:
                raise serializers.ValidationError(
                    'L\'alias doit utiliser le domaine de la configuration'
                )
        return value

class ListeDiffusionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les listes de diffusion"""
    configuration = serializers.PrimaryKeyRelatedField(
        queryset=ConfigurationEmail.objects.all()
    )
    moderateurs = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CompteEmail.objects.all(),
        required=False
    )
    membres = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CompteEmail.objects.all(),
        required=False
    )
    
    class Meta:
        model = ListeDiffusion
        fields = [
            'id', 'configuration', 'nom', 'adresse_email',
            'description', 'moderateurs', 'membres',
            'moderation_active', 'inscription_libre',
            'archive_active', 'actif',
            'date_creation', 'date_modification'
        ]
    
    def validate_adresse_email(self, value):
        """Valide que l'adresse email correspond au domaine"""
        configuration = self.initial_data.get('configuration')
        if configuration:
            config = ConfigurationEmail.objects.get(id=configuration)
            domaine = value.split('@')[1]
            if domaine != config.nom_domaine:
                raise serializers.ValidationError(
                    'L\'adresse email doit utiliser le domaine de la configuration'
                )
        return value
