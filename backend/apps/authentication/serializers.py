from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle utilisateur"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'matricule', 'categorie',
            'nom', 'prenoms', 'date_naissance',
            'lieu_naissance', 'telephone', 'universite',
            'departement', 'specialite', 'niveau_etude',
            'profession', 'enfants', 'statut',
            'date_creation', 'date_modification',
            'langue', 'notifications_email',
            'notifications_sms'
        ]
        read_only_fields = [
            'date_creation', 'date_modification'
        ]

class UserCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'utilisateur"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'matricule', 'categorie',
            'nom', 'prenoms', 'password', 'password2',
            'universite', 'departement'
        ]
    
    def validate(self, attrs):
        """Valide les données d'entrée"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': _('Les mots de passe ne correspondent pas.')
            })
        return attrs
    
    def create(self, validated_data):
        """Crée un nouvel utilisateur"""
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la mise à jour d'utilisateur"""
    
    class Meta:
        model = User
        fields = [
            'nom', 'prenoms', 'date_naissance',
            'lieu_naissance', 'telephone',
            'specialite', 'niveau_etude',
            'profession', 'langue',
            'notifications_email', 'notifications_sms'
        ]

class ChangePasswordSerializer(serializers.Serializer):
    """Sérialiseur pour le changement de mot de passe"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        """Valide l'ancien mot de passe"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('L\'ancien mot de passe est incorrect.')
            )
        return value
    
    def validate(self, attrs):
        """Valide les données d'entrée"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password': _('Les nouveaux mots de passe ne correspondent pas.')
            })
        return attrs
