from django.contrib import admin
from django.utils.html import format_html
from .models import Tuteur, SeanceTutorat, Inscription, Evaluation, Support

@admin.register(Tuteur)
class TuteurAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'niveau', 'departement',
        'statut', 'note_moyenne', 'nombre_evaluations'
    ]
    list_filter = ['niveau', 'statut', 'departement']
    search_fields = [
        'utilisateur__email',
        'utilisateur__first_name',
        'utilisateur__last_name',
        'biographie'
    ]
    filter_horizontal = ['specialites']
    readonly_fields = ['note_moyenne', 'nombre_evaluations']
    fieldsets = (
        (None, {
            'fields': (
                'utilisateur', 'niveau', 'departement',
                'specialites', 'biographie'
            )
        }),
        ('Validation', {
            'fields': (
                'cv', 'disponibilites', 'statut',
                'date_validation', 'commentaire_admin'
            )
        }),
        ('Statistiques', {
            'fields': ('note_moyenne', 'nombre_evaluations')
        })
    )

@admin.register(SeanceTutorat)
class SeanceTutoratAdmin(admin.ModelAdmin):
    list_display = [
        'tuteur', 'cours', 'type_seance',
        'modalite', 'date_debut', 'statut'
    ]
    list_filter = [
        'type_seance', 'modalite', 'statut',
        'date_debut'
    ]
    search_fields = [
        'tuteur__utilisateur__email',
        'cours__intitule',
        'description'
    ]
    date_hierarchy = 'date_debut'
    fieldsets = (
        (None, {
            'fields': (
                'tuteur', 'cours', 'type_seance',
                'modalite', 'date_debut', 'date_fin'
            )
        }),
        ('Détails', {
            'fields': (
                'lieu', 'capacite_max', 'description',
                'objectifs', 'prerequis', 'materiel_necessaire'
            )
        }),
        ('Tarification et Statut', {
            'fields': ('tarif_horaire', 'statut')
        })
    )

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'seance', 'etudiant', 'statut',
        'date_inscription', 'presence_confirmee'
    ]
    list_filter = ['statut', 'presence_confirmee']
    search_fields = [
        'etudiant__email',
        'seance__cours__intitule',
        'commentaire'
    ]
    date_hierarchy = 'date_inscription'
    raw_id_fields = ['seance', 'etudiant']

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'seance', 'etudiant', 'note',
        'date_evaluation', 'anonyme'
    ]
    list_filter = ['note', 'anonyme']
    search_fields = [
        'etudiant__email',
        'seance__cours__intitule',
        'commentaire'
    ]
    date_hierarchy = 'date_evaluation'
    raw_id_fields = ['seance', 'etudiant']

@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'seance', 'type_support',
        'date_publication', 'document_link'
    ]
    list_filter = ['type_support', 'date_publication']
    search_fields = ['titre', 'seance__cours__intitule']
    date_hierarchy = 'date_publication'
    raw_id_fields = ['seance']

    def document_link(self, obj):
        if obj.fichier:
            return format_html(
                '<a href="{}" target="_blank">Télécharger</a>',
                obj.fichier.url
            )
        return "Pas de fichier"
    document_link.short_description = "Fichier"
