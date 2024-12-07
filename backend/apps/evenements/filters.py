import django_filters
from django.db.models import Q
from .models import Evenement, Inscription, Document

class EvenementFilter(django_filters.FilterSet):
    """Filtres pour les événements"""
    titre = django_filters.CharFilter(lookup_expr='icontains')
    type_evenement = django_filters.ChoiceFilter(choices=Evenement.TYPE_CHOICES)
    date_debut_apres = django_filters.DateTimeFilter(
        field_name='date_debut',
        lookup_expr='gte'
    )
    date_debut_avant = django_filters.DateTimeFilter(
        field_name='date_debut',
        lookup_expr='lte'
    )
    departement = django_filters.NumberFilter(
        field_name='departements',
        lookup_expr='exact'
    )
    statut = django_filters.ChoiceFilter(choices=Evenement.STATUT_CHOICES)
    places_disponibles = django_filters.BooleanFilter(
        method='filter_places_disponibles'
    )
    recherche = django_filters.CharFilter(method='filter_recherche')

    class Meta:
        model = Evenement
        fields = [
            'titre', 'type_evenement', 'statut',
            'inscription_requise', 'organisateur'
        ]

    def filter_places_disponibles(self, queryset, name, value):
        if value:
            return queryset.filter(places_disponibles__gt=0)
        return queryset

    def filter_recherche(self, queryset, name, value):
        return queryset.filter(
            Q(titre__icontains=value) |
            Q(description__icontains=value) |
            Q(lieu__icontains=value) |
            Q(public_cible__icontains=value)
        )

class InscriptionFilter(django_filters.FilterSet):
    """Filtres pour les inscriptions"""
    evenement = django_filters.NumberFilter()
    participant = django_filters.NumberFilter()
    statut = django_filters.ChoiceFilter(choices=Inscription.STATUT_CHOICES)
    date_inscription_apres = django_filters.DateTimeFilter(
        field_name='date_inscription',
        lookup_expr='gte'
    )
    date_inscription_avant = django_filters.DateTimeFilter(
        field_name='date_inscription',
        lookup_expr='lte'
    )
    presence_confirmee = django_filters.BooleanFilter()

    class Meta:
        model = Inscription
        fields = ['evenement', 'participant', 'statut', 'presence_confirmee']

class DocumentFilter(django_filters.FilterSet):
    """Filtres pour les documents"""
    evenement = django_filters.NumberFilter()
    type_document = django_filters.ChoiceFilter(choices=Document.TYPE_CHOICES)
    titre = django_filters.CharFilter(lookup_expr='icontains')
    public = django_filters.BooleanFilter()
    date_publication_apres = django_filters.DateTimeFilter(
        field_name='date_publication',
        lookup_expr='gte'
    )
    date_publication_avant = django_filters.DateTimeFilter(
        field_name='date_publication',
        lookup_expr='lte'
    )

    class Meta:
        model = Document
        fields = ['evenement', 'type_document', 'public']
