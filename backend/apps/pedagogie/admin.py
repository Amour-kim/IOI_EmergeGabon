from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Programme, UE, EC,
    Cours, Ressource, Evaluation
)

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'code', 'departement',
        'niveau', 'credits', 'statut'
    )
    list_filter = (
        'departement__faculte__universite',
        'departement', 'niveau', 'statut'
    )
    search_fields = (
        'nom', 'code',
        'departement__nom'
    )
    filter_horizontal = ('responsables',)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "responsables":
            kwargs["queryset"] = User.objects.filter(
                categorie='ENSEIGNANT',
                is_active=True
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

@admin.register(UE)
class UEAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'nom', 'programme',
        'semestre', 'credits', 'statut'
    )
    list_filter = (
        'programme__departement__faculte__universite',
        'programme', 'semestre', 'statut'
    )
    search_fields = ('code', 'nom', 'programme__nom')

@admin.register(EC)
class ECAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'nom', 'ue',
        'credits', 'coefficient', 'statut'
    )
    list_filter = (
        'ue__programme__departement__faculte__universite',
        'ue__programme', 'statut'
    )
    search_fields = ('code', 'nom', 'ue__nom')

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = (
        'ec', 'enseignant', 'annee_academique',
        'date_debut', 'date_fin', 'statut'
    )
    list_filter = (
        'ec__ue__programme__departement__faculte__universite',
        'annee_academique', 'statut'
    )
    search_fields = (
        'ec__nom', 'enseignant__nom',
        'annee_academique'
    )
    date_hierarchy = 'date_debut'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enseignant":
            kwargs["queryset"] = User.objects.filter(
                categorie='ENSEIGNANT',
                is_active=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Ressource)
class RessourceAdmin(admin.ModelAdmin):
    list_display = (
        'titre', 'cours', 'type_ressource',
        'format', 'taille', 'date_ajout'
    )
    list_filter = (
        'cours__ec__ue__programme__departement__faculte__universite',
        'type_ressource', 'format'
    )
    search_fields = ('titre', 'description', 'cours__ec__nom')
    date_hierarchy = 'date_ajout'

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'cours', 'type_evaluation',
        'date_evaluation', 'coefficient',
        'statut'
    )
    list_filter = (
        'cours__ec__ue__programme__departement__faculte__universite',
        'type_evaluation', 'statut'
    )
    search_fields = ('cours__ec__nom',)
    date_hierarchy = 'date_evaluation'
