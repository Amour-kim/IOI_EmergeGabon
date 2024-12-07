import django_filters
from .models import DossierInscription, Document, Certificat

class DossierInscriptionFilter(django_filters.FilterSet):
    """Filtres pour les dossiers d'inscription"""
    etudiant_nom = django_filters.CharFilter(
        field_name='etudiant__last_name',
        lookup_expr='icontains'
    )
    etudiant_prenom = django_filters.CharFilter(
        field_name='etudiant__first_name',
        lookup_expr='icontains'
    )
    date_soumission_min = django_filters.DateFilter(
        field_name='date_soumission',
        lookup_expr='gte'
    )
    date_soumission_max = django_filters.DateFilter(
        field_name='date_soumission',
        lookup_expr='lte'
    )

    class Meta:
        model = DossierInscription
        fields = {
            'annee_academique': ['exact'],
            'niveau_etude': ['exact'],
            'departement': ['exact'],
            'statut': ['exact'],
        }

class DocumentFilter(django_filters.FilterSet):
    """Filtres pour les documents"""
    dossier_etudiant = django_filters.CharFilter(
        field_name='dossier__etudiant__username',
        lookup_expr='exact'
    )
    date_ajout_min = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    date_ajout_max = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    class Meta:
        model = Document
        fields = {
            'type_document': ['exact'],
            'valide': ['exact'],
            'dossier': ['exact'],
        }

class CertificatFilter(django_filters.FilterSet):
    """Filtres pour les certificats"""
    dossier_etudiant = django_filters.CharFilter(
        field_name='dossier__etudiant__username',
        lookup_expr='exact'
    )
    date_generation_min = django_filters.DateFilter(
        field_name='date_generation',
        lookup_expr='gte'
    )
    date_generation_max = django_filters.DateFilter(
        field_name='date_generation',
        lookup_expr='lte'
    )
    valide_jusqu_au_min = django_filters.DateFilter(
        field_name='valide_jusqu_au',
        lookup_expr='gte'
    )

    class Meta:
        model = Certificat
        fields = {
            'type_certificat': ['exact'],
            'numero': ['exact', 'contains'],
            'dossier': ['exact'],
        }
