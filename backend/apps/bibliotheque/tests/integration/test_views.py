from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from apps.departements.models import Departement, Cours
from ...models import (
    Categorie, Ressource, Evaluation,
    Telechargement, Collection
)

User = get_user_model()

class CategorieViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="admin@univ-gabon.ga",
            password="testpass123",
            is_staff=True
        )
        self.categorie = Categorie.objects.create(
            nom="Sciences",
            description="Ressources scientifiques"
        )

    def test_liste_categories(self):
        """Test de la liste des catégories"""
        url = reverse('bibliotheque:categorie-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_categorie(self):
        """Test de création d'une catégorie"""
        self.client.force_authenticate(user=self.user)
        url = reverse('bibliotheque:categorie-list')
        data = {
            'nom': 'Physique',
            'description': 'Ressources de physique',
            'parent': self.categorie.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Categorie.objects.count(), 2)

class RessourceViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="prof@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Physique",
            code="PHY"
        )
        self.cours = Cours.objects.create(
            intitule="Mécanique quantique",
            code="PHY301",
            departement=self.departement,
            credits=6
        )
        self.categorie = Categorie.objects.create(
            nom="Physique",
            description="Ressources de physique"
        )

    def test_upload_ressource(self):
        """Test d'upload d'une ressource"""
        self.client.force_authenticate(user=self.user)
        url = reverse('bibliotheque:ressource-list')
        data = {
            'titre': 'Introduction à la physique',
            'type_ressource': 'LIVRE',
            'description': 'Manuel introduction',
            'auteur': 'Dr. Einstein',
            'categorie': self.categorie.id,
            'cours': self.cours.id,
            'fichier': SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ressource.objects.count(), 1)

    def test_recherche_ressource(self):
        """Test de recherche de ressources"""
        ressource = Ressource.objects.create(
            titre="Introduction à la physique",
            type_ressource="LIVRE",
            description="Manuel d'introduction",
            auteur="Dr. Einstein",
            categorie=self.categorie,
            cours=self.cours,
            proprietaire=self.user,
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        
        url = reverse('bibliotheque:ressource-list')
        response = self.client.get(url, {'search': 'physique'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class EvaluationViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.categorie = Categorie.objects.create(
            nom="Physique",
            description="Ressources de physique"
        )
        self.ressource = Ressource.objects.create(
            titre="Introduction à la physique",
            type_ressource="LIVRE",
            description="Manuel d'introduction",
            auteur="Dr. Einstein",
            categorie=self.categorie,
            proprietaire=self.user,
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )

    def test_creation_evaluation(self):
        """Test de création d'une évaluation"""
        self.client.force_authenticate(user=self.user)
        url = reverse('bibliotheque:evaluation-list')
        data = {
            'ressource': self.ressource.id,
            'note': 4,
            'commentaire': 'Très bon livre'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Evaluation.objects.count(), 1)

class CollectionViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.categorie = Categorie.objects.create(
            nom="Physique",
            description="Ressources de physique"
        )
        self.ressource = Ressource.objects.create(
            titre="Introduction à la physique",
            type_ressource="LIVRE",
            description="Manuel d'introduction",
            auteur="Dr. Einstein",
            categorie=self.categorie,
            proprietaire=self.user,
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )

    def test_creation_collection(self):
        """Test de création d'une collection"""
        self.client.force_authenticate(user=self.user)
        url = reverse('bibliotheque:collection-list')
        data = {
            'nom': 'Mes livres de physique',
            'description': 'Collection personnelle',
            'ressources': [self.ressource.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Collection.objects.count(), 1)

    def test_ajout_ressource_collection(self):
        """Test d'ajout d'une ressource à une collection"""
        self.client.force_authenticate(user=self.user)
        collection = Collection.objects.create(
            nom="Ma collection",
            utilisateur=self.user
        )
        url = reverse(
            'bibliotheque:collection-add-ressource',
            args=[collection.id]
        )
        data = {'ressource_id': self.ressource.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            self.ressource,
            collection.ressources.all()
        )
