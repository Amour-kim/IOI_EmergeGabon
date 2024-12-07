import django_filters
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Ressource

class RessourceFilter(django_filters.FilterSet):
    """Filtres pour les ressources"""
    titre = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_("Titre")
    )
    auteurs = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_("Auteurs")
    )
    type_ressource = django_filters.MultipleChoiceFilter(
        choices=Ressource.TYPES,
        label=_("Type de ressource")
    )
    langue = django_filters.MultipleChoiceFilter(
        choices=Ressource.LANGUES,
        label=_("Langue")
    )
    niveau = django_filters.MultipleChoiceFilter(
        choices=Ressource.NIVEAUX,
        label=_("Niveau")
    )
    categories = django_filters.NumberFilter(
        field_name='categories',
        label=_("Catégorie")
    )
    departements = django_filters.NumberFilter(
        field_name='departements',
        label=_("Département")
    )
    cours = django_filters.NumberFilter(
        field_name='cours',
        label=_("Cours")
    )
    mots_cles = django_filters.CharFilter(
        method='filter_mots_cles',
        label=_("Mots-clés")
    )
    annee_min = django_filters.NumberFilter(
        field_name='annee_publication',
        lookup_expr='gte',
        label=_("Année minimum")
    )
    annee_max = django_filters.NumberFilter(
        field_name='annee_publication',
        lookup_expr='lte',
        label=_("Année maximum")
    )
    note_min = django_filters.NumberFilter(
        field_name='note_moyenne',
        lookup_expr='gte',
        label=_("Note minimum")
    )

    class Meta:
        model = Ressource
        fields = [
            'titre', 'auteurs', 'type_ressource',
            'langue', 'niveau', 'categories',
            'departements', 'cours', 'mots_cles',
            'annee_min', 'annee_max', 'note_min',
            'est_public', 'est_valide'
        ]

    def filter_mots_cles(self, queryset, name, value):
        """Filtre sur les mots-clés"""
        if not value:
            return queryset

        mots = [mot.strip() for mot in value.split(',')]
        q_objects = Q()

        for mot in mots:
            q_objects |= Q(mots_cles__icontains=mot)

        return queryset.filter(q_objects)
