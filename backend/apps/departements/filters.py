import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Departement, Programme, Cours

class DepartementFilter(django_filters.FilterSet):
    """Filtres pour les départements"""
    nom = django_filters.CharFilter(lookup_expr='icontains')
    faculte = django_filters.NumberFilter()
    recherche = django_filters.CharFilter(method='filter_recherche')

    class Meta:
        model = Departement
        fields = ['nom', 'faculte']

    def filter_recherche(self, queryset, name, value):
        """Recherche globale"""
        return queryset.filter(
            Q(nom__icontains=value) |
            Q(code__icontains=value) |
            Q(description__icontains=value)
        )

class ProgrammeFilter(django_filters.FilterSet):
    """Filtres pour les programmes"""
    nom = django_filters.CharFilter(lookup_expr='icontains')
    departement = django_filters.NumberFilter()
    niveau = django_filters.ChoiceFilter(choices=Programme.NIVEAUX)
    duree = django_filters.NumberFilter()

    class Meta:
        model = Programme
        fields = ['nom', 'departement', 'niveau', 'duree']

class CoursFilter(django_filters.FilterSet):
    """Filtres pour les cours"""
    intitule = django_filters.CharFilter(lookup_expr='icontains')
    departement = django_filters.NumberFilter()
    niveau = django_filters.ChoiceFilter(choices=Cours.NIVEAUX)
    semestre = django_filters.ChoiceFilter(choices=Cours.SEMESTRES)
    credits = django_filters.NumberFilter()
    est_optionnel = django_filters.BooleanFilter()
    enseignant = django_filters.NumberFilter(
        field_name='enseignants',
        label=_("Enseignant")
    )

    class Meta:
        model = Cours
        fields = [
            'intitule', 'departement', 'niveau',
            'semestre', 'credits', 'est_optionnel',
            'enseignant'
        ]
