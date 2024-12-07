from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from .models import User
from .serializers import (
    UserSerializer, UserCreateSerializer,
    UserUpdateSerializer, ChangePasswordSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle utilisateur"""
    
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Retourne le sérialiseur approprié"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filtre les utilisateurs selon l'université"""
        queryset = User.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                universite=self.request.user.universite
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change le mot de passe de l'utilisateur"""
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({
                'message': _('Mot de passe changé avec succès.')
            })
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def activer(self, request, pk=None):
        """Active le compte utilisateur"""
        user = self.get_object()
        user.activer()
        return Response({
            'message': _('Compte activé avec succès.')
        })
    
    @action(detail=True, methods=['post'])
    def desactiver(self, request, pk=None):
        """Désactive le compte utilisateur"""
        user = self.get_object()
        user.desactiver()
        return Response({
            'message': _('Compte désactivé avec succès.')
        })
    
    @action(detail=True, methods=['post'])
    def suspendre(self, request, pk=None):
        """Suspend le compte utilisateur"""
        user = self.get_object()
        user.suspendre()
        return Response({
            'message': _('Compte suspendu avec succès.')
        })
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retourne les informations de l'utilisateur connecté"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def enseignants(self, request):
        """Liste tous les enseignants de l'université"""
        queryset = self.get_queryset().filter(categorie='ENSEIGNANT')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def etudiants(self, request):
        """Liste tous les étudiants de l'université"""
        queryset = self.get_queryset().filter(categorie='ETUDIANT')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def professionnels(self, request):
        """Liste tous les professionnels de l'université"""
        queryset = self.get_queryset().filter(categorie='PROFESSIONNEL')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def parents(self, request):
        """Liste tous les parents"""
        queryset = self.get_queryset().filter(categorie='PARENT')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
