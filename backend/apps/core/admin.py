from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class ModernAdminSite(AdminSite):
    site_title = _('Administration Gabon EDU')
    site_header = _('Plateforme Universitaire du Gabon')
    index_title = _('Administration')
    
    def each_context(self, request):
        context = super().each_context(request)
        context['custom_data'] = {
            'primary_color': '#1a73e8',
            'secondary_color': '#4285f4',
            'accent_color': '#fbbc04',
            'dark_color': '#202124',
            'light_color': '#ffffff',
            'success_color': '#34a853',
            'error_color': '#ea4335',
            'warning_color': '#fbbc04',
        }
        return context

# Création d'une nouvelle instance d'administration
modern_admin = ModernAdminSite(name='modern_admin')
