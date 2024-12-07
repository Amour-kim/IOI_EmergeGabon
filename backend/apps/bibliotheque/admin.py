from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Categorie,
    Ressource,
    Evaluation,
    Telechargement,
    Collection
)

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'parent', 'ordre', 'nombre_ressources']
    list_filter = ['parent']
    search_fields = ['nom', 'description']
    ordering = ['ordre', 'nom']

    def nombre_ressources(self, obj):
        return obj.ressources.count()
    nombre_ressources.short_description = _("Nombre de ressources")

@admin.register(Ressource)
class RessourceAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'type_ressource', 'langue',
        'niveau', 'contributeur', 'est_public',
        'est_valide', 'note_moyenne',
        'nombre_telechargements'
    ]
    list_filter = [
        'type_ressource', 'langue', 'niveau',
        'est_public', 'est_valide', 'categories',
        'departements'
    ]
    search_fields = [
        'titre', 'auteurs', 'description',
        'mots_cles'
    ]
    filter_horizontal = [
        'categories', 'departements', 'cours'
    ]
    readonly_fields = [
        'note_moyenne', 'nombre_evaluations',
        'nombre_telechargements'
    ]
    fieldsets = (
        (_("Informations générales"), {
            'fields': (
                'titre', 'auteurs', 'annee_publication',
                'description', 'type_ressource', 'langue',
                'niveau'
            )
        }),
        (_("Catégorisation"), {
            'fields': (
                'categories', 'departements', 'cours',
                'mots_cles'
            )
        }),
        (_("Fichiers"), {
            'fields': ('fichier', 'url_externe')
        }),
        (_("Paramètres"), {
            'fields': (
                'est_public', 'est_valide',
                'contributeur'
            )
        }),
        (_("Statistiques"), {
            'fields': (
                'note_moyenne', 'nombre_evaluations',
                'nombre_telechargements'
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Nouvelle ressource
            obj.contributeur = request.user
        super().save_model(request, obj, form, change)

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'ressource', 'utilisateur', 'note',
        'created_at'
    ]
    list_filter = ['note', 'created_at']
    search_fields = [
        'ressource__titre', 'utilisateur__email',
        'commentaire'
    ]
    readonly_fields = ['created_at']

@admin.register(Telechargement)
class TelechargementAdmin(admin.ModelAdmin):
    list_display = [
        'ressource', 'utilisateur', 'ip_address',
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = [
        'ressource__titre', 'utilisateur__email',
        'ip_address'
    ]
    readonly_fields = ['created_at']

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'utilisateur', 'est_publique',
        'nombre_ressources', 'created_at'
    ]
    list_filter = ['est_publique', 'created_at']
    search_fields = ['nom', 'description', 'utilisateur__email']
    filter_horizontal = ['ressources']
    readonly_fields = ['created_at']

    def nombre_ressources(self, obj):
        return obj.ressources.count()
    nombre_ressources.short_description = _("Nombre de ressources")
