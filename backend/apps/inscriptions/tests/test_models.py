from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.departements.models import Departement
from ..models import DossierInscription, Document, Certificat

User = get_user_model()

class DossierInscriptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.dossier = DossierInscription.objects.create(
            etudiant=self.user,
            annee_academique="2023-2024",
            niveau_etude="LICENCE 1",
            departement=self.departement
        )

    def test_creation_dossier(self):
        """Test de création d'un dossier d'inscription"""
        self.assertEqual(self.dossier.statut, 'EN_ATTENTE')
        self.assertIsNotNone(self.dossier.date_soumission)
        self.assertIsNone(self.dossier.date_validation)

    def test_str_representation(self):
        """Test de la représentation string du dossier"""
        expected = f"Dossier de {self.user.get_full_name()} - 2023-2024"
        self.assertEqual(str(self.dossier), expected)

class DocumentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.dossier = DossierInscription.objects.create(
            etudiant=self.user,
            annee_academique="2023-2024",
            niveau_etude="LICENCE 1",
            departement=self.departement
        )
        self.document = Document.objects.create(
            dossier=self.dossier,
            type_document='IDENTITE',
            fichier='documents_inscription/test.pdf'
        )

    def test_creation_document(self):
        """Test de création d'un document"""
        self.assertFalse(self.document.valide)
        self.assertEqual(self.document.type_document, 'IDENTITE')

    def test_str_representation(self):
        """Test de la représentation string du document"""
        expected = f"Pièce d'identité - {self.user.get_full_name()}"
        self.assertEqual(str(self.document), expected)

class CertificatTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.dossier = DossierInscription.objects.create(
            etudiant=self.user,
            annee_academique="2023-2024",
            niveau_etude="LICENCE 1",
            departement=self.departement
        )
        self.certificat = Certificat.objects.create(
            dossier=self.dossier,
            type_certificat='SCOLARITE',
            numero='CERT-2023-001',
            fichier='certificats/test.pdf',
            valide_jusqu_au=timezone.now().date() + timedelta(days=365)
        )

    def test_creation_certificat(self):
        """Test de création d'un certificat"""
        self.assertEqual(self.certificat.type_certificat, 'SCOLARITE')
        self.assertIsNotNone(self.certificat.date_generation)

    def test_str_representation(self):
        """Test de la représentation string du certificat"""
        expected = f"Certificat de scolarité - CERT-2023-001"
        self.assertEqual(str(self.certificat), expected)
