from rest_framework import serializers
from .models import (
    Departement, Cycle, Filiere, UE, ECUE,
    Programme, Seance
)

class DepartementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class CycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cycle
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class FiliereSerializer(serializers.ModelSerializer):
    departement_nom = serializers.CharField(
        source='departement.nom',
        read_only=True
    )
    cycle_nom = serializers.CharField(
        source='cycle.nom',
        read_only=True
    )
    
    class Meta:
        model = Filiere
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class UESerializer(serializers.ModelSerializer):
    filiere_nom = serializers.CharField(
        source='filiere.nom',
        read_only=True
    )
    volume_horaire_total = serializers.IntegerField(read_only=True)
    prerequis_details = serializers.SerializerMethodField()
    
    class Meta:
        model = UE
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_prerequis_details(self, obj):
        return [
            {
                'code': ue.code,
                'intitule': ue.intitule
            }
            for ue in obj.prerequis.all()
        ]

class ECUESerializer(serializers.ModelSerializer):
    ue_intitule = serializers.CharField(
        source='ue.intitule',
        read_only=True
    )
    volume_horaire_total = serializers.IntegerField(read_only=True)
    enseignant_nom = serializers.CharField(
        source='enseignant.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = ECUE
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class ProgrammeSerializer(serializers.ModelSerializer):
    ecue_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Programme
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_ecue_details(self, obj):
        return {
            'code': obj.ecue.code,
            'intitule': obj.ecue.intitule,
            'credits': obj.ecue.credits,
            'enseignant': obj.ecue.enseignant.get_full_name() if obj.ecue.enseignant else None
        }

class SeanceSerializer(serializers.ModelSerializer):
    ecue_details = serializers.SerializerMethodField()
    enseignant_nom = serializers.CharField(
        source='enseignant.get_full_name',
        read_only=True
    )
    duree = serializers.DurationField(read_only=True)
    
    class Meta:
        model = Seance
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_ecue_details(self, obj):
        return {
            'code': obj.ecue.code,
            'intitule': obj.ecue.intitule,
            'ue': {
                'code': obj.ecue.ue.code,
                'intitule': obj.ecue.ue.intitule
            },
            'filiere': {
                'code': obj.ecue.ue.filiere.code,
                'nom': obj.ecue.ue.filiere.nom
            }
        }
    
    def validate(self, data):
        """Validation des dates de début et de fin"""
        if data['date_debut'] >= data['date_fin']:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début"
            )
        return data

class SeanceDetailSerializer(SeanceSerializer):
    """Sérialiseur détaillé pour les séances avec plus d'informations"""
    class Meta(SeanceSerializer.Meta):
        depth = 2  # Inclut les détails des relations jusqu'à 2 niveaux
