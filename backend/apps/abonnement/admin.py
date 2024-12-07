from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    PlanAbonnement, Abonnement,
    HistoriquePaiement
)

@admin.register(PlanAbonnement)
class PlanAbonnementAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'type_plan', 'prix_mensuel',
        'prix_annuel', 'nb_max_datacenters'
    )
    search_fields = ('nom', 'description')
    
    fieldsets = (
        (None, {
            'fields': ('nom', 'type_plan', 'description')
        }),
        (_('Prix'), {
            'fields': ('prix_mensuel', 'prix_annuel')
        }),
        (_('Limites Datacenter'), {
            'fields': ('nb_max_datacenters', 'capacite_datacenter')
        }),
        (_('Limites Bibliothèque'), {
            'fields': ('nb_max_bibliotheques', 'capacite_bibliotheque')
        }),
        (_('Limites Documentation'), {
            'fields': ('nb_max_documentations', 'capacite_documentation')
        })
    )

@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = (
        'universite', 'plan', 'periodicite',
        'date_debut', 'date_fin', 'etat'
    )
    list_filter = (
        'universite', 'plan',
        'periodicite', 'etat'
    )
    search_fields = (
        'universite__nom',
        'plan__nom'
    )
    date_hierarchy = 'date_debut'
    
    fieldsets = (
        (None, {
            'fields': (
                'universite', 'plan',
                'periodicite'
            )
        }),
        (_('Période'), {
            'fields': ('date_debut', 'date_fin')
        }),
        (_('État'), {
            'fields': (
                'etat',
                'renouvellement_auto'
            )
        }),
        (_('Utilisation'), {
            'fields': (
                'nb_datacenters_utilises',
                'nb_bibliotheques_utilisees',
                'nb_documentations_utilisees',
                'nb_serveurs_mail_utilises',
                'nb_mediatheques_utilisees'
            )
        }),
        (_('Paiements'), {
            'fields': (
                'date_dernier_paiement',
                'date_prochain_paiement'
            )
        }),
        (_('Notes'), {
            'fields': ('notes',)
        })
    )

@admin.register(HistoriquePaiement)
class HistoriquePaiementAdmin(admin.ModelAdmin):
    list_display = (
        'abonnement', 'montant',
        'methode_paiement', 'date_paiement',
        'statut'
    )
    list_filter = (
        'abonnement__universite',
        'methode_paiement', 'statut'
    )
    search_fields = (
        'abonnement__universite__nom',
        'reference_transaction'
    )
    date_hierarchy = 'date_paiement'
    readonly_fields = (
        'reference_transaction',
        'date_paiement'
    )
