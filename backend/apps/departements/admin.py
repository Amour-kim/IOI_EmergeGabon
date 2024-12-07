from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Faculte, Departement, Programme, Cours

@admin.register(Faculte)
class FaculteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'doyen', 'date_creation']
    search_fields = ['nom', 'code', 'doyen']
    list_filter = ['date_creation']

@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'faculte', 'chef_departement']
    search_fields = ['nom', 'code', 'chef_departement']
    list_filter = ['faculte']

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'departement', 'niveau', 'duree']
    search_fields = ['nom', 'code']
    list_filter = ['departement', 'niveau']
    filter_horizontal = ['prerequis']

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'intitule', 'departement',
        'credits', 'est_optionnel'
    ]
    search_fields = ['code', 'intitule']
    list_filter = ['departement', 'niveau', 'semestre', 'est_optionnel']
    filter_horizontal = ['prerequis', 'enseignants']
    fieldsets = (
        (_("Informations générales"), {
            'fields': (
                'code', 'intitule', 'description',
                'departement', 'credits'
            )
        }),
        (_("Organisation"), {
            'fields': (
                'niveau', 'semestre', 'est_optionnel',
                'heures_cm', 'heures_td', 'heures_tp'
            )
        }),
        (_("Relations"), {
            'fields': ('prerequis', 'enseignants')
        }),
        (_("Contenu"), {
            'fields': ('objectifs', 'plan_cours', 'bibliographie')
        }),
    )
