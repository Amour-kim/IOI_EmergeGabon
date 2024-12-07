import django_filters
from django.db.models import Q
from .models import Tuteur, SeanceTutorat, Inscription, Evaluation

class TuteurFilter(django_filters.FilterSet):
    """Filtres pour les tuteurs"""
    niveau = django_filters.ChoiceFilter(choices=Tuteur.NIVEAU_CHOICES)
    departement = django_filters.NumberFilter()
    specialite = django_filters.NumberFilter(
        field_name='specialites',
        lookup_expr='exact'
    )
    statut = django_filters.ChoiceFilter(choices=Tuteur.STATUT_CHOICES)
    note_minimum = django_filters.NumberFilter(
        field_name='note_moyenne',
        lookup_expr='gte'
    )
    recherche = django_filters.CharFilter(method='filter_recherche')

    class Meta:
        model = Tuteur
        fields = ['niveau', 'departement', 'statut']

    def filter_recherche(self, queryset, name, value):
        return queryset.filter(
            Q(utilisateur__first_name__icontains=value) |
            Q(utilisateur__last_name__icontains=value) |
            Q(biographie__icontains=value)
        )

class SeanceTutoratFilter(django_filters.FilterSet):
    """Filtres pour les séances de tutorat"""
    tuteur = django_filters.NumberFilter()
    cours = django_filters.NumberFilter()
    type_seance = django_filters.ChoiceFilter(
        choices=SeanceTutorat.TYPE_CHOICES
    )
    modalite = django_filters.ChoiceFilter(
        choices=SeanceTutorat.MODALITE_CHOICES
    )
    date_debut_apres = django_filters.DateTimeFilter(
        field_name='date_debut',
        lookup_expr='gte'
    )
    date_debut_avant = django_filters.DateTimeFilter(
        field_name='date_debut',
        lookup_expr='lte'
    )
    statut = django_filters.ChoiceFilter(
        choices=SeanceTutorat.STATUT_CHOICES
    )
    places_disponibles = django_filters.BooleanFilter(
        method='filter_places_disponibles'
    )
    tarif_maximum = django_filters.NumberFilter(
        field_name='tarif_horaire',
        lookup_expr='lte'
    )

    class Meta:
        model = SeanceTutorat
        fields = [
            'tuteur', 'cours', 'type_seance',
            'modalite', 'statut'
        ]

    def filter_places_disponibles(self, queryset, name, value):
        if value:
            return queryset.filter(
                capacite_max__gt=models.Count('inscriptions')
            )
        return queryset

class InscriptionFilter(django_filters.FilterSet):
    """Filtres pour les inscriptions"""
    seance = django_filters.NumberFilter()
    etudiant = django_filters.NumberFilter()
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
        fields = ['seance', 'etudiant', 'statut', 'presence_confirmee']

class EvaluationFilter(django_filters.FilterSet):
    """Filtres pour les évaluations"""
    seance = django_filters.NumberFilter()
    etudiant = django_filters.NumberFilter()
    note_minimum = django_filters.NumberFilter(
        field_name='note',
        lookup_expr='gte'
    )
    date_evaluation_apres = django_filters.DateTimeFilter(
        field_name='date_evaluation',
        lookup_expr='gte'
    )
    date_evaluation_avant = django_filters.DateTimeFilter(
        field_name='date_evaluation',
        lookup_expr='lte'
    )
    anonyme = django_filters.BooleanFilter()

    class Meta:
        model = Evaluation
        fields = ['seance', 'etudiant', 'note', 'anonyme']
