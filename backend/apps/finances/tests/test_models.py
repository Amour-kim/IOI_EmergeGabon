from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.finances.models import (
    FraisScolarite,
    Paiement,
    Facture,
    RemboursementDemande
)
from apps.departements.models import Departement
from apps.inscriptions.models import DossierInscription

User = get_user_model()

class FraisScolariteTests(TestCase):
    def setUp(self):
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.frais = FraisScolarite.objects.create(
            departement=self.departement,
            cycle="LICENCE",
            annee_academique="2023-2024",
            montant=Decimal("500000.00")
        )

    def test_creation_frais_scolarite(self):
        self.assertEqual(self.frais.cycle, "LICENCE")
        self.assertEqual(self.frais.montant, Decimal("500000.00"))
        self.assertEqual(str(self.frais), "Frais de scolarité - Informatique - LICENCE 2023-2024")

class PaiementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="etudiant@gabon-edu.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.dossier = DossierInscription.objects.create(
            etudiant=self.user,
            departement=self.departement,
            niveau="L1",
            annee_academique="2023-2024"
        )
        self.paiement = Paiement.objects.create(
            etudiant=self.user,
            dossier_inscription=self.dossier,
            type_paiement="SCOLARITE",
            montant=Decimal("500000.00"),
            mode_paiement="MOBILE_MONEY",
            reference="PAY123456"
        )

    def test_creation_paiement(self):
        self.assertEqual(self.paiement.statut, "EN_ATTENTE")
        self.assertEqual(self.paiement.montant, Decimal("500000.00"))
        self.assertIsNone(self.paiement.date_validation)

    def test_validation_paiement(self):
        self.paiement.statut = "VALIDE"
        self.paiement.date_validation = timezone.now()
        self.paiement.save()
        
        self.assertEqual(self.paiement.statut, "VALIDE")
        self.assertIsNotNone(self.paiement.date_validation)

class FactureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="etudiant@gabon-edu.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.dossier = DossierInscription.objects.create(
            etudiant=self.user,
            departement=self.departement,
            niveau="L1",
            annee_academique="2023-2024"
        )
        self.paiement = Paiement.objects.create(
            etudiant=self.user,
            dossier_inscription=self.dossier,
            type_paiement="SCOLARITE",
            montant=Decimal("500000.00"),
            mode_paiement="MOBILE_MONEY",
            reference="PAY123456"
        )
        self.facture = Facture.objects.create(
            paiement=self.paiement,
            numero="FACT123456",
            montant_ht=Decimal("423728.81"),  # 500000 / 1.18
            montant_ttc=Decimal("500000.00")
        )

    def test_creation_facture(self):
        self.assertEqual(self.facture.tva, Decimal("18.00"))
        self.assertEqual(self.facture.montant_ttc, Decimal("500000.00"))
        self.assertEqual(
            str(self.facture),
            f"Facture {self.facture.numero} - {self.paiement.etudiant}"
        )

class RemboursementDemandeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="etudiant@gabon-edu.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.dossier = DossierInscription.objects.create(
            etudiant=self.user,
            departement=self.departement,
            niveau="L1",
            annee_academique="2023-2024"
        )
        self.paiement = Paiement.objects.create(
            etudiant=self.user,
            dossier_inscription=self.dossier,
            type_paiement="SCOLARITE",
            montant=Decimal("500000.00"),
            mode_paiement="MOBILE_MONEY",
            reference="PAY123456"
        )
        self.remboursement = RemboursementDemande.objects.create(
            paiement=self.paiement,
            motif="Annulation d'inscription"
        )

    def test_creation_remboursement(self):
        self.assertEqual(self.remboursement.statut, "EN_ATTENTE")
        self.assertIsNone(self.remboursement.date_traitement)
        self.assertEqual(
            str(self.remboursement),
            f"Demande de remboursement - {self.paiement.reference}"
        )

    def test_traitement_remboursement(self):
        self.remboursement.statut = "APPROUVE"
        self.remboursement.date_traitement = timezone.now()
        self.remboursement.commentaire_admin = "Remboursement approuvé"
        self.remboursement.save()

        self.assertEqual(self.remboursement.statut, "APPROUVE")
        self.assertIsNotNone(self.remboursement.date_traitement)
        self.assertEqual(
            self.remboursement.commentaire_admin,
            "Remboursement approuvé"
        )
