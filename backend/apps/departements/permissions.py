from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée permettant uniquement aux administrateurs
    de modifier les données. Lecture seule pour les autres utilisateurs.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsDepartementStaffOrReadOnly(permissions.BasePermission):
    """
    Permission permettant au personnel du département de modifier les données.
    Lecture seule pour les autres utilisateurs.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Vérifie si l'utilisateur fait partie du personnel du département
        if hasattr(obj, 'departement'):
            departement = obj.departement
        elif hasattr(obj, 'faculte'):
            departement = None  # Cas des facultés
        else:
            return False

        return (
            request.user.is_staff or
            (departement and request.user in departement.personnel.all())
        )
