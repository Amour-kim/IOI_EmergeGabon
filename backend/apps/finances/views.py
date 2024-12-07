from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from .models import FraisScolarite, Paiement, Facture, RemboursementDemande
from .serializers import (
    FraisScolariteSerializer,
    PaiementSerializer,
    FactureSerializer,
    RemboursementDemandeSerializer
)
from apps.inscriptions.permissions import IsOwnerOrStaff

class FraisScolariteViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des frais de scolarité"""
    queryset = FraisScolarite.objects.all()
    serializer_class = FraisScolariteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """Seul le personnel peut modifier les frais"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

class PaiementViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des paiements"""
    serializer_class = PaiementSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Paiement.objects.all()
        return Paiement.objects.filter(etudiant=user)

    def perform_create(self, serializer):
        serializer.save(etudiant=self.request.user)

    @action(detail=True, methods=['post'])
    def valider_paiement(self, request, pk=None):
        """Permet au personnel de valider un paiement"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        paiement = self.get_object()
        paiement.statut = 'VALIDE'
        paiement.date_validation = timezone.now()
        paiement.save()

        # Création automatique de la facture
        Facture.objects.create(
            paiement=paiement,
            montant_ht=paiement.montant,
            tva=18.00  # À ajuster selon la réglementation
        )

        return Response(
            PaiementSerializer(paiement).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Statistiques des paiements pour le personnel"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        total_valide = Paiement.objects.filter(
            statut='VALIDE'
        ).aggregate(total=Sum('montant'))['total'] or 0

        total_en_attente = Paiement.objects.filter(
            statut='EN_ATTENTE'
        ).aggregate(total=Sum('montant'))['total'] or 0

        return Response({
            "total_valide": total_valide,
            "total_en_attente": total_en_attente,
            "nombre_paiements_valides": Paiement.objects.filter(statut='VALIDE').count(),
            "nombre_paiements_en_attente": Paiement.objects.filter(statut='EN_ATTENTE').count()
        })

class FactureViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour la consultation des factures"""
    serializer_class = FactureSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Facture.objects.all()
        return Facture.objects.filter(paiement__etudiant=user)

class RemboursementDemandeViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des demandes de remboursement"""
    serializer_class = RemboursementDemandeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return RemboursementDemande.objects.all()
        return RemboursementDemande.objects.filter(paiement__etudiant=user)

    @action(detail=True, methods=['post'])
    def traiter_demande(self, request, pk=None):
        """Permet au personnel de traiter une demande de remboursement"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        demande = self.get_object()
        nouveau_statut = request.data.get('statut')
        if nouveau_statut not in dict(RemboursementDemande.STATUT_CHOICES):
            return Response(
                {"detail": "Statut invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )

        demande.statut = nouveau_statut
        demande.date_traitement = timezone.now()
        demande.commentaire_admin = request.data.get('commentaire', '')
        demande.save()

        # Si la demande est approuvée, mettre à jour le statut du paiement
        if nouveau_statut == 'APPROUVE':
            paiement = demande.paiement
            paiement.statut = 'REMBOURSE'
            paiement.save()

        return Response(
            RemboursementDemandeSerializer(demande).data,
            status=status.HTTP_200_OK
        )
