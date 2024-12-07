from datetime import date
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import DossierInscription, Document, Certificat

User = get_user_model()

class DocumentsAPITests(APITestCase):
    def setUp(self):
        # Création d'un utilisateur administratif
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        
        # Création d'un étudiant
        self.etudiant = User.objects.create_user(
            email='etudiant@example.com',
            password='etudiant123',
            first_name='Jean',
            last_name='Dupont',
            date_naissance=date(2000, 1, 1),
            lieu_naissance='Libreville',
            matricule='2023001'
        )
        
        # Création d'un dossier d'inscription
        self.dossier = DossierInscription.objects.create(
            etudiant=self.etudiant,
            annee_academique='2023-2024',
            niveau_etude='Licence 1',
            statut='VALIDE'
        )
        
        # Authentification en tant qu'admin
        self.client.force_authenticate(user=self.admin)

    def test_generer_certificat_scolarite(self):
        url = reverse('generer-certificat-scolarite', args=[self.dossier.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Certificat.objects.filter(
                dossier=self.dossier,
                type_certificat='SCOLARITE'
            ).exists()
        )
        
        # Vérification du contenu de la réponse
        self.assertIn('numero', response.data)
        self.assertIn('fichier', response.data)
        self.assertIn('date_generation', response.data)

    def test_generer_attestation_inscription(self):
        url = reverse('generer-attestation-inscription', args=[self.dossier.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Certificat.objects.filter(
                dossier=self.dossier,
                type_certificat='INSCRIPTION'
            ).exists()
        )

    def test_generer_carte_etudiant(self):
        url = reverse('generer-carte-etudiant', args=[self.dossier.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Certificat.objects.filter(
                dossier=self.dossier,
                type_certificat='CARTE'
            ).exists()
        )

    def test_verifier_certificat(self):
        # Création d'un certificat
        certificat = Certificat.objects.create(
            dossier=self.dossier,
            type_certificat='SCOLARITE',
            numero='CS-2023001',
            valide_jusqu_au=date(2024, 9, 30)
        )
        
        url = reverse('verifier-certificat', args=[certificat.numero])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], 'VALIDE')
        self.assertEqual(
            response.data['etudiant']['matricule'],
            self.etudiant.matricule
        )

    def test_liste_certificats_etudiant(self):
        # Création de plusieurs certificats
        Certificat.objects.create(
            dossier=self.dossier,
            type_certificat='SCOLARITE',
            numero='CS-2023001',
            valide_jusqu_au=date(2024, 9, 30)
        )
        Certificat.objects.create(
            dossier=self.dossier,
            type_certificat='INSCRIPTION',
            numero='AI-2023001',
            valide_jusqu_au=date(2024, 9, 30)
        )
        
        # Test en tant qu'étudiant
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('liste-certificats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Vérification des champs sensibles
        for certificat in response.data:
            self.assertNotIn('fichier', certificat)

    def test_permissions(self):
        # Test sans authentification
        self.client.force_authenticate(user=None)
        url = reverse('generer-certificat-scolarite', args=[self.dossier.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test en tant qu'étudiant pour une action administrative
        self.client.force_authenticate(user=self.etudiant)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test en tant qu'admin pour un autre dossier
        autre_dossier = DossierInscription.objects.create(
            etudiant=User.objects.create_user(
                email='autre@example.com',
                password='autre123',
                matricule='2023002'
            ),
            annee_academique='2023-2024',
            statut='EN_ATTENTE'
        )
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('generer-certificat-scolarite', args=[autre_dossier.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('statut', response.data)
