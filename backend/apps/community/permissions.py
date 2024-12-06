from rest_framework import permissions

class IsCommunityMember(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est membre de la communauté"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and not obj.is_private:
            return True
        return obj.is_member(request.user)

class IsCommunityModerator(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est modérateur"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        try:
            membership = obj.memberships.get(user=request.user)
            return membership.role in ['MODERATOR', 'ADMIN']
        except:
            return False

class IsCommunityAdmin(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est administrateur"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        try:
            membership = obj.memberships.get(user=request.user)
            return membership.role == 'ADMIN'
        except:
            return False

class IsDiscussionAuthor(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est l'auteur de la discussion"""
    
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class IsCommentAuthor(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est l'auteur du commentaire"""
    
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class CanModerateContent(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur peut modérer le contenu"""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
            
        community = getattr(obj, 'community', None)
        if not community:
            community = obj
            
        try:
            membership = community.memberships.get(user=request.user)
            return membership.role in ['MODERATOR', 'ADMIN']
        except:
            return False

class IsNotBanned(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur n'est pas banni"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS and not obj.is_private:
            return True
            
        try:
            membership = obj.memberships.get(user=request.user)
            return not membership.is_banned
        except:
            return True  # Si pas membre, pas banni

class CanCreateContent(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur peut créer du contenu"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        community_id = request.data.get('community')
        if not community_id:
            return False
            
        try:
            from .models import Community, CommunityMembership
            community = Community.objects.get(id=community_id)
            membership = CommunityMembership.objects.get(
                user=request.user,
                community=community
            )
            return not membership.is_banned
        except:
            return False
