from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.departements.models import Departement, Cours
from ..models import Quiz, Question, Reponse, Tentative, ReponseEtudiant

User = get_user_model()

class QuizTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
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
            description="Test de Python",
            cours=self.cours,
            duree=60,
            note_passage=50,
            createur=self.user
        )

    def test_creation_quiz(self):
        """Test de création d'un quiz"""
        self.assertEqual(self.quiz.type_quiz, 'ENTRAINEMENT')
        self.assertTrue(self.quiz.actif)
        self.assertEqual(self.quiz.nombre_tentatives, 1)

    def test_str_representation(self):
        """Test de la représentation string du quiz"""
        expected = f"Quiz Python ({self.cours.intitule})"
        self.assertEqual(str(self.quiz), expected)

class QuestionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
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
            createur=self.user
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            texte="Qu'est-ce que Python?",
            type_question='QCM',
            points=2.0,
            ordre=1
        )

    def test_creation_question(self):
        """Test de création d'une question"""
        self.assertEqual(self.question.type_question, 'QCM')
        self.assertEqual(self.question.points, 2.0)
        self.assertEqual(self.question.ordre, 1)

    def test_str_representation(self):
        """Test de la représentation string de la question"""
        expected = f"Question 1 - Quiz Python"
        self.assertEqual(str(self.question), expected)

class ReponseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
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
            createur=self.user
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            texte="Qu'est-ce que Python?",
            type_question='QCM'
        )
        self.reponse = Reponse.objects.create(
            question=self.question,
            texte="Un langage de programmation",
            correcte=True,
            ordre=1
        )

    def test_creation_reponse(self):
        """Test de création d'une réponse"""
        self.assertTrue(self.reponse.correcte)
        self.assertEqual(self.reponse.ordre, 1)

    def test_str_representation(self):
        """Test de la représentation string de la réponse"""
        expected = f"Réponse 1 - Question 0"
        self.assertEqual(str(self.reponse), expected)

class TentativeTests(TestCase):
    def setUp(self):
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
        self.tentative = Tentative.objects.create(
            quiz=self.quiz,
            etudiant=self.etudiant
        )

    def test_creation_tentative(self):
        """Test de création d'une tentative"""
        self.assertEqual(self.tentative.statut, 'EN_COURS')
        self.assertIsNone(self.tentative.note)
        self.assertEqual(self.tentative.numero_tentative, 1)

    def test_str_representation(self):
        """Test de la représentation string de la tentative"""
        expected = f"Tentative 1 - {self.etudiant.get_full_name()}"
        self.assertEqual(str(self.tentative), expected)

class ReponseEtudiantTests(TestCase):
    def setUp(self):
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
            type_question='QCM'
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
        self.reponse_etudiant = ReponseEtudiant.objects.create(
            tentative=self.tentative,
            question=self.question
        )

    def test_creation_reponse_etudiant(self):
        """Test de création d'une réponse étudiant"""
        self.assertFalse(self.reponse_etudiant.correcte)
        self.assertEqual(self.reponse_etudiant.points_obtenus, 0)

    def test_str_representation(self):
        """Test de la représentation string de la réponse étudiant"""
        expected = f"Réponse de {self.etudiant.get_full_name()} - Question 0"
        self.assertEqual(str(self.reponse_etudiant), expected)
