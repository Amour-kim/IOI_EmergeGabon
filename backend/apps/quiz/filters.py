import django_filters
from django.db.models import Q
from .models import Quiz, Question, Tentative

class QuizFilter(django_filters.FilterSet):
    """Filtres pour les quiz"""
    titre = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    date_debut_min = django_filters.DateTimeFilter(
        field_name='date_debut',
        lookup_expr='gte'
    )
    date_debut_max = django_filters.DateTimeFilter(
        field_name='date_debut',
        lookup_expr='lte'
    )
    date_fin_min = django_filters.DateTimeFilter(
        field_name='date_fin',
        lookup_expr='gte'
    )
    date_fin_max = django_filters.DateTimeFilter(
        field_name='date_fin',
        lookup_expr='lte'
    )
    disponible = django_filters.BooleanFilter(method='filter_disponible')

    class Meta:
        model = Quiz
        fields = {
            'cours': ['exact'],
            'type_quiz': ['exact'],
            'actif': ['exact'],
            'createur': ['exact'],
            'aleatoire': ['exact'],
        }

    def filter_disponible(self, queryset, name, value):
        """Filtre les quiz disponibles"""
        if value:
            return queryset.filter(
                Q(date_debut__isnull=True) |
                Q(date_debut__lte=timezone.now()),
                Q(date_fin__isnull=True) |
                Q(date_fin__gte=timezone.now()),
                actif=True
            )
        return queryset

class QuestionFilter(django_filters.FilterSet):
    """Filtres pour les questions"""
    texte = django_filters.CharFilter(lookup_expr='icontains')
    points_min = django_filters.NumberFilter(
        field_name='points',
        lookup_expr='gte'
    )
    points_max = django_filters.NumberFilter(
        field_name='points',
        lookup_expr='lte'
    )

    class Meta:
        model = Question
        fields = {
            'quiz': ['exact'],
            'type_question': ['exact'],
            'ordre': ['exact', 'gte', 'lte'],
        }

class TentativeFilter(django_filters.FilterSet):
    """Filtres pour les tentatives"""
    date_debut_min = django_filters.DateTimeFilter(
        field_name='date_debut',
        lookup_expr='gte'
    )
    date_debut_max = django_filters.DateTimeFilter(
        field_name='date_debut',
        lookup_expr='lte'
    )
    date_fin_min = django_filters.DateTimeFilter(
        field_name='date_fin',
        lookup_expr='gte'
    )
    date_fin_max = django_filters.DateTimeFilter(
        field_name='date_fin',
        lookup_expr='lte'
    )
    note_min = django_filters.NumberFilter(
        field_name='note',
        lookup_expr='gte'
    )
    note_max = django_filters.NumberFilter(
        field_name='note',
        lookup_expr='lte'
    )

    class Meta:
        model = Tentative
        fields = {
            'quiz': ['exact'],
            'etudiant': ['exact'],
            'statut': ['exact'],
            'numero_tentative': ['exact', 'gte', 'lte'],
        }
