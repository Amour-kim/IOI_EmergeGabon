from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models import Evenement, Inscription, Document, Feedback

User = get_user_model()

class EvenementTests(TestCase):
    def setUp(self):
        self.organisateur = User.objects.create_user(
            username="organisateur@univ-gabon.ga",
            password="testpass123"
        )
        self.evenement = Evenement.objects.create(
            titre="Conférence Test",
            type_evenement="CONFERENCE",
            description="Une conférence de test",
            date_debut=timezone.now() + timedelta(days=1),
            date_fin=timezone.now() + timedelta(days=1, hours=2),
            lieu="Amphi A",
            capacite=100,
            organisateur=self.organisateur,
            places_disponibles=100,
            public_cible="Étudiants en informatique",
            contact_email="contact@univ-gabon.ga"
        )

    def test_creation_evenement(self):
        """Test de création d'un événement"""
        self.assertEqual(self.evenement.titre, "Conférence Test")
        self.assertEqual(self.evenement.type_evenement, "CONFERENCE")
        self.assertEqual(self.evenement.capacite, 100)
        self.assertEqual(self.evenement.places_disponibles, 100)

    def test_str_representation(self):
        """Test de la représentation string"""
        self.assertEqual(
            str(self.evenement),
            "Conférence Test (Conférence)"
        )

class InscriptionTests(TestCase):
    def setUp(self):
        self.organisateur = User.objects.create_user(
            username="organisateur@univ-gabon.ga",
            password="testpass123"
        )
        self.participant = User.objects.create_user(
            username="participant@univ-gabon.ga",
            password="testpass123"
        )
        self.evenement = Evenement.objects.create(
            titre="Conférence Test",
            type_evenement="CONFERENCE",
            description="Une conférence de test",
            date_debut=timezone.now() + timedelta(days=1),
            date_fin=timezone.now() + timedelta(days=1, hours=2),
            lieu="Amphi A",
            capacite=100,
            organisateur=self.organisateur,
            places_disponibles=100,
            public_cible="Étudiants en informatique",
            contact_email="contact@univ-gabon.ga"
        )
        self.inscription = Inscription.objects.create(
            evenement=self.evenement,
            participant=self.participant
        )

    def test_creation_inscription(self):
        """Test de création d'une inscription"""
        self.assertEqual(self.inscription.evenement, self.evenement)
        self.assertEqual(self.inscription.participant, self.participant)
        self.assertEqual(self.inscription.statut, "EN_ATTENTE")

    def test_unique_inscription(self):
        """Test d'unicité d'inscription"""
        with self.assertRaises(Exception):
            Inscription.objects.create(
                evenement=self.evenement,
                participant=self.participant
            )

class DocumentTests(TestCase):
    def setUp(self):
        self.organisateur = User.objects.create_user(
            username="organisateur@univ-gabon.ga",
            password="testpass123"
        )
        self.evenement = Evenement.objects.create(
            titre="Conférence Test",
            type_evenement="CONFERENCE",
            description="Une conférence de test",
            date_debut=timezone.now() + timedelta(days=1),
            date_fin=timezone.now() + timedelta(days=1, hours=2),
            lieu="Amphi A",
            capacite=100,
            organisateur=self.organisateur,
            places_disponibles=100,
            public_cible="Étudiants en informatique",
            contact_email="contact@univ-gabon.ga"
        )
        self.document = Document.objects.create(
            evenement=self.evenement,
            titre="Programme",
            type_document="PROGRAMME",
            description="Programme de la conférence"
        )

    def test_creation_document(self):
        """Test de création d'un document"""
        self.assertEqual(self.document.evenement, self.evenement)
        self.assertEqual(self.document.titre, "Programme")
        self.assertEqual(self.document.type_document, "PROGRAMME")

class FeedbackTests(TestCase):
    def setUp(self):
        self.organisateur = User.objects.create_user(
            username="organisateur@univ-gabon.ga",
            password="testpass123"
        )
        self.participant = User.objects.create_user(
            username="participant@univ-gabon.ga",
            password="testpass123"
        )
        self.evenement = Evenement.objects.create(
            titre="Conférence Test",
            type_evenement="CONFERENCE",
            description="Une conférence de test",
            date_debut=timezone.now() + timedelta(days=1),
            date_fin=timezone.now() + timedelta(days=1, hours=2),
            lieu="Amphi A",
            capacite=100,
            organisateur=self.organisateur,
            places_disponibles=100,
            public_cible="Étudiants en informatique",
            contact_email="contact@univ-gabon.ga"
        )
        self.feedback = Feedback.objects.create(
            evenement=self.evenement,
            participant=self.participant,
            note=5,
            commentaire="Excellent événement"
        )

    def test_creation_feedback(self):
        """Test de création d'un feedback"""
        self.assertEqual(self.feedback.evenement, self.evenement)
        self.assertEqual(self.feedback.participant, self.participant)
        self.assertEqual(self.feedback.note, 5)
        self.assertEqual(self.feedback.commentaire, "Excellent événement")
