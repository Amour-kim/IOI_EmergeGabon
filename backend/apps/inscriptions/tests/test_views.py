from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.departements.models import Departement
from ..models import DossierInscription, Document, Certificat

User = get_user_model()

class DossierInscriptionViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@univ-gabon.ga",
            password="adminpass123"
        )
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.dossier = DossierInscription.objects.create(
            etudiant=self.etudiant,
            annee_academique="2023-2024",
            niveau_etude="LICENCE 1",
            departement=self.departement
        )

    def test_liste_dossiers(self):
        """Test de la liste des dossiers"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('inscriptions:dossier-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_dossier(self):
        """Test de création d'un dossier"""
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('inscriptions:dossier-list')
        data = {
            'annee_academique': '2023-2024',
            'niveau_etude': 'LICENCE 2',
            'departement': self.departement.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DossierInscription.objects.count(), 2)

class DocumentViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.dossier = DossierInscription.objects.create(
            etudiant=self.etudiant,
            annee_academique="2023-2024",
            niveau_etude="LICENCE 1",
            departement=self.departement
        )

    def test_upload_document(self):
        """Test d'upload d'un document"""
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('inscriptions:document-list')
        data = {
            'dossier': self.dossier.id,
            'type_document': 'IDENTITE',
            'fichier': 'test.pdf'  # Mock file
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)

class CertificatViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin@univ-gabon.ga",
            password="adminpass123"
        )
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.dossier = DossierInscription.objects.create(
            etudiant=self.etudiant,
            annee_academique="2023-2024",
            niveau_etude="LICENCE 1",
            departement=self.departement,
            statut='VALIDE'
        )

    def test_generation_certificat(self):
        """Test de génération d'un certificat"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('inscriptions:certificat-list')
        data = {
            'dossier': self.dossier.id,
            'type_certificat': 'SCOLARITE',
            'numero': 'CERT-2023-001',
            'fichier': 'cert.pdf',  # Mock file
            'valide_jusqu_au': (timezone.now() + timezone.timedelta(days=365)).date()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Certificat.objects.count(), 1)
