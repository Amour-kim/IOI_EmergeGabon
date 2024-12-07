from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Universite, Campus, Faculte, Departement

@admin.register(Universite)
class UniversiteAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'code', 'ville', 'type_etablissement',
        'statut', 'date_creation'
    )
    list_filter = ('type_etablissement', 'statut', 'ville')
    search_fields = ('nom', 'code', 'ville')
    date_hierarchy = 'date_creation'
    
    fieldsets = (
        (None, {
            'fields': ('nom', 'code', 'description')
        }),
        (_('Localisation'), {
            'fields': ('ville', 'adresse', 'telephone', 'email')
        }),
        (_('Classification'), {
            'fields': ('type_etablissement', 'specialites')
        }),
        (_('Statut'), {
            'fields': ('statut', 'date_creation')
        }),
    )
    readonly_fields = ('date_creation',)

@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'universite', 'ville',
        'statut', 'date_creation'
    )
    list_filter = ('universite', 'ville', 'statut')
    search_fields = ('nom', 'universite__nom', 'ville')
    date_hierarchy = 'date_creation'

@admin.register(Faculte)
class FaculteAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'code', 'universite',
        'campus', 'statut', 'date_creation'
    )
    list_filter = ('universite', 'campus', 'statut')
    search_fields = ('nom', 'code', 'universite__nom')
    date_hierarchy = 'date_creation'

@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'code', 'faculte',
        'responsable', 'statut', 'date_creation'
    )
    list_filter = (
        'faculte__universite',
        'faculte',
        'statut'
    )
    search_fields = (
        'nom', 'code',
        'faculte__nom',
        'responsable__nom'
    )
    date_hierarchy = 'date_creation'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "responsable":
            kwargs["queryset"] = User.objects.filter(
                categorie='ENSEIGNANT',
                is_active=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
