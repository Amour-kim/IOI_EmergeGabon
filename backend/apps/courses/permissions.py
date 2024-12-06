from rest_framework import permissions

class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to edit courses.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or request.user.role == request.user.Role.TEACHER

class IsEnrolledOrTeacher(permissions.BasePermission):
    """
    Custom permission to only allow access to enrolled students or teachers.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        # Allow teachers and staff
        if user.is_staff or user.role == user.Role.TEACHER:
            return True
        # Allow enrolled students
        if obj.student == user:
            return True
        return False
