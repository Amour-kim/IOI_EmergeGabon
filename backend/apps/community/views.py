from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import (
    Community, CommunityMembership, MembershipRequest,
    Discussion, Comment, Tag, Report
)
from .serializers import (
    CommunitySerializer, CommunityMembershipSerializer,
    MembershipRequestSerializer, DiscussionSerializer,
    CommentSerializer, TagSerializer, ReportSerializer
)
from .permissions import (
    IsCommunityMember, IsCommunityModerator, IsCommunityAdmin,
    IsDiscussionAuthor, IsCommentAuthor, CanModerateContent,
    IsNotBanned, CanCreateContent
)

class CommunityViewSet(viewsets.ModelViewSet):
    """Gestion des communautés"""
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'tags__name']
    ordering_fields = ['created_at', 'name']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsCommunityAdmin]
        elif self.action in ['join', 'leave']:
            self.permission_classes = [permissions.IsAuthenticated, IsNotBanned]
        return super().get_permissions()

    def get_queryset(self):
        queryset = Community.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(is_private=False) | 
                Q(members=self.request.user)
            ).distinct()
        return queryset

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Rejoindre une communauté"""
        community = self.get_object()
        user = request.user

        if community.is_member(user):
            return Response(
                {"detail": "Vous êtes déjà membre de cette communauté."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if community.requires_approval:
            # Créer une demande d'adhésion
            MembershipRequest.objects.create(
                user=user,
                community=community,
                message=request.data.get('message', '')
            )
            return Response({
                "detail": "Demande d'adhésion envoyée avec succès."
            })
        else:
            # Adhésion directe
            CommunityMembership.objects.create(
                user=user,
                community=community
            )
            return Response({
                "detail": "Vous avez rejoint la communauté avec succès."
            })

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Quitter une communauté"""
        community = self.get_object()
        user = request.user

        try:
            membership = CommunityMembership.objects.get(
                user=user,
                community=community
            )
            if membership.role == CommunityMembership.Role.ADMIN:
                # Vérifier s'il y a d'autres administrateurs
                other_admins = CommunityMembership.objects.filter(
                    community=community,
                    role=CommunityMembership.Role.ADMIN
                ).exclude(user=user)
                
                if not other_admins.exists():
                    return Response({
                        "detail": "Vous ne pouvez pas quitter la communauté car vous êtes le seul administrateur."
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            membership.delete()
            return Response({
                "detail": "Vous avez quitté la communauté avec succès."
            })
        except CommunityMembership.DoesNotExist:
            return Response({
                "detail": "Vous n'êtes pas membre de cette communauté."
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Obtenir les statistiques de la communauté"""
        community = self.get_object()
        stats = {
            'member_count': community.get_member_count(),
            'discussion_count': community.discussions.count(),
            'active_members': CommunityMembership.objects.filter(
                community=community,
                user__last_login__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
            'roles_distribution': CommunityMembership.objects.filter(
                community=community
            ).values('role').annotate(count=Count('id')),
            'top_contributors': CommunityMembership.objects.filter(
                community=community
            ).annotate(
                discussions=Count('user__community_discussions'),
                comments=Count('user__community_comments')
            ).order_by('-discussions', '-comments')[:5]
        }
        return Response(stats)

class MembershipRequestViewSet(viewsets.ModelViewSet):
    """Gestion des demandes d'adhésion"""
    serializer_class = MembershipRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return MembershipRequest.objects.all()
            
        # Les modérateurs peuvent voir les demandes de leurs communautés
        moderated_communities = user.community_memberships.filter(
            role__in=['MODERATOR', 'ADMIN']
        ).values_list('community', flat=True)
        
        return MembershipRequest.objects.filter(
            Q(user=user) |
            Q(community__in=moderated_communities)
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver une demande d'adhésion"""
        membership_request = self.get_object()
        community = membership_request.community

        # Vérifier les permissions
        try:
            membership = CommunityMembership.objects.get(
                user=request.user,
                community=community
            )
            if membership.role not in ['MODERATOR', 'ADMIN']:
                return Response({
                    "detail": "Vous n'avez pas la permission d'approuver les demandes."
                }, status=status.HTTP_403_FORBIDDEN)
        except CommunityMembership.DoesNotExist:
            return Response({
                "detail": "Vous n'êtes pas membre de cette communauté."
            }, status=status.HTTP_403_FORBIDDEN)

        # Créer l'adhésion
        CommunityMembership.objects.create(
            user=membership_request.user,
            community=community
        )

        # Mettre à jour la demande
        membership_request.status = MembershipRequest.Status.APPROVED
        membership_request.handled_by = request.user
        membership_request.handled_at = timezone.now()
        membership_request.save()

        return Response({
            "detail": "Demande d'adhésion approuvée avec succès."
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter une demande d'adhésion"""
        membership_request = self.get_object()
        community = membership_request.community

        # Vérifier les permissions
        try:
            membership = CommunityMembership.objects.get(
                user=request.user,
                community=community
            )
            if membership.role not in ['MODERATOR', 'ADMIN']:
                return Response({
                    "detail": "Vous n'avez pas la permission de rejeter les demandes."
                }, status=status.HTTP_403_FORBIDDEN)
        except CommunityMembership.DoesNotExist:
            return Response({
                "detail": "Vous n'êtes pas membre de cette communauté."
            }, status=status.HTTP_403_FORBIDDEN)

        # Mettre à jour la demande
        membership_request.status = MembershipRequest.Status.REJECTED
        membership_request.handled_by = request.user
        membership_request.handled_at = timezone.now()
        membership_request.save()

        return Response({
            "detail": "Demande d'adhésion rejetée avec succès."
        })

class DiscussionViewSet(viewsets.ModelViewSet):
    """Gestion des discussions"""
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommunityMember]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'tags__name']
    ordering_fields = ['created_at', 'last_activity', 'views_count']

    def get_queryset(self):
        queryset = Discussion.objects.all()
        community_id = self.request.query_params.get('community', None)
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        return queryset

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsDiscussionAuthor | CanModerateContent]
        elif self.action == 'destroy':
            self.permission_classes = [CanModerateContent]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        """Incrémenter le compteur de vues lors de la consultation"""
        instance = self.get_object()
        instance.increment_views()
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Épingler/Désépingler une discussion"""
        discussion = self.get_object()
        if not CanModerateContent().has_object_permission(request, self, discussion):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        discussion.is_pinned = not discussion.is_pinned
        discussion.save()
        
        action = "épinglée" if discussion.is_pinned else "désépinglée"
        return Response({
            "detail": f"Discussion {action} avec succès."
        })

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Verrouiller/Déverrouiller une discussion"""
        discussion = self.get_object()
        if not CanModerateContent().has_object_permission(request, self, discussion):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        discussion.is_locked = not discussion.is_locked
        discussion.save()
        
        action = "verrouillée" if discussion.is_locked else "déverrouillée"
        return Response({
            "detail": f"Discussion {action} avec succès."
        })

class CommentViewSet(viewsets.ModelViewSet):
    """Gestion des commentaires"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommunityMember]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        queryset = Comment.objects.filter(parent=None)  # Only parent comments
        discussion_id = self.request.query_params.get('discussion', None)
        if discussion_id:
            queryset = queryset.filter(discussion_id=discussion_id)
        return queryset

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsCommentAuthor | CanModerateContent]
        return super().get_permissions()

class TagViewSet(viewsets.ModelViewSet):
    """Gestion des tags"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

class ReportViewSet(viewsets.ModelViewSet):
    """Gestion des signalements"""
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Report.objects.all()
            
        # Les modérateurs peuvent voir les signalements de leurs communautés
        moderated_communities = user.community_memberships.filter(
            role__in=['MODERATOR', 'ADMIN']
        ).values_list('community', flat=True)
        
        return Report.objects.filter(
            Q(reporter=user) |
            Q(community__in=moderated_communities)
        )

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Résoudre un signalement"""
        report = self.get_object()
        if not CanModerateContent().has_object_permission(request, self, report.community):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        report.status = Report.Status.RESOLVED
        report.handled_by = request.user
        report.handled_at = timezone.now()
        report.save()
        
        return Response({
            "detail": "Signalement résolu avec succès."
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter un signalement"""
        report = self.get_object()
        if not CanModerateContent().has_object_permission(request, self, report.community):
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        report.status = Report.Status.REJECTED
        report.handled_by = request.user
        report.handled_at = timezone.now()
        report.save()
        
        return Response({
            "detail": "Signalement rejeté avec succès."
        })
