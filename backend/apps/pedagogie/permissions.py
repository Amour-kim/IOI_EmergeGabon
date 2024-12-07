from rest_framework import permissions

class IsResponsableOrAdmin(permissions.BasePermission):
    """
    Permission permettant uniquement aux responsables ou aux administrateurs
    d'accéder à la vue.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        # Vérifie si l'utilisateur est responsable de quelque chose
        return any([
            request.user.departements_diriges.exists(),
            request.user.filieres_dirigees.exists(),
            request.user.ues_dirigees.exists()
        ])
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        # Vérifie si l'utilisateur est responsable de l'objet
        if hasattr(obj, 'responsable'):
            return obj.responsable == request.user
        
        return False

class IsEnseignantOrAdmin(permissions.BasePermission):
    """
    Permission permettant uniquement aux enseignants ou aux administrateurs
    d'accéder à la vue.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        # Vérifie si l'utilisateur est enseignant
        return any([
            request.user.ecues_enseignees.exists(),
            request.user.seances_enseignees.exists()
        ])
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        # Vérifie si l'utilisateur est l'enseignant de l'objet
        if hasattr(obj, 'enseignant'):
            return obj.enseignant == request.user
        elif hasattr(obj, 'ecue'):
            return obj.ecue.enseignant == request.user
        
        return False

class ReadOnly(permissions.BasePermission):
    """
    Permission permettant uniquement la lecture des données.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
