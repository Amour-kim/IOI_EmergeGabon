from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Departement, Cycle, Filiere,
    UE, ECUE, Programme, Seance
)

@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'code', 'responsable'
    )
    search_fields = ('nom', 'code', 'description')

@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'niveau', 'duree'
    )
    list_filter = ('niveau',)
    search_fields = ('nom', 'description')

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'code', 'departement',
        'cycle', 'responsable'
    )
    list_filter = (
        'departement', 'cycle'
    )
    search_fields = (
        'nom', 'code',
        'description'
    )

@admin.register(UE)
class UEAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'intitule', 'filiere',
        'semestre', 'credits', 'responsable'
    )
    list_filter = (
        'filiere__departement',
        'filiere', 'semestre'
    )
    search_fields = ('code', 'intitule', 'description')

@admin.register(ECUE)
class ECUEAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'intitule', 'ue',
        'credits', 'coefficient', 'enseignant'
    )
    list_filter = (
        'ue__filiere__departement',
        'ue__filiere'
    )
    search_fields = ('code', 'intitule', 'description')

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = (
        'ecue', 'titre'
    )
    search_fields = (
        'titre', 'description',
        'objectifs', 'contenu'
    )

@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    list_display = (
        'ecue', 'type_seance', 'date_debut',
        'date_fin', 'salle', 'enseignant',
        'statut'
    )
    list_filter = (
        'ecue__ue__filiere__departement',
        'type_seance', 'statut'
    )
    search_fields = (
        'ecue__intitule', 'description',
        'salle'
    )
    date_hierarchy = 'date_debut'
