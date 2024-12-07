from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Quiz, Question, Reponse, Tentative, ReponseEtudiant
from .serializers import (
    QuizListSerializer, QuizDetailSerializer,
    QuestionSerializer, ReponseSerializer,
    TentativeListSerializer, TentativeDetailSerializer,
    ReponseEtudiantSerializer
)
from .permissions import (
    IsQuizCreator, CanTakeQuiz,
    IsQuizParticipant, CanModifyResponse
)
from .filters import (
    QuizFilter, QuestionFilter,
    TentativeFilter
)

class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les quiz"""
    queryset = Quiz.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = QuizFilter
    search_fields = ['titre', 'description']
    ordering_fields = [
        'created_at', 'titre', 'date_debut',
        'date_fin'
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            # Les étudiants ne voient que les quiz actifs de leurs cours
            if self.request.user.cours_inscrits.exists():
                return queryset.filter(
                    cours__in=self.request.user.cours_inscrits.all(),
                    actif=True
                )
            return queryset.none()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        return QuizDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsQuizCreator]
        elif self.action in ['take_quiz', 'submit_quiz']:
            self.permission_classes = [IsAuthenticated, CanTakeQuiz]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(createur=self.request.user)

    @action(detail=True, methods=['post'])
    def take_quiz(self, request, pk=None):
        """Démarre une nouvelle tentative de quiz"""
        quiz = self.get_object()
        serializer = TentativeListSerializer(data={
            'quiz': quiz.id,
            'etudiant': request.user.id
        })
        
        if serializer.is_valid():
            # Détermine le numéro de la tentative
            numero = Tentative.objects.filter(
                quiz=quiz,
                etudiant=request.user
            ).count() + 1
            
            tentative = serializer.save(
                numero_tentative=numero
            )
            
            return Response(
                TentativeDetailSerializer(tentative).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'])
    def statistiques(self, request, pk=None):
        """Récupère les statistiques du quiz"""
        quiz = self.get_object()
        tentatives = quiz.tentatives.filter(statut='TERMINEE')
        
        stats = {
            'nombre_tentatives': tentatives.count(),
            'note_moyenne': tentatives.aggregate(
                avg=Avg('note')
            )['avg'] or 0,
            'repartition_notes': tentatives.values(
                'note'
            ).annotate(total=Count('id')),
            'temps_moyen': tentatives.aggregate(
                avg=Avg('temps_passe')
            )['avg'],
            'questions': []
        }
        
        for question in quiz.questions.all():
            reponses = question.reponses_etudiant.filter(
                tentative__in=tentatives
            )
            stats['questions'].append({
                'id': question.id,
                'texte': question.texte,
                'nombre_reponses': reponses.count(),
                'nombre_correctes': reponses.filter(
                    correcte=True
                ).count()
            })
        
        return Response(stats)

class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les questions"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = QuestionFilter
    ordering_fields = ['ordre', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsQuizCreator]
        return super().get_permissions()

class TentativeViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les tentatives"""
    queryset = Tentative.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter
    ]
    filterset_class = TentativeFilter
    ordering_fields = ['date_debut', 'note']

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(etudiant=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return TentativeListSerializer
        return TentativeDetailSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsQuizParticipant]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Soumet une tentative de quiz"""
        tentative = self.get_object()
        
        if tentative.statut != 'EN_COURS':
            return Response(
                {"detail": "Cette tentative est déjà terminée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calcule la note et le temps passé
        total_points = sum(
            q.points for q in tentative.quiz.questions.all()
        )
        points_obtenus = sum(
            r.points_obtenus for r in tentative.reponses_etudiant.all()
        )
        
        tentative.note = (points_obtenus / total_points) * 100
        tentative.temps_passe = timezone.now() - tentative.date_debut
        tentative.date_fin = timezone.now()
        tentative.statut = 'TERMINEE'
        tentative.save()
        
        return Response(
            TentativeDetailSerializer(tentative).data
        )

class ReponseEtudiantViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les réponses des étudiants"""
    queryset = ReponseEtudiant.objects.all()
    serializer_class = ReponseEtudiantSerializer
    permission_classes = [IsAuthenticated, CanModifyResponse]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            return queryset.filter(
                tentative__etudiant=self.request.user
            )
        return queryset

    def perform_create(self, serializer):
        # Vérifie et calcule les points pour la réponse
        question = serializer.validated_data['question']
        reponses = serializer.validated_data.get('reponses', [])
        texte_reponse = serializer.validated_data.get('texte_reponse', '')
        
        if question.type_question in ['QCM', 'QCU']:
            # Pour les questions à choix
            correctes = set(
                r.id for r in question.reponses.filter(correcte=True)
            )
            reponses_etudiant = set(r.id for r in reponses)
            
            if question.type_question == 'QCU':
                # Une seule réponse possible
                correcte = len(reponses) == 1 and reponses[0].correcte
            else:
                # Toutes les réponses doivent être correctes
                correcte = correctes == reponses_etudiant
            
            points = question.points if correcte else 0
            
        elif question.type_question == 'VRAI_FAUX':
            # Pour les questions vrai/faux
            correcte = len(reponses) == 1 and reponses[0].correcte
            points = question.points if correcte else 0
            
        else:
            # Pour les questions à réponse textuelle
            # La correction devra être faite manuellement
            correcte = False
            points = 0
        
        serializer.save(
            correcte=correcte,
            points_obtenus=points
        )
