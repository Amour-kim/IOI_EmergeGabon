from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    TypeAbonnement, Abonnement,
    Paiement, Facture
)

@admin.register(TypeAbonnement)
class TypeAbonnementAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'code', 'prix_mensuel',
        'prix_annuel', 'capacite_stockage',
        'statut'
    )
    list_filter = ('statut',)
    search_fields = ('nom', 'code', 'description')
    
    fieldsets = (
        (None, {
            'fields': ('nom', 'code', 'description')
        }),
        (_('Tarification'), {
            'fields': ('prix_mensuel', 'prix_annuel')
        }),
        (_('Caractéristiques'), {
            'fields': (
                'capacite_stockage',
                'nombre_utilisateurs_max',
                'backup_inclus',
                'support_prioritaire'
            )
        }),
        (_('Statut'), {
            'fields': ('statut',)
        }),
    )

@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    list_display = (
        'universite', 'type_abonnement',
        'date_debut', 'date_fin',
        'montant_total', 'statut'
    )
    list_filter = (
        'universite', 'type_abonnement',
        'periodicite', 'statut'
    )
    search_fields = (
        'universite__nom',
        'type_abonnement__nom'
    )
    date_hierarchy = 'date_debut'
    
    fieldsets = (
        (None, {
            'fields': (
                'universite', 'type_abonnement',
                'periodicite'
            )
        }),
        (_('Période'), {
            'fields': ('date_debut', 'date_fin')
        }),
        (_('Facturation'), {
            'fields': (
                'montant_total',
                'reduction_appliquee'
            )
        }),
        (_('Statut'), {
            'fields': ('statut',)
        }),
    )
    readonly_fields = ('montant_total',)

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = (
        'abonnement', 'montant',
        'mode_paiement', 'date_paiement',
        'statut'
    )
    list_filter = (
        'abonnement__universite',
        'mode_paiement', 'statut'
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

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = (
        'numero_facture', 'abonnement',
        'montant_total', 'date_emission',
        'date_echeance', 'statut'
    )
    list_filter = (
        'abonnement__universite',
        'type_facture', 'statut'
    )
    search_fields = (
        'numero_facture',
        'abonnement__universite__nom'
    )
    date_hierarchy = 'date_emission'
    
    readonly_fields = (
        'numero_facture',
        'montant_total',
        'date_emission'
    )
