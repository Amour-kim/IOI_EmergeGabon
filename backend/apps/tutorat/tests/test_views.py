from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from apps.departements.models import Departement, Cours
from ..models import Tuteur, SeanceTutorat, Inscription, Evaluation

User = get_user_model()

class TuteurViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@univ-gabon.ga",
            password="adminpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.utilisateur = User.objects.create_user(
            username="tuteur@univ-gabon.ga",
            password="testpass123"
        )
        self.tuteur = Tuteur.objects.create(
            utilisateur=self.utilisateur,
            niveau="MASTER",
            departement=self.departement,
            biographie="Tuteur expérimenté",
            disponibilites="Lundi au vendredi"
        )

    def test_liste_tuteurs(self):
        """Test de la liste des tuteurs"""
        url = reverse('tutorat:tuteur-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_tuteur(self):
        """Test de création d'un tuteur"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('tutorat:tuteur-list')
        nouveau_user = User.objects.create_user(
            username="nouveau@univ-gabon.ga",
            password="testpass123"
        )
        data = {
            'utilisateur': nouveau_user.id,
            'niveau': 'LICENCE',
            'departement': self.departement.id,
            'biographie': 'Nouveau tuteur',
            'disponibilites': 'Weekends'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tuteur.objects.count(), 2)

class SeanceTutoratViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.utilisateur = User.objects.create_user(
            username="tuteur@univ-gabon.ga",
            password="testpass123"
        )
        self.tuteur = Tuteur.objects.create(
            utilisateur=self.utilisateur,
            niveau="MASTER",
            departement=self.departement,
            statut="ACTIF"
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )

    def test_creation_seance(self):
        """Test de création d'une séance"""
        self.client.force_authenticate(user=self.utilisateur)
        url = reverse('tutorat:seance-list')
        data = {
            'tuteur': self.tuteur.id,
            'cours': self.cours.id,
            'type_seance': 'INDIVIDUEL',
            'modalite': 'PRESENTIEL',
            'date_debut': timezone.now() + timedelta(days=1),
            'date_fin': timezone.now() + timedelta(days=1, hours=2),
            'lieu': 'Salle 101',
            'capacite_max': 5,
            'description': 'Séance test',
            'objectifs': 'Objectifs test',
            'tarif_horaire': 5000
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SeanceTutorat.objects.count(), 1)

class InscriptionViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.tuteur_user = User.objects.create_user(
            username="tuteur@univ-gabon.ga",
            password="testpass123"
        )
        self.tuteur = Tuteur.objects.create(
            utilisateur=self.tuteur_user,
            niveau="MASTER",
            departement=self.departement,
            statut="ACTIF"
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )
        self.seance = SeanceTutorat.objects.create(
            tuteur=self.tuteur,
            cours=self.cours,
            type_seance="INDIVIDUEL",
            modalite="PRESENTIEL",
            date_debut=timezone.now() + timedelta(days=1),
            date_fin=timezone.now() + timedelta(days=1, hours=2),
            lieu="Salle 101",
            capacite_max=5,
            tarif_horaire=5000
        )
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )

    def test_inscription_seance(self):
        """Test d'inscription à une séance"""
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('tutorat:inscription-list')
        data = {
            'seance': self.seance.id,
            'commentaire': 'Je souhaite participer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inscription.objects.count(), 1)

class EvaluationViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.tuteur_user = User.objects.create_user(
            username="tuteur@univ-gabon.ga",
            password="testpass123"
        )
        self.tuteur = Tuteur.objects.create(
            utilisateur=self.tuteur_user,
            niveau="MASTER",
            departement=self.departement,
            statut="ACTIF"
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )
        self.seance = SeanceTutorat.objects.create(
            tuteur=self.tuteur,
            cours=self.cours,
            type_seance="INDIVIDUEL",
            modalite="PRESENTIEL",
            date_debut=timezone.now() - timedelta(days=1),
            date_fin=timezone.now() - timedelta(hours=2),
            lieu="Salle 101",
            capacite_max=5,
            tarif_horaire=5000,
            statut="TERMINEE"
        )
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.inscription = Inscription.objects.create(
            seance=self.seance,
            etudiant=self.etudiant,
            statut="CONFIRMEE",
            presence_confirmee=True
        )

    def test_ajout_evaluation(self):
        """Test d'ajout d'une évaluation"""
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('tutorat:evaluation-list')
        data = {
            'seance': self.seance.id,
            'note': 5,
            'commentaire': 'Excellent cours',
            'points_forts': 'Clarté des explications',
            'points_amelioration': 'Rien à signaler'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Evaluation.objects.count(), 1)
