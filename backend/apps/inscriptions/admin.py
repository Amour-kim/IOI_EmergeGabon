from django.contrib import admin
from django.utils.html import format_html
from .models import DossierInscription, Document, Certificat

@admin.register(DossierInscription)
class DossierInscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'etudiant',
        'annee_academique',
        'niveau_etude',
        'departement',
        'statut',
        'date_soumission',
        'date_validation'
    )
    list_filter = (
        'statut',
        'annee_academique',
        'niveau_etude',
        'departement',
        'date_soumission'
    )
    search_fields = (
        'etudiant__username',
        'etudiant__first_name',
        'etudiant__last_name'
    )
    readonly_fields = ('date_soumission', 'date_validation')
    date_hierarchy = 'date_soumission'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'etudiant',
            'departement'
        )

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'dossier_etudiant',
        'type_document',
        'valide',
        'date_ajout',
        'fichier_link'
    )
    list_filter = ('type_document', 'valide', 'created_at')
    search_fields = (
        'dossier__etudiant__username',
        'dossier__etudiant__first_name',
        'dossier__etudiant__last_name'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def dossier_etudiant(self, obj):
        return obj.dossier.etudiant.get_full_name()
    dossier_etudiant.short_description = "Étudiant"
    
    def date_ajout(self, obj):
        return obj.created_at
    date_ajout.short_description = "Date d'ajout"
    
    def fichier_link(self, obj):
        if obj.fichier:
            return format_html(
                '<a href="{}" target="_blank">Voir le fichier</a>',
                obj.fichier.url
            )
        return "Aucun fichier"
    fichier_link.short_description = "Fichier"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'dossier__etudiant'
        )

@admin.register(Certificat)
class CertificatAdmin(admin.ModelAdmin):
    list_display = (
        'numero',
        'dossier_etudiant',
        'type_certificat',
        'date_generation',
        'valide_jusqu_au',
        'fichier_link'
    )
    list_filter = (
        'type_certificat',
        'date_generation',
        'valide_jusqu_au'
    )
    search_fields = (
        'numero',
        'dossier__etudiant__username',
        'dossier__etudiant__first_name',
        'dossier__etudiant__last_name'
    )
    readonly_fields = ('date_generation',)
    date_hierarchy = 'date_generation'
    
    def dossier_etudiant(self, obj):
        return obj.dossier.etudiant.get_full_name()
    dossier_etudiant.short_description = "Étudiant"
    
    def fichier_link(self, obj):
        if obj.fichier:
            return format_html(
                '<a href="{}" target="_blank">Voir le fichier</a>',
                obj.fichier.url
            )
        return "Aucun fichier"
    fichier_link.short_description = "Fichier"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'dossier__etudiant'
        )
