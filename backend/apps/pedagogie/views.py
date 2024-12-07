from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from .models import (
    Departement, Cycle, Filiere, UE, ECUE,
    Programme, Seance
)
from .serializers import (
    DepartementSerializer, CycleSerializer, FiliereSerializer,
    UESerializer, ECUESerializer, ProgrammeSerializer,
    SeanceSerializer, SeanceDetailSerializer
)
from .permissions import (
    IsResponsableOrAdmin, IsEnseignantOrAdmin, ReadOnly
)

class DepartementViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les départements"""
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer
    permission_classes = [IsAuthenticated & (IsResponsableOrAdmin | ReadOnly)]
    
    @action(detail=True)
    def statistiques(self, request, pk=None):
        """Retourne les statistiques du département"""
        departement = self.get_object()
        return Response({
            'nb_filieres': departement.filieres.count(),
            'nb_etudiants': departement.filieres.values(
                'inscriptions__etudiant'
            ).distinct().count(),
            'nb_enseignants': departement.filieres.values(
                'ues__ecues__enseignant'
            ).distinct().count()
        })

class CycleViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les cycles d'études"""
    queryset = Cycle.objects.all()
    serializer_class = CycleSerializer
    permission_classes = [IsAuthenticated & (IsResponsableOrAdmin | ReadOnly)]

class FiliereViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les filières"""
    queryset = Filiere.objects.all()
    serializer_class = FiliereSerializer
    permission_classes = [IsAuthenticated & (IsResponsableOrAdmin | ReadOnly)]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        departement = self.request.query_params.get('departement', None)
        cycle = self.request.query_params.get('cycle', None)
        
        if departement:
            queryset = queryset.filter(departement_id=departement)
        if cycle:
            queryset = queryset.filter(cycle_id=cycle)
        
        return queryset
    
    @action(detail=True)
    def maquette(self, request, pk=None):
        """Retourne la maquette pédagogique de la filière"""
        filiere = self.get_object()
        ues = filiere.ues.all().order_by('semestre')
        return Response({
            'filiere': FiliereSerializer(filiere).data,
            'ues': UESerializer(ues, many=True).data
        })

class UEViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les UEs"""
    queryset = UE.objects.all()
    serializer_class = UESerializer
    permission_classes = [IsAuthenticated & (IsResponsableOrAdmin | ReadOnly)]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filiere = self.request.query_params.get('filiere', None)
        semestre = self.request.query_params.get('semestre', None)
        
        if filiere:
            queryset = queryset.filter(filiere_id=filiere)
        if semestre:
            queryset = queryset.filter(semestre=semestre)
        
        return queryset

class ECUEViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les ECUEs"""
    queryset = ECUE.objects.all()
    serializer_class = ECUESerializer
    permission_classes = [IsAuthenticated & (IsEnseignantOrAdmin | ReadOnly)]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            # Filtre pour les enseignants
            queryset = queryset.filter(
                Q(enseignant=self.request.user) |
                Q(ue__filiere__responsable=self.request.user)
            )
        return queryset
    
    @action(detail=True)
    def progression(self, request, pk=None):
        """Retourne la progression du cours"""
        ecue = self.get_object()
        seances = ecue.seances.all()
        
        volume_realise = sum(
            seance.duree.total_seconds() / 3600
            for seance in seances
            if seance.statut == 'TERMINE'
        )
        
        return Response({
            'volume_total': ecue.volume_horaire_total,
            'volume_realise': volume_realise,
            'progression': (volume_realise / ecue.volume_horaire_total * 100)
            if ecue.volume_horaire_total > 0 else 0
        })

class ProgrammeViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les programmes"""
    queryset = Programme.objects.all()
    serializer_class = ProgrammeSerializer
    permission_classes = [IsAuthenticated & (IsEnseignantOrAdmin | ReadOnly)]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(ecue__enseignant=self.request.user) |
                Q(ecue__ue__filiere__responsable=self.request.user)
            )
        return queryset

class SeanceViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les séances"""
    queryset = Seance.objects.all()
    serializer_class = SeanceSerializer
    permission_classes = [IsAuthenticated & (IsEnseignantOrAdmin | ReadOnly)]
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return SeanceDetailSerializer
        return SeanceSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(enseignant=self.request.user) |
                Q(ecue__ue__filiere__responsable=self.request.user)
            )
        
        # Filtres
        ecue = self.request.query_params.get('ecue', None)
        date_debut = self.request.query_params.get('date_debut', None)
        date_fin = self.request.query_params.get('date_fin', None)
        statut = self.request.query_params.get('statut', None)
        
        if ecue:
            queryset = queryset.filter(ecue_id=ecue)
        if date_debut:
            queryset = queryset.filter(date_debut__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_fin__lte=date_fin)
        if statut:
            queryset = queryset.filter(statut=statut)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def commencer(self, request, pk=None):
        """Marque une séance comme commencée"""
        seance = self.get_object()
        if seance.statut != 'PLANIFIE':
            return Response(
                {"detail": "La séance n'est pas en statut planifié"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seance.statut = 'EN_COURS'
        seance.save()
        return Response(SeanceDetailSerializer(seance).data)
    
    @action(detail=True, methods=['post'])
    def terminer(self, request, pk=None):
        """Marque une séance comme terminée"""
        seance = self.get_object()
        if seance.statut != 'EN_COURS':
            return Response(
                {"detail": "La séance n'est pas en cours"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seance.statut = 'TERMINE'
        seance.save()
        return Response(SeanceDetailSerializer(seance).data)
    
    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annule une séance"""
        seance = self.get_object()
        if seance.statut == 'TERMINE':
            return Response(
                {"detail": "Impossible d'annuler une séance terminée"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seance.statut = 'ANNULE'
        seance.save()
        return Response(SeanceDetailSerializer(seance).data)
    
    @action(detail=False)
    def planning(self, request):
        """Retourne le planning des séances"""
        date_debut = request.query_params.get(
            'date_debut',
            timezone.now().date().isoformat()
        )
        date_fin = request.query_params.get(
            'date_fin',
            (timezone.now() + timezone.timedelta(days=7)).date().isoformat()
        )
        
        seances = self.get_queryset().filter(
            date_debut__date__gte=date_debut,
            date_debut__date__lte=date_fin
        ).order_by('date_debut')
        
        return Response(SeanceDetailSerializer(seances, many=True).data)
