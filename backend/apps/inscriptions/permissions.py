from rest_framework import permissions

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permission personnalisée pour permettre uniquement aux propriétaires
    d'un dossier ou au personnel administratif d'y accéder.
    """

    def has_object_permission(self, request, view, obj):
        # Le personnel administratif a tous les droits
        if request.user.is_staff:
            return True

        # Pour les dossiers d'inscription
        if hasattr(obj, 'etudiant'):
            return obj.etudiant == request.user

        # Pour les documents
        if hasattr(obj, 'dossier'):
            return obj.dossier.etudiant == request.user

        return False
