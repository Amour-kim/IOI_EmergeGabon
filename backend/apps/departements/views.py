from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Faculte, Departement, Programme, Cours
from .serializers import (
    FaculteSerializer,
    DepartementSerializer,
    ProgrammeListSerializer,
    ProgrammeDetailSerializer,
    CoursListSerializer,
    CoursDetailSerializer
)

class FaculteViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des facultés"""
    queryset = Faculte.objects.all()
    serializer_class = FaculteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'code', 'description']
    ordering_fields = ['nom', 'code', 'date_creation']

    def get_permissions(self):
        """Seul le personnel peut modifier les facultés"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=True)
    def statistiques(self, request, pk=None):
        """Statistiques de la faculté"""
        faculte = self.get_object()
        return Response({
            'nombre_departements': faculte.departements.count(),
            'nombre_programmes': Programme.objects.filter(
                departement__faculte=faculte
            ).count(),
            'nombre_cours': Cours.objects.filter(
                programme__departement__faculte=faculte
            ).count(),
            'programmes_par_niveau': Programme.objects.filter(
                departement__faculte=faculte
            ).values('niveau').annotate(total=Count('id')),
            'cours_par_type': Cours.objects.filter(
                programme__departement__faculte=faculte
            ).values('type_cours').annotate(total=Count('id'))
        })

class DepartementViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des départements"""
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'code', 'description', 'faculte__nom']
    ordering_fields = ['nom', 'code', 'faculte__nom', 'date_creation']

    def get_permissions(self):
        """Seul le personnel peut modifier les départements"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=True)
    def statistiques(self, request, pk=None):
        """Statistiques du département"""
        departement = self.get_object()
        return Response({
            'nombre_programmes': departement.programmes.count(),
            'nombre_cours': Cours.objects.filter(
                programme__departement=departement
            ).count(),
            'programmes_par_niveau': departement.programmes.values(
                'niveau'
            ).annotate(total=Count('id')),
            'cours_par_semestre': Cours.objects.filter(
                programme__departement=departement
            ).values('semestre').annotate(total=Count('id')),
            'cours_par_type': Cours.objects.filter(
                programme__departement=departement
            ).values('type_cours').annotate(total=Count('id'))
        })

class ProgrammeViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des programmes"""
    queryset = Programme.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'nom', 'code', 'description', 'departement__nom',
        'departement__faculte__nom'
    ]
    ordering_fields = ['nom', 'code', 'niveau', 'departement__nom']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProgrammeDetailSerializer
        return ProgrammeListSerializer

    def get_permissions(self):
        """Seul le personnel peut modifier les programmes"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=True)
    def structure(self, request, pk=None):
        """Structure détaillée du programme par semestre"""
        programme = self.get_object()
        structure = {}
        cours = programme.cours.all()

        for semestre in range(1, programme.duree + 1):
            cours_semestre = cours.filter(semestre=semestre)
            structure[f'semestre_{semestre}'] = {
                'obligatoires': CoursListSerializer(
                    cours_semestre.filter(type_cours='OBLIGATOIRE'),
                    many=True
                ).data,
                'optionnels': CoursListSerializer(
                    cours_semestre.filter(type_cours='OPTIONNEL'),
                    many=True
                ).data,
                'credits_total': cours_semestre.filter(
                    type_cours='OBLIGATOIRE'
                ).aggregate(total=Count('credits'))['total']
            }

        return Response(structure)

class CoursViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des cours"""
    queryset = Cours.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'code', 'intitule', 'description', 'programme__nom',
        'programme__departement__nom'
    ]
    ordering_fields = [
        'code', 'intitule', 'credits', 'semestre',
        'programme__nom'
    ]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CoursDetailSerializer
        return CoursListSerializer

    def get_permissions(self):
        """Seul le personnel peut modifier les cours"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=True)
    def prerequis_tree(self, request, pk=None):
        """Arbre des prérequis pour un cours"""
        cours = self.get_object()
        
        def get_prerequis_recursif(cours_actuel, niveau=0, max_niveau=3):
            if niveau >= max_niveau:
                return []
            
            return [{
                'cours': CoursListSerializer(prereq).data,
                'prerequis': get_prerequis_recursif(prereq, niveau + 1, max_niveau)
            } for prereq in cours_actuel.prerequis.all()]

        return Response({
            'cours': CoursListSerializer(cours).data,
            'prerequis': get_prerequis_recursif(cours)
        })
