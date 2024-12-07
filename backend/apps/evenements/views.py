from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Count, Q
from .models import Evenement, Inscription, Document, Feedback
from .serializers import (
    EvenementListSerializer,
    EvenementDetailSerializer,
    InscriptionSerializer,
    DocumentSerializer,
    FeedbackSerializer
)

class EvenementViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des événements"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titre', 'description', 'lieu', 'public_cible']
    ordering_fields = ['date_debut', 'date_fin', 'titre', 'type_evenement']

    def get_queryset(self):
        queryset = Evenement.objects.all()
        
        # Filtres par type d'événement
        type_evenement = self.request.query_params.get('type', None)
        if type_evenement:
            queryset = queryset.filter(type_evenement=type_evenement)

        # Filtres par statut
        statut = self.request.query_params.get('statut', None)
        if statut:
            queryset = queryset.filter(statut=statut)

        # Filtres par département
        departement_id = self.request.query_params.get('departement', None)
        if departement_id:
            queryset = queryset.filter(departements__id=departement_id)

        # Filtres par date
        date_min = self.request.query_params.get('date_min', None)
        if date_min:
            queryset = queryset.filter(date_debut__gte=date_min)

        date_max = self.request.query_params.get('date_max', None)
        if date_max:
            queryset = queryset.filter(date_debut__lte=date_max)

        # Filtres par gratuité
        gratuit = self.request.query_params.get('gratuit', None)
        if gratuit is not None:
            if gratuit.lower() == 'true':
                queryset = queryset.filter(cout=0)
            else:
                queryset = queryset.filter(cout__gt=0)

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EvenementDetailSerializer
        return EvenementListSerializer

    def get_permissions(self):
        """Seul le personnel peut créer/modifier des événements"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def inscrire(self, request, pk=None):
        """Inscription à un événement"""
        evenement = self.get_object()
        
        # Vérifier si l'inscription est possible
        if evenement.statut != 'PLANIFIE':
            return Response(
                {"detail": "Les inscriptions sont closes pour cet événement"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if evenement.places_disponibles <= 0:
            return Response(
                {"detail": "Plus de places disponibles"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si l'utilisateur n'est pas déjà inscrit
        if Inscription.objects.filter(
            evenement=evenement,
            participant=request.user
        ).exists():
            return Response(
                {"detail": "Vous êtes déjà inscrit à cet événement"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Créer l'inscription
        inscription = Inscription.objects.create(
            evenement=evenement,
            participant=request.user,
            commentaire=request.data.get('commentaire', '')
        )

        # Mettre à jour le nombre de places disponibles
        evenement.places_disponibles -= 1
        evenement.save()

        return Response(
            InscriptionSerializer(inscription).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def annuler_inscription(self, request, pk=None):
        """Annulation d'une inscription"""
        evenement = self.get_object()
        try:
            inscription = Inscription.objects.get(
                evenement=evenement,
                participant=request.user
            )
        except Inscription.DoesNotExist:
            return Response(
                {"detail": "Vous n'êtes pas inscrit à cet événement"},
                status=status.HTTP_404_NOT_FOUND
            )

        if evenement.date_debut <= timezone.now():
            return Response(
                {"detail": "Impossible d'annuler une inscription pour un événement passé"},
                status=status.HTTP_400_BAD_REQUEST
            )

        inscription.statut = 'ANNULEE'
        inscription.save()

        # Remettre à disposition la place
        evenement.places_disponibles += 1
        evenement.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True)
    def participants(self, request, pk=None):
        """Liste des participants à l'événement"""
        if not request.user.is_staff and request.user != self.get_object().organisateur:
            return Response(
                {"detail": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        evenement = self.get_object()
        inscriptions = evenement.inscriptions.filter(
            statut='CONFIRMEE'
        ).select_related('participant')
        
        return Response({
            'nombre_total': inscriptions.count(),
            'participants': [{
                'id': insc.participant.id,
                'nom': insc.participant.get_full_name(),
                'email': insc.participant.email,
                'presence_confirmee': insc.presence_confirmee,
                'date_inscription': insc.date_inscription
            } for insc in inscriptions]
        })

    @action(detail=True, methods=['post'])
    def confirmer_presence(self, request, pk=None):
        """Confirmation de présence pour les participants"""
        if not request.user.is_staff and request.user != self.get_object().organisateur:
            return Response(
                {"detail": "Permission refusée"},
                status=status.HTTP_403_FORBIDDEN
            )

        evenement = self.get_object()
        participant_id = request.data.get('participant_id')
        
        try:
            inscription = evenement.inscriptions.get(participant_id=participant_id)
            inscription.presence_confirmee = True
            inscription.save()
            return Response(InscriptionSerializer(inscription).data)
        except Inscription.DoesNotExist:
            return Response(
                {"detail": "Participant non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des documents"""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(
            Q(public=True) |
            Q(evenement__organisateur=self.request.user) |
            Q(evenement__inscriptions__participant=self.request.user,
              evenement__inscriptions__statut='CONFIRMEE')
        ).distinct()

    def get_permissions(self):
        """Seul le personnel peut ajouter/modifier des documents"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des feedbacks"""
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Feedback.objects.all()
        return Feedback.objects.filter(participant=self.request.user)

    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)

    def get_permissions(self):
        """Protection des feedbacks"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @action(detail=False)
    def statistiques(self, request, pk=None):
        """Statistiques des feedbacks pour un événement"""
        evenement_id = request.query_params.get('evenement')
        if not evenement_id:
            return Response(
                {"detail": "Paramètre 'evenement' requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        feedbacks = Feedback.objects.filter(evenement_id=evenement_id)
        
        return Response({
            'nombre_total': feedbacks.count(),
            'note_moyenne': feedbacks.aggregate(Avg('note'))['note__avg'],
            'repartition_notes': feedbacks.values('note').annotate(
                total=Count('id')
            ),
            'anonymes': feedbacks.filter(anonyme=True).count()
        })
