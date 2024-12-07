from django.contrib import admin
from django.utils.html import format_html
from .models import Evenement, Inscription, Document, Feedback

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'type_evenement', 'date_debut',
        'lieu', 'places_disponibles', 'statut'
    ]
    list_filter = ['type_evenement', 'statut', 'inscription_requise']
    search_fields = ['titre', 'description', 'lieu']
    date_hierarchy = 'date_debut'
    filter_horizontal = ['departements']
    readonly_fields = ['places_disponibles']
    fieldsets = (
        (None, {
            'fields': (
                'titre', 'type_evenement', 'description',
                'date_debut', 'date_fin', 'lieu'
            )
        }),
        ('Organisation', {
            'fields': (
                'organisateur', 'departements', 'capacite',
                'places_disponibles', 'inscription_requise'
            )
        }),
        ('Détails', {
            'fields': (
                'image', 'public_cible', 'contact_email',
                'contact_telephone', 'site_web', 'cout'
            )
        }),
        ('Statut', {
            'fields': ('statut',)
        })
    )

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'evenement', 'participant', 'statut',
        'date_inscription', 'presence_confirmee'
    ]
    list_filter = ['statut', 'presence_confirmee', 'certificat_genere']
    search_fields = [
        'evenement__titre',
        'participant__email',
        'participant__first_name',
        'participant__last_name'
    ]
    date_hierarchy = 'date_inscription'
    raw_id_fields = ['evenement', 'participant']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'evenement', 'type_document',
        'date_publication', 'public', 'document_link'
    ]
    list_filter = ['type_document', 'public', 'date_publication']
    search_fields = ['titre', 'evenement__titre', 'description']
    date_hierarchy = 'date_publication'
    raw_id_fields = ['evenement']

    def document_link(self, obj):
        if obj.fichier:
            return format_html(
                '<a href="{}" target="_blank">Télécharger</a>',
                obj.fichier.url
            )
        return "Pas de fichier"
    document_link.short_description = "Fichier"

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'evenement', 'participant', 'note',
        'date_feedback', 'anonyme'
    ]
    list_filter = ['note', 'anonyme', 'date_feedback']
    search_fields = [
        'evenement__titre',
        'participant__email',
        'commentaire'
    ]
    date_hierarchy = 'date_feedback'
    raw_id_fields = ['evenement', 'participant']
