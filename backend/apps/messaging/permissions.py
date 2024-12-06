from rest_framework import permissions

class IsParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        if hasattr(obj, 'conversation'):
            # For messages, check the conversation
            return request.user in obj.conversation.participants.all()
        # For conversations
        return request.user in obj.participants.all()

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an announcement to edit it.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
