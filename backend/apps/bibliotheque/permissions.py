from rest_framework import permissions

class IsContributeurOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour les contributeurs de ressources.
    Lecture seule pour les autres utilisateurs.
    """

    def has_permission(self, request, view):
        # Autoriser les requêtes en lecture pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        # Autoriser la création pour les utilisateurs authentifiés
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Autoriser les requêtes en lecture pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        # Autoriser les modifications pour le contributeur et les admins
        return (
            request.user.is_staff or
            obj.contributeur == request.user
        )

class IsCollectionOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour les propriétaires de collections.
    Lecture seule pour les autres utilisateurs si la collection est publique.
    """

    def has_permission(self, request, view):
        # Autoriser les requêtes en lecture pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        # Autoriser la création pour les utilisateurs authentifiés
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Autoriser les requêtes en lecture si la collection est publique
        if request.method in permissions.SAFE_METHODS:
            return obj.est_publique or obj.utilisateur == request.user
        # Autoriser les modifications uniquement pour le propriétaire
        return obj.utilisateur == request.user
