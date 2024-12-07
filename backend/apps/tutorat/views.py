from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Count, Q
from .models import Tuteur, SeanceTutorat, Inscription, Evaluation, Support
from .serializers import (
    TuteurListSerializer,
    TuteurDetailSerializer,
    SeanceTutoratListSerializer,
    SeanceTutoratDetailSerializer,
    InscriptionSerializer,
    EvaluationSerializer,
    SupportSerializer
)

class TuteurViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des tuteurs"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'utilisateur__first_name', 'utilisateur__last_name',
        'biographie', 'departement__nom'
    ]
    ordering_fields = ['note_moyenne', 'nombre_evaluations', 'date_validation']

    def get_queryset(self):
        queryset = Tuteur.objects.all()

        # Filtres par niveau
        niveau = self.request.query_params.get('niveau', None)
        if niveau:
            queryset = queryset.filter(niveau=niveau)

        # Filtres par département
        departement_id = self.request.query_params.get('departement', None)
        if departement_id:
            queryset = queryset.filter(departement_id=departement_id)

        # Filtres par statut
        statut = self.request.query_params.get('statut', None)
        if statut:
            queryset = queryset.filter(statut=statut)

        # Filtres par note minimale
        note_min = self.request.query_params.get('note_min', None)
        if note_min:
            queryset = queryset.filter(note_moyenne__gte=float(note_min))

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TuteurDetailSerializer
        return TuteurListSerializer

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    @action(detail=True, methods=['post'])
    def valider_tuteur(self, request, pk=None):
        """Permet au personnel de valider un tuteur"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        tuteur = self.get_object()
        tuteur.statut = 'ACTIF'
        tuteur.date_validation = timezone.now()
        tuteur.commentaire_admin = request.data.get('commentaire', '')
        tuteur.save()

        return Response(
            TuteurDetailSerializer(tuteur).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True)
    def statistiques(self, request, pk=None):
        """Statistiques du tuteur"""
        tuteur = self.get_object()
        seances = tuteur.seances.all()
        
        return Response({
            'nombre_seances_total': seances.count(),
            'nombre_seances_planifiees': seances.filter(
                statut='PLANIFIEE'
            ).count(),
            'nombre_etudiants_total': Inscription.objects.filter(
                seance__tuteur=tuteur,
                statut='CONFIRMEE'
            ).count(),
            'note_moyenne': tuteur.note_moyenne,
            'nombre_evaluations': tuteur.nombre_evaluations,
            'repartition_notes': Evaluation.objects.filter(
                seance__tuteur=tuteur
            ).values('note').annotate(total=Count('id')),
            'seances_par_type': seances.values(
                'type_seance'
            ).annotate(total=Count('id'))
        })

class SeanceTutoratViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des séances de tutorat"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'objectifs', 'lieu']
    ordering_fields = ['date_debut', 'date_fin', 'tarif_horaire']

    def get_queryset(self):
        queryset = SeanceTutorat.objects.all()

        # Filtres par tuteur
        tuteur_id = self.request.query_params.get('tuteur', None)
        if tuteur_id:
            queryset = queryset.filter(tuteur_id=tuteur_id)

        # Filtres par cours
        cours_id = self.request.query_params.get('cours', None)
        if cours_id:
            queryset = queryset.filter(cours_id=cours_id)

        # Filtres par type de séance
        type_seance = self.request.query_params.get('type', None)
        if type_seance:
            queryset = queryset.filter(type_seance=type_seance)

        # Filtres par modalité
        modalite = self.request.query_params.get('modalite', None)
        if modalite:
            queryset = queryset.filter(modalite=modalite)

        # Filtres par plage de prix
        prix_min = self.request.query_params.get('prix_min', None)
        if prix_min:
            queryset = queryset.filter(tarif_horaire__gte=float(prix_min))

        prix_max = self.request.query_params.get('prix_max', None)
        if prix_max:
            queryset = queryset.filter(tarif_horaire__lte=float(prix_max))

        # Filtres par disponibilité
        if self.request.query_params.get('disponible') == 'true':
            queryset = queryset.filter(
                statut='PLANIFIEE',
                date_debut__gt=timezone.now()
            ).annotate(
                inscrits=Count('inscriptions')
            ).filter(inscrits__lt=models.F('capacite_max'))

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SeanceTutoratDetailSerializer
        return SeanceTutoratListSerializer

    @action(detail=True, methods=['post'])
    def inscrire(self, request, pk=None):
        """Inscription à une séance"""
        seance = self.get_object()
        
        # Vérifications
        if seance.statut != 'PLANIFIEE':
            return Response(
                {"detail": "Les inscriptions sont closes pour cette séance"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if seance.date_debut <= timezone.now():
            return Response(
                {"detail": "La séance a déjà commencé"},
                status=status.HTTP_400_BAD_REQUEST
            )

        inscriptions_confirmees = seance.inscriptions.filter(
            statut='CONFIRMEE'
        ).count()
        if inscriptions_confirmees >= seance.capacite_max:
            return Response(
                {"detail": "Plus de places disponibles"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Création de l'inscription
        inscription = Inscription.objects.create(
            seance=seance,
            etudiant=request.user,
            commentaire=request.data.get('commentaire', '')
        )

        return Response(
            InscriptionSerializer(inscription).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annulation d'une séance par le tuteur"""
        seance = self.get_object()
        
        if request.user != seance.tuteur.utilisateur and not request.user.is_staff:
            return Response(
                {"detail": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        if seance.statut != 'PLANIFIEE':
            return Response(
                {"detail": "Impossible d'annuler une séance déjà commencée ou terminée"},
                status=status.HTTP_400_BAD_REQUEST
            )

        seance.statut = 'ANNULEE'
        seance.save()

        # Notification des inscrits (à implémenter)

        return Response(status=status.HTTP_204_NO_CONTENT)

class InscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des inscriptions"""
    serializer_class = InscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Inscription.objects.all()
        return Inscription.objects.filter(
            Q(etudiant=self.request.user) |
            Q(seance__tuteur__utilisateur=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(etudiant=self.request.user)

class EvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des évaluations"""
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Evaluation.objects.all()
        return Evaluation.objects.filter(
            Q(etudiant=self.request.user) |
            Q(seance__tuteur__utilisateur=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(etudiant=self.request.user)

class SupportViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des supports de cours"""
    serializer_class = SupportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Support.objects.all()
        return Support.objects.filter(
            Q(seance__tuteur__utilisateur=self.request.user) |
            Q(seance__inscriptions__etudiant=self.request.user,
              seance__inscriptions__statut='CONFIRMEE')
        ).distinct()
