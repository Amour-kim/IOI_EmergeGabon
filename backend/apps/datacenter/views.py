from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .models import (
    Datacenter, Bibliotheque, Documentation,
    Mediatheque, Livre, Document, Media
)
from .serializers import (
    DatacenterSerializer, BibliothequeSerializer,
    DocumentationSerializer, MediathequeSerializer,
    LivreSerializer, DocumentSerializer, MediaSerializer
)
from .services import DatacenterService

class DatacenterViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle Datacenter"""
    serializer_class = DatacenterSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les datacenters de l'université de l'utilisateur"""
        return Datacenter.objects.filter(
            universite=self.request.user.universite
        )
    
    @action(detail=True, methods=['get'])
    def statistiques(self, request, pk=None):
        """Retourne les statistiques du datacenter"""
        datacenter = self.get_object()
        stats = DatacenterService.verifier_stockage(datacenter)
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def activer_backup(self, request, pk=None):
        """Active le backup automatique"""
        datacenter = self.get_object()
        frequence = request.data.get('frequence', 'QUOTIDIEN')
        retention = request.data.get('retention', 30)
        
        datacenter.backup_actif = True
        datacenter.frequence_backup = frequence
        datacenter.retention_backup = retention
        datacenter.save()
        
        return Response({
            'message': 'Backup activé avec succès',
            'frequence': frequence,
            'retention': retention
        })
    
    @action(detail=True, methods=['post'])
    def desactiver_backup(self, request, pk=None):
        """Désactive le backup automatique"""
        datacenter = self.get_object()
        datacenter.backup_actif = False
        datacenter.save()
        
        return Response({
            'message': 'Backup désactivé avec succès'
        })

class BibliothequeViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle Bibliothèque"""
    serializer_class = BibliothequeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les bibliothèques des datacenters de l'université"""
        return Bibliotheque.objects.filter(
            datacenter__universite=self.request.user.universite
        )
    
    @action(detail=True, methods=['post'])
    def ajouter_livre(self, request, pk=None):
        """Ajoute un livre à la bibliothèque"""
        bibliotheque = self.get_object()
        section_id = request.data.get('section')
        
        try:
            livre = DatacenterService.ajouter_livre(
                bibliotheque=bibliotheque,
                section_id=section_id,
                donnees=request.data
            )
            serializer = LivreSerializer(livre)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class DocumentationViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle Documentation"""
    serializer_class = DocumentationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les centres de documentation des datacenters"""
        return Documentation.objects.filter(
            datacenter__universite=self.request.user.universite
        )
    
    @action(detail=True, methods=['post'])
    def ajouter_document(self, request, pk=None):
        """Ajoute un document à la documentation"""
        documentation = self.get_object()
        
        try:
            document = DatacenterService.ajouter_document(
                documentation=documentation,
                donnees=request.data
            )
            serializer = DocumentSerializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class MediathequeViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle Médiathèque"""
    serializer_class = MediathequeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les médiathèques des datacenters"""
        return Mediatheque.objects.filter(
            datacenter__universite=self.request.user.universite
        )
    
    @action(detail=True, methods=['post'])
    def ajouter_media(self, request, pk=None):
        """Ajoute un média à la médiathèque"""
        mediatheque = self.get_object()
        
        try:
            media = DatacenterService.ajouter_media(
                mediatheque=mediatheque,
                donnees=request.data
            )
            serializer = MediaSerializer(media)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
