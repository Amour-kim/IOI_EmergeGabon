from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'matricule', 'email', 'nom', 'prenoms',
        'categorie', 'universite', 'statut',
        'is_active', 'is_staff'
    )
    list_filter = (
        'categorie', 'statut', 'universite',
        'is_active', 'is_staff', 'date_creation'
    )
    search_fields = (
        'matricule', 'email', 'nom', 'prenoms',
        'telephone'
    )
    ordering = ('nom', 'prenoms')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {
            'fields': (
                'matricule', 'nom', 'prenoms',
                'date_naissance', 'lieu_naissance',
                'telephone'
            )
        }),
        (_('Catégorie et Affiliation'), {
            'fields': (
                'categorie', 'universite', 'departement'
            )
        }),
        (_('Informations spécifiques'), {
            'fields': (
                'specialite', 'niveau_etude',
                'profession', 'enfants'
            )
        }),
        (_('Statut et permissions'), {
            'fields': (
                'statut', 'is_active', 'is_staff',
                'is_superuser', 'groups',
                'user_permissions'
            )
        }),
        (_('Préférences'), {
            'fields': (
                'langue', 'notifications_email',
                'notifications_sms'
            )
        }),
        (_('Dates importantes'), {
            'fields': ('date_creation', 'date_modification')
        }),
    )
    
    readonly_fields = ('date_creation', 'date_modification')
    filter_horizontal = ('groups', 'user_permissions', 'enfants')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'matricule', 'password1',
                'password2', 'categorie', 'nom',
                'prenoms', 'universite'
            ),
        }),
    )
