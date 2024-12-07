from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from ..models import Evenement, Inscription, Document, Feedback

User = get_user_model()

class EvenementViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@univ-gabon.ga",
            password="adminpass123"
        )
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

    def test_liste_evenements(self):
        """Test de la liste des événements"""
        url = reverse('evenements:evenement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_evenement(self):
        """Test de création d'un événement"""
        self.client.force_authenticate(user=self.organisateur)
        url = reverse('evenements:evenement-list')
        data = {
            'titre': 'Nouveau Séminaire',
            'type_evenement': 'SEMINAIRE',
            'description': 'Un nouveau séminaire',
            'date_debut': timezone.now() + timedelta(days=2),
            'date_fin': timezone.now() + timedelta(days=2, hours=2),
            'lieu': 'Salle B',
            'capacite': 50,
            'public_cible': 'Chercheurs',
            'contact_email': 'contact@univ-gabon.ga'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Evenement.objects.count(), 2)

class InscriptionViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.participant = User.objects.create_user(
            username="participant@univ-gabon.ga",
            password="testpass123"
        )
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

    def test_inscription_evenement(self):
        """Test d'inscription à un événement"""
        self.client.force_authenticate(user=self.participant)
        url = reverse('evenements:inscription-list')
        data = {
            'evenement': self.evenement.id,
            'commentaire': 'Je souhaite participer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inscription.objects.count(), 1)

class DocumentViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@univ-gabon.ga",
            password="adminpass123"
        )
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

    def test_ajout_document(self):
        """Test d'ajout d'un document"""
        self.client.force_authenticate(user=self.organisateur)
        url = reverse('evenements:document-list')
        data = {
            'evenement': self.evenement.id,
            'titre': 'Programme',
            'type_document': 'PROGRAMME',
            'description': 'Programme de la conférence',
            'public': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)

class FeedbackViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.participant = User.objects.create_user(
            username="participant@univ-gabon.ga",
            password="testpass123"
        )
        self.organisateur = User.objects.create_user(
            username="organisateur@univ-gabon.ga",
            password="testpass123"
        )
        self.evenement = Evenement.objects.create(
            titre="Conférence Test",
            type_evenement="CONFERENCE",
            description="Une conférence de test",
            date_debut=timezone.now() - timedelta(days=1),
            date_fin=timezone.now() - timedelta(hours=2),
            lieu="Amphi A",
            capacite=100,
            organisateur=self.organisateur,
            places_disponibles=100,
            public_cible="Étudiants en informatique",
            contact_email="contact@univ-gabon.ga",
            statut="TERMINE"
        )
        self.inscription = Inscription.objects.create(
            evenement=self.evenement,
            participant=self.participant,
            statut="CONFIRMEE",
            presence_confirmee=True
        )

    def test_ajout_feedback(self):
        """Test d'ajout d'un feedback"""
        self.client.force_authenticate(user=self.participant)
        url = reverse('evenements:feedback-list')
        data = {
            'evenement': self.evenement.id,
            'note': 5,
            'commentaire': 'Excellent événement',
            'points_positifs': 'Organisation parfaite',
            'points_amelioration': 'Rien à signaler'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 1)
