from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.finances.models import (
    FraisScolarite,
    Paiement,
    Facture,
    RemboursementDemande
)
from apps.departements.models import Departement
from apps.inscriptions.models import DossierInscription

User = get_user_model()

class FinancesViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Création d'un utilisateur étudiant
        self.etudiant = User.objects.create_user(
            email="etudiant@gabon-edu.ga",
            password="testpass123",
            role="ETUDIANT"
        )
        
        # Création d'un utilisateur staff
        self.staff = User.objects.create_user(
            email="staff@gabon-edu.ga",
            password="testpass123",
            role="STAFF",
            is_staff=True
        )
        
        # Création des données de base
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        
        self.dossier = DossierInscription.objects.create(
            etudiant=self.etudiant,
            departement=self.departement,
            niveau="L1",
            annee_academique="2023-2024"
        )
        
        self.frais = FraisScolarite.objects.create(
            departement=self.departement,
            cycle="LICENCE",
            annee_academique="2023-2024",
            montant=Decimal("500000.00")
        )

    def test_liste_frais_scolarite(self):
        """Test de la liste des frais de scolarité"""
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('finances:frais-scolarite-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_creation_paiement(self):
        """Test de la création d'un paiement"""
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('finances:paiement-list')
        data = {
            'dossier_inscription': self.dossier.id,
            'type_paiement': 'SCOLARITE',
            'montant': '500000.00',
            'mode_paiement': 'MOBILE_MONEY',
            'reference': 'PAY123456'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Paiement.objects.count(), 1)
        self.assertEqual(
            Paiement.objects.first().montant,
            Decimal('500000.00')
        )

    def test_validation_paiement(self):
        """Test de la validation d'un paiement par le staff"""
        paiement = Paiement.objects.create(
            etudiant=self.etudiant,
            dossier_inscription=self.dossier,
            type_paiement="SCOLARITE",
            montant=Decimal("500000.00"),
            mode_paiement="MOBILE_MONEY",
            reference="PAY123456"
        )
        
        self.client.force_authenticate(user=self.staff)
        url = reverse('finances:paiement-valider-paiement', args=[paiement.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        paiement.refresh_from_db()
        self.assertEqual(paiement.statut, 'VALIDE')
        self.assertIsNotNone(paiement.date_validation)

    def test_creation_demande_remboursement(self):
        """Test de la création d'une demande de remboursement"""
        paiement = Paiement.objects.create(
            etudiant=self.etudiant,
            dossier_inscription=self.dossier,
            type_paiement="SCOLARITE",
            montant=Decimal("500000.00"),
            mode_paiement="MOBILE_MONEY",
            reference="PAY123456"
        )
        
        self.client.force_authenticate(user=self.etudiant)
        url = reverse('finances:remboursement-list')
        data = {
            'paiement': paiement.id,
            'motif': "Annulation d'inscription"
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RemboursementDemande.objects.count(), 1)

    def test_traitement_demande_remboursement(self):
        """Test du traitement d'une demande de remboursement par le staff"""
        paiement = Paiement.objects.create(
            etudiant=self.etudiant,
            dossier_inscription=self.dossier,
            type_paiement="SCOLARITE",
            montant=Decimal("500000.00"),
            mode_paiement="MOBILE_MONEY",
            reference="PAY123456"
        )
        remboursement = RemboursementDemande.objects.create(
            paiement=paiement,
            motif="Annulation d'inscription"
        )
        
        self.client.force_authenticate(user=self.staff)
        url = reverse('finances:remboursement-traiter-demande', args=[remboursement.id])
        data = {
            'statut': 'APPROUVE',
            'commentaire_admin': 'Remboursement approuvé'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        remboursement.refresh_from_db()
        self.assertEqual(remboursement.statut, 'APPROUVE')
        self.assertEqual(
            remboursement.commentaire_admin,
            'Remboursement approuvé'
        )

    def test_statistiques_paiements(self):
        """Test des statistiques de paiements pour le staff"""
        # Création de quelques paiements
        for i in range(3):
            Paiement.objects.create(
                etudiant=self.etudiant,
                dossier_inscription=self.dossier,
                type_paiement="SCOLARITE",
                montant=Decimal("500000.00"),
                mode_paiement="MOBILE_MONEY",
                reference=f"PAY12345{i}",
                statut="VALIDE"
            )
        
        self.client.force_authenticate(user=self.staff)
        url = reverse('finances:paiement-statistiques')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_paiements'], 3)
        self.assertEqual(
            response.data['montant_total'],
            str(Decimal('1500000.00'))
        )
