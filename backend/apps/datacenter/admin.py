from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Datacenter, Bibliotheque, Documentation,
    Mediatheque, Livre, Document, Media
)

@admin.register(Datacenter)
class DatacenterAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'universite', 'capacite_totale',
        'capacite_utilisee', 'get_pourcentage_utilisation',
        'statut'
    )
    list_filter = ('universite', 'statut')
    search_fields = ('nom', 'universite__nom')
    
    fieldsets = (
        (None, {
            'fields': ('nom', 'universite', 'description')
        }),
        (_('Capacité'), {
            'fields': (
                'capacite_totale', 'capacite_utilisee',
                'get_pourcentage_utilisation'
            )
        }),
        (_('Configuration'), {
            'fields': (
                'backup_actif', 'frequence_backup',
                'retention_backup', 'statut'
            )
        }),
    )
    readonly_fields = ('capacite_utilisee', 'get_pourcentage_utilisation')

@admin.register(Bibliotheque)
class BibliothequeAdmin(admin.ModelAdmin):
    list_display = (
        'datacenter', 'capacite_allouee',
        'capacite_utilisee', 'get_pourcentage_utilisation'
    )
    list_filter = ('datacenter__universite',)
    search_fields = ('datacenter__nom',)

@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = (
        'datacenter', 'capacite_allouee',
        'capacite_utilisee', 'get_pourcentage_utilisation'
    )
    list_filter = ('datacenter__universite',)
    search_fields = ('datacenter__nom',)

@admin.register(Mediatheque)
class MediathequeAdmin(admin.ModelAdmin):
    list_display = (
        'datacenter', 'capacite_allouee',
        'capacite_utilisee', 'get_pourcentage_utilisation'
    )
    list_filter = ('datacenter__universite',)
    search_fields = ('datacenter__nom',)

@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = (
        'titre', 'auteur', 'bibliotheque',
        'format', 'taille', 'date_ajout'
    )
    list_filter = (
        'bibliotheque__datacenter__universite',
        'format', 'date_ajout'
    )
    search_fields = ('titre', 'auteur', 'description')
    date_hierarchy = 'date_ajout'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'titre', 'type_document', 'documentation',
        'format', 'taille', 'date_ajout'
    )
    list_filter = (
        'documentation__datacenter__universite',
        'type_document', 'format', 'date_ajout'
    )
    search_fields = ('titre', 'description')
    date_hierarchy = 'date_ajout'

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = (
        'titre', 'type_media', 'mediatheque',
        'format', 'taille', 'date_ajout'
    )
    list_filter = (
        'mediatheque__datacenter__universite',
        'type_media', 'format', 'date_ajout'
    )
    search_fields = ('titre', 'description')
    date_hierarchy = 'date_ajout'
