from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from ..models import (
    Categorie,
    Ressource,
    Evaluation,
    Collection
)

User = get_user_model()

class CategorieViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@test.com",
            password="adminpass123"
        )
        self.categorie = Categorie.objects.create(
            nom="Informatique",
            description="Ressources informatiques"
        )

    def test_liste_categories(self):
        """Test de la liste des catégories"""
        url = reverse('bibliotheque:categorie-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_categorie(self):
        """Test de création d'une catégorie"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('bibliotheque:categorie-list')
        data = {
            'nom': 'Programmation',
            'description': 'Ressources de programmation',
            'parent': self.categorie.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Categorie.objects.count(), 2)

class RessourceViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test@test.com",
            password="testpass123"
        )
        self.categorie = Categorie.objects.create(
            nom="Informatique",
            description="Ressources informatiques"
        )
        self.ressource = Ressource.objects.create(
            titre="Python pour débutants",
            auteurs="John Doe",
            annee_publication=2023,
            description="Guide complet pour débuter avec Python",
            type_ressource="LIVRE",
            contributeur=self.user,
            mots_cles="python, programmation, débutant",
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            ),
            est_public=True,
            est_valide=True
        )
        self.ressource.categories.add(self.categorie)

    def test_liste_ressources(self):
        """Test de la liste des ressources"""
        url = reverse('bibliotheque:ressource-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_ressource(self):
        """Test de création d'une ressource"""
        self.client.force_authenticate(user=self.user)
        url = reverse('bibliotheque:ressource-list')
        data = {
            'titre': 'JavaScript pour débutants',
            'auteurs': 'Jane Doe',
            'annee_publication': 2023,
            'description': 'Guide JavaScript',
            'type_ressource': 'LIVRE',
            'mots_cles': 'javascript, web',
            'categories': [self.categorie.id],
            'fichier': SimpleUploadedFile(
                "test2.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ressource.objects.count(), 2)

class EvaluationViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test@test.com",
            password="testpass123"
        )
        self.ressource = Ressource.objects.create(
            titre="Python pour débutants",
            auteurs="John Doe",
            annee_publication=2023,
            description="Guide complet pour débuter avec Python",
            type_ressource="LIVRE",
            contributeur=self.user,
            mots_cles="python, programmation, débutant",
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            ),
            est_public=True,
            est_valide=True
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
            username="test@test.com",
            password="testpass123"
        )
        self.ressource = Ressource.objects.create(
            titre="Python pour débutants",
            auteurs="John Doe",
            annee_publication=2023,
            description="Guide complet pour débuter avec Python",
            type_ressource="LIVRE",
            contributeur=self.user,
            mots_cles="python, programmation, débutant",
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            ),
            est_public=True,
            est_valide=True
        )

    def test_creation_collection(self):
        """Test de création d'une collection"""
        self.client.force_authenticate(user=self.user)
        url = reverse('bibliotheque:collection-list')
        data = {
            'nom': 'Mes livres Python',
            'description': 'Collection de livres Python',
            'est_publique': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Collection.objects.count(), 1)

    def test_ajout_ressource_collection(self):
        """Test d'ajout d'une ressource à une collection"""
        self.client.force_authenticate(user=self.user)
        collection = Collection.objects.create(
            nom="Mes livres Python",
            description="Collection de livres Python",
            utilisateur=self.user
        )
        url = reverse(
            'bibliotheque:collection-ajouter-ressource',
            kwargs={'pk': collection.pk}
        )
        data = {'ressource_id': self.ressource.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(collection.ressources.count(), 1)
