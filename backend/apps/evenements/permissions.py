from rest_framework import permissions

class IsOrganisateurOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée permettant uniquement aux organisateurs
    de modifier leurs événements.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organisateur == request.user

class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Permission permettant uniquement aux participants de modifier
    leurs inscriptions et feedbacks.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.participant == request.user

class CanAccessDocument(permissions.BasePermission):
    """
    Permission pour l'accès aux documents d'événements.
    """

    def has_object_permission(self, request, view, obj):
        if obj.public:
            return True
        if request.user.is_staff:
            return True
        if obj.evenement.organisateur == request.user:
            return True
        return obj.evenement.inscriptions.filter(
            participant=request.user,
            statut='CONFIRMEE'
        ).exists()
