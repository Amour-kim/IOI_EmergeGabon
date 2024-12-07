from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Categorie,
    Ressource,
    Evaluation,
    Telechargement,
    Collection
)
from .serializers import (
    CategorieListSerializer,
    CategorieDetailSerializer,
    RessourceListSerializer,
    RessourceDetailSerializer,
    EvaluationSerializer,
    TelechargementSerializer,
    CollectionListSerializer,
    CollectionDetailSerializer
)
from .filters import RessourceFilter
from .permissions import (
    IsContributeurOrReadOnly,
    IsCollectionOwnerOrReadOnly
)
from .utils import (
    get_client_ip,
    get_user_agent,
    generate_download_link
)

class CategorieViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des catégories"""
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'ordre']

    def get_queryset(self):
        return Categorie.objects.annotate(
            nombre_ressources=Count('ressources')
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategorieDetailSerializer
        return CategorieListSerializer

    @action(detail=True)
    def arborescence(self, request, pk=None):
        """Retourne l'arborescence complète à partir de cette catégorie"""
        categorie = self.get_object()
        serializer = CategorieDetailSerializer(
            categorie,
            context={'request': request}
        )
        return Response(serializer.data)

class RessourceViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des ressources"""
    permission_classes = [IsContributeurOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = RessourceFilter
    search_fields = [
        'titre', 'auteurs', 'description',
        'mots_cles', 'categories__nom'
    ]
    ordering_fields = [
        'created_at', 'titre', 'note_moyenne',
        'nombre_telechargements', 'nombre_evaluations'
    ]

    def get_queryset(self):
        queryset = Ressource.objects.all()

        # Filtrage selon les permissions
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(est_public=True, est_valide=True) |
                Q(contributeur=self.request.user)
            )

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RessourceDetailSerializer
        return RessourceListSerializer

    def perform_create(self, serializer):
        serializer.save(contributeur=self.request.user)

    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """Validation d'une ressource par un administrateur"""
        if not request.user.is_staff:
            return Response(
                {"detail": _("Permission refusée")},
                status=status.HTTP_403_FORBIDDEN
            )

        ressource = self.get_object()
        ressource.est_valide = True
        ressource.save()

        # Notification du contributeur (à implémenter)

        return Response(
            RessourceDetailSerializer(ressource).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True)
    def telecharger(self, request, pk=None):
        """Génère un lien de téléchargement temporaire"""
        ressource = self.get_object()
        
        # Enregistrement du téléchargement
        Telechargement.objects.create(
            ressource=ressource,
            utilisateur=request.user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )

        # Génération du lien temporaire
        download_url = generate_download_link(ressource.fichier)
        
        return Response({
            'download_url': download_url,
            'expires_in': 3600  # 1 heure
        })

    @action(detail=True)
    def statistiques(self, request, pk=None):
        """Statistiques détaillées de la ressource"""
        ressource = self.get_object()
        telechargements = ressource.telechargements.all()
        evaluations = ressource.evaluations.all()

        return Response({
            'statistiques_globales': {
                'nombre_telechargements': telechargements.count(),
                'note_moyenne': ressource.note_moyenne,
                'nombre_evaluations': evaluations.count()
            },
            'telechargements_par_jour': telechargements.values(
                'created_at__date'
            ).annotate(total=Count('id')),
            'repartition_notes': evaluations.values(
                'note'
            ).annotate(total=Count('id')),
            'collections': ressource.collections.filter(
                est_publique=True
            ).count()
        })

class EvaluationViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des évaluations"""
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Evaluation.objects.all()
        return Evaluation.objects.filter(
            Q(utilisateur=self.request.user) |
            Q(ressource__contributeur=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

class TelechargementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour la consultation des téléchargements"""
    serializer_class = TelechargementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Telechargement.objects.all()
        return Telechargement.objects.filter(
            Q(utilisateur=self.request.user) |
            Q(ressource__contributeur=self.request.user)
        )

class CollectionViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des collections"""
    permission_classes = [IsCollectionOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['created_at', 'nom']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Collection.objects.all()
        return Collection.objects.filter(
            Q(utilisateur=self.request.user) |
            Q(est_publique=True)
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollectionDetailSerializer
        return CollectionListSerializer

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    @action(detail=True, methods=['post'])
    def ajouter_ressource(self, request, pk=None):
        """Ajoute une ressource à la collection"""
        collection = self.get_object()
        ressource_id = request.data.get('ressource_id')

        try:
            ressource = Ressource.objects.get(
                id=ressource_id,
                est_public=True,
                est_valide=True
            )
        except Ressource.DoesNotExist:
            return Response(
                {"detail": _("Ressource non trouvée")},
                status=status.HTTP_404_NOT_FOUND
            )

        collection.ressources.add(ressource)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def retirer_ressource(self, request, pk=None):
        """Retire une ressource de la collection"""
        collection = self.get_object()
        ressource_id = request.data.get('ressource_id')

        try:
            ressource = collection.ressources.get(id=ressource_id)
        except Ressource.DoesNotExist:
            return Response(
                {"detail": _("Ressource non trouvée dans la collection")},
                status=status.HTTP_404_NOT_FOUND
            )

        collection.ressources.remove(ressource)
        return Response(status=status.HTTP_204_NO_CONTENT)
