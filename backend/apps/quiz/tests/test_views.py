from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.departements.models import Departement, Cours
from ..models import Quiz, Question, Reponse, Tentative, ReponseEtudiant

User = get_user_model()

class QuizViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.prof = User.objects.create_user(
            username="prof@univ-gabon.ga",
            password="testpass123"
        )
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )
        self.quiz = Quiz.objects.create(
            titre="Quiz Python",
            description="Test de Python",
            cours=self.cours,
            duree=60,
            note_passage=50,
            createur=self.prof
        )

    def test_liste_quiz(self):
        """Test de la liste des quiz"""
        self.client.force_authenticate(user=self.prof)
        url = reverse('quiz:quiz-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_quiz(self):
        """Test de création d'un quiz"""
        self.client.force_authenticate(user=self.prof)
        url = reverse('quiz:quiz-list')
        data = {
            'titre': 'Nouveau Quiz',
            'description': 'Test',
            'cours': self.cours.id,
            'duree': 30,
            'note_passage': 60
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 2)

    def test_take_quiz(self):
        """Test de démarrage d'un quiz"""
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('quiz:quiz-take-quiz', args=[self.quiz.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tentative.objects.count(), 1)

class QuestionViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.prof = User.objects.create_user(
            username="prof@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )
        self.quiz = Quiz.objects.create(
            titre="Quiz Python",
            cours=self.cours,
            duree=60,
            createur=self.prof
        )

    def test_creation_question(self):
        """Test de création d'une question"""
        self.client.force_authenticate(user=self.prof)
        url = reverse('quiz:question-list')
        data = {
            'quiz': self.quiz.id,
            'texte': "Qu'est-ce que Python?",
            'type_question': 'QCM',
            'points': 2.0,
            'ordre': 1,
            'reponses': [
                {
                    'texte': 'Un langage de programmation',
                    'correcte': True,
                    'ordre': 1
                },
                {
                    'texte': 'Un serpent',
                    'correcte': False,
                    'ordre': 2
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Reponse.objects.count(), 2)

class TentativeViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.prof = User.objects.create_user(
            username="prof@univ-gabon.ga",
            password="testpass123"
        )
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )
        self.quiz = Quiz.objects.create(
            titre="Quiz Python",
            cours=self.cours,
            duree=60,
            createur=self.prof
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            texte="Qu'est-ce que Python?",
            type_question='QCM',
            points=2.0
        )
        self.reponse = Reponse.objects.create(
            question=self.question,
            texte="Un langage de programmation",
            correcte=True
        )
        self.tentative = Tentative.objects.create(
            quiz=self.quiz,
            etudiant=self.etudiant
        )

    def test_submit_tentative(self):
        """Test de soumission d'une tentative"""
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('quiz:tentative-submit', args=[self.tentative.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tentative.refresh_from_db()
        self.assertEqual(self.tentative.statut, 'TERMINEE')

class ReponseEtudiantViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.prof = User.objects.create_user(
            username="prof@univ-gabon.ga",
            password="testpass123"
        )
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )
        self.quiz = Quiz.objects.create(
            titre="Quiz Python",
            cours=self.cours,
            duree=60,
            createur=self.prof
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            texte="Qu'est-ce que Python?",
            type_question='QCM',
            points=2.0
        )
        self.reponse = Reponse.objects.create(
            question=self.question,
            texte="Un langage de programmation",
            correcte=True
        )
        self.tentative = Tentative.objects.create(
            quiz=self.quiz,
            etudiant=self.etudiant
        )

    def test_creation_reponse_etudiant(self):
        """Test de création d'une réponse étudiant"""
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('quiz:reponse-etudiant-list')
        data = {
            'tentative': self.tentative.id,
            'question': self.question.id,
            'reponses': [self.reponse.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReponseEtudiant.objects.count(), 1)
        reponse_etudiant = ReponseEtudiant.objects.first()
        self.assertTrue(reponse_etudiant.correcte)
        self.assertEqual(reponse_etudiant.points_obtenus, 2.0)
