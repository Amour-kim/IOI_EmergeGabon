import django_filters
from .models import UE, ECUE, Seance

class UEFilter(django_filters.FilterSet):
    """Filtres pour les UEs"""
    code = django_filters.CharFilter(lookup_expr='icontains')
    intitule = django_filters.CharFilter(lookup_expr='icontains')
    credits = django_filters.NumberFilter()
    credits_min = django_filters.NumberFilter(field_name='credits', lookup_expr='gte')
    credits_max = django_filters.NumberFilter(field_name='credits', lookup_expr='lte')
    
    class Meta:
        model = UE
        fields = ['code', 'intitule', 'credits', 'filiere', 'semestre']

class ECUEFilter(django_filters.FilterSet):
    """Filtres pour les ECUEs"""
    code = django_filters.CharFilter(lookup_expr='icontains')
    intitule = django_filters.CharFilter(lookup_expr='icontains')
    credits = django_filters.NumberFilter()
    enseignant = django_filters.CharFilter(
        field_name='enseignant__email',
        lookup_expr='iexact'
    )
    
    class Meta:
        model = ECUE
        fields = ['code', 'intitule', 'credits', 'ue', 'enseignant']

class SeanceFilter(django_filters.FilterSet):
    """Filtres pour les séances"""
    date_debut = django_filters.DateFilter(field_name='date_debut', lookup_expr='date')
    date_debut_min = django_filters.DateFilter(
        field_name='date_debut',
        lookup_expr='date__gte'
    )
    date_debut_max = django_filters.DateFilter(
        field_name='date_debut',
        lookup_expr='date__lte'
    )
    enseignant = django_filters.CharFilter(
        field_name='enseignant__email',
        lookup_expr='iexact'
    )
    
    class Meta:
        model = Seance
        fields = [
            'type_seance', 'statut', 'ecue',
            'date_debut', 'enseignant', 'salle'
        ]
