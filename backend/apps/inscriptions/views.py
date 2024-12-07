from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import DossierInscription, Document, Certificat
from .serializers import (
    DossierInscriptionSerializer,
    DocumentSerializer,
    DocumentCreateSerializer,
    CertificatSerializer
)
from .permissions import IsOwnerOrStaff

class DossierInscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des dossiers d'inscription.
    Permet aux étudiants de soumettre et suivre leurs dossiers,
    et au personnel administratif de les gérer.
    """
    serializer_class = DossierInscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return DossierInscription.objects.all()
        return DossierInscription.objects.filter(etudiant=user)

    def perform_create(self, serializer):
        serializer.save(etudiant=self.request.user)

    @action(detail=True, methods=['post'])
    def changer_statut(self, request, pk=None):
        """Permet au personnel de changer le statut d'un dossier"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        dossier = self.get_object()
        nouveau_statut = request.data.get('statut')
        if nouveau_statut not in dict(DossierInscription.STATUT_CHOICES):
            return Response(
                {"detail": "Statut invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )

        dossier.statut = nouveau_statut
        if nouveau_statut == 'VALIDE':
            dossier.date_validation = timezone.now()
        dossier.save()

        return Response(
            DossierInscriptionSerializer(dossier).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def documents_manquants(self, request, pk=None):
        """Liste les documents manquants pour un dossier"""
        dossier = self.get_object()
        documents_requis = set(dict(Document.TYPE_CHOICES).keys())
        documents_soumis = set(
            dossier.documents.filter(valide=True).values_list('type_document', flat=True)
        )
        manquants = documents_requis - documents_soumis
        return Response({
            "documents_manquants": [
                {
                    "type": doc_type,
                    "nom": dict(Document.TYPE_CHOICES)[doc_type]
                }
                for doc_type in manquants
            ]
        })

class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des documents d'inscription"""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentCreateSerializer
        return DocumentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(dossier__etudiant=user)

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """Permet au personnel de valider un document"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        document = self.get_object()
        document.valide = True
        document.commentaire = request.data.get('commentaire', '')
        document.save()

        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_200_OK
        )

class CertificatViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour la consultation des certificats"""
    serializer_class = CertificatSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Certificat.objects.all()
        return Certificat.objects.filter(dossier__etudiant=user)
