from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Faculte, Departement, Programme, Cours

User = get_user_model()

class FaculteViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@univ-gabon.ga",
            password="adminpass123"
        )
        self.doyen = User.objects.create_user(
            username="doyen@univ-gabon.ga",
            password="testpass123"
        )
        self.faculte = Faculte.objects.create(
            nom="Sciences",
            code="FST",
            doyen=self.doyen
        )

    def test_liste_facultes(self):
        """Test de la liste des facultés"""
        url = reverse('departements:faculte-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_faculte(self):
        """Test de création d'une faculté"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('departements:faculte-list')
        data = {
            'nom': 'Lettres',
            'code': 'FLSH',
            'description': 'Faculté des Lettres et Sciences Humaines',
            'doyen': self.doyen.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Faculte.objects.count(), 2)

class DepartementViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@univ-gabon.ga",
            password="adminpass123"
        )
        self.faculte = Faculte.objects.create(
            nom="Sciences",
            code="FST"
        )
        self.chef_dept = User.objects.create_user(
            username="chef@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO",
            faculte=self.faculte,
            chef_departement=self.chef_dept
        )

    def test_liste_departements(self):
        """Test de la liste des départements"""
        url = reverse('departements:departement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_departement(self):
        """Test de création d'un département"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('departements:departement-list')
        data = {
            'nom': 'Mathématiques',
            'code': 'MATH',
            'faculte': self.faculte.id,
            'chef_departement': self.chef_dept.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Departement.objects.count(), 2)

class ProgrammeViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@univ-gabon.ga",
            password="adminpass123"
        )
        self.faculte = Faculte.objects.create(
            nom="Sciences",
            code="FST"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO",
            faculte=self.faculte
        )
        self.programme = Programme.objects.create(
            nom="Licence Informatique",
            code="LI",
            departement=self.departement,
            niveau="L",
            duree=3
        )

    def test_liste_programmes(self):
        """Test de la liste des programmes"""
        url = reverse('departements:programme-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_programme(self):
        """Test de création d'un programme"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('departements:programme-list')
        data = {
            'nom': 'Master Informatique',
            'code': 'MI',
            'departement': self.departement.id,
            'niveau': 'M',
            'duree': 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Programme.objects.count(), 2)

class CoursViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@univ-gabon.ga",
            password="adminpass123"
        )
        self.faculte = Faculte.objects.create(
            nom="Sciences",
            code="FST"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO",
            faculte=self.faculte
        )
        self.enseignant = User.objects.create_user(
            username="prof@univ-gabon.ga",
            password="testpass123"
        )
        self.cours = Cours.objects.create(
            code="INF101",
            intitule="Introduction à la programmation",
            departement=self.departement,
            credits=6,
            niveau="L1",
            semestre="S1"
        )
        self.cours.enseignants.add(self.enseignant)

    def test_liste_cours(self):
        """Test de la liste des cours"""
        url = reverse('departements:cours-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_cours(self):
        """Test de création d'un cours"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('departements:cours-list')
        data = {
            'code': 'INF102',
            'intitule': 'Algorithmique',
            'departement': self.departement.id,
            'credits': 6,
            'niveau': 'L1',
            'semestre': 'S1',
            'enseignants': [self.enseignant.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cours.objects.count(), 2)
