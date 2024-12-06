from rest_framework import permissions
from django.utils import timezone

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner or admin
        return obj == request.user or request.user.is_staff

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to edit objects.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or request.user.role == request.user.Role.TEACHER

class IsAccountActive(permissions.BasePermission):
    """
    Vérifier si le compte est actif et non verrouillé
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_active:
            return False
            
        if user.account_locked_until and user.account_locked_until > timezone.now():
            return False
            
        return True

class IsPasswordValid(permissions.BasePermission):
    """
    Vérifier si le mot de passe n'a pas expiré
    """
    def has_permission(self, request, view):
        user = request.user
        if user.must_change_password:
            return False
            
        if user.check_password_expiry():
            user.must_change_password = True
            user.save()
            return False
            
        return True
