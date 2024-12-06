from rest_framework import permissions

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to edit academic records.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or request.user.role == request.user.Role.TEACHER

class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow teachers and admins to access.
    """
    def has_permission(self, request, view):
        return (request.user.is_staff or 
                request.user.role == request.user.Role.TEACHER)
