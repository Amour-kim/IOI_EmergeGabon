from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.universite.models import Universite
from apps.datacenter.models import (
    Datacenter, Bibliotheque, Documentation,
    Mediatheque, Livre, Document, Media
)
from apps.datacenter.services import DatacenterService

User = get_user_model()

class DatacenterServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.universite = Universite.objects.create(
            nom='Université Test',
            code='UT',
            domaine='test.edu'
        )
    
    def test_creer_datacenter(self):
        """Test la création d'un datacenter avec ses composants"""
        datacenter = DatacenterService.creer_datacenter(
            universite=self.universite,
            type_abonnement='PREMIUM',
            nom='Datacenter Test',
            description='Description test'
        )
        
        # Vérification du datacenter
        self.assertEqual(datacenter.universite, self.universite)
        self.assertEqual(datacenter.nom, 'Datacenter Test')
        self.assertEqual(
            datacenter.capacite_totale,
            DatacenterService.LIMITES_ABONNEMENT['PREMIUM']['stockage_total']
        )
        self.assertTrue(datacenter.backup_actif)
        self.assertEqual(datacenter.frequence_backup, 'QUOTIDIEN')
        
        # Vérification des composants
        bibliotheque = datacenter.bibliotheques.first()
        self.assertIsNotNone(bibliotheque)
        self.assertEqual(
            bibliotheque.capacite_stockage,
            DatacenterService.LIMITES_ABONNEMENT['PREMIUM']['stockage_bibliotheque']
        )
        
        documentation = datacenter.documentations.first()
        self.assertIsNotNone(documentation)
        self.assertEqual(
            documentation.capacite_stockage,
            DatacenterService.LIMITES_ABONNEMENT['PREMIUM']['stockage_documentation']
        )
        
        mediatheque = datacenter.mediatheques.first()
        self.assertIsNotNone(mediatheque)
        self.assertEqual(
            mediatheque.capacite_stockage,
            DatacenterService.LIMITES_ABONNEMENT['PREMIUM']['stockage_mediatheque']
        )
    
    def test_verifier_stockage(self):
        """Test la vérification du stockage"""
        datacenter = DatacenterService.creer_datacenter(
            universite=self.universite,
            type_abonnement='STANDARD',
            nom='Datacenter Test'
        )
        
        stockage = DatacenterService.verifier_stockage(datacenter)
        
        self.assertEqual(
            stockage['total']['alloue'],
            DatacenterService.LIMITES_ABONNEMENT['STANDARD']['stockage_total']
        )
        self.assertEqual(stockage['total']['utilise'], 0)
        self.assertEqual(
            stockage['total']['disponible'],
            DatacenterService.LIMITES_ABONNEMENT['STANDARD']['stockage_total']
        )
        self.assertEqual(stockage['total']['pourcentage'], 0)
    
    def test_ajouter_media(self):
        """Test l'ajout d'un média"""
        datacenter = DatacenterService.creer_datacenter(
            universite=self.universite,
            type_abonnement='STANDARD',
            nom='Datacenter Test'
        )
        mediatheque = datacenter.mediatheques.first()
        
        # Création d'un fichier test
        fichier = SimpleUploadedFile(
            "test.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        
        media = DatacenterService.ajouter_media(
            mediatheque=mediatheque,
            donnees={
                'titre': 'Test Vidéo',
                'type_media': 'VIDEO',
                'auteur': self.user,
                'format': 'MP4',
                'resolution': '1080p',
                'taille': 100,  # Mo
                'fichier': fichier,
                'description': 'Test description'
            }
        )
        
        self.assertIsNotNone(media)
        self.assertEqual(media.titre, 'Test Vidéo')
        self.assertEqual(mediatheque.stockage_utilise, 100)
        self.assertEqual(datacenter.stockage_utilise, 100)
    
    def test_limite_stockage(self):
        """Test la limite de stockage"""
        datacenter = DatacenterService.creer_datacenter(
            universite=self.universite,
            type_abonnement='BASIC',
            nom='Datacenter Test'
        )
        mediatheque = datacenter.mediatheques.first()
        
        fichier = SimpleUploadedFile(
            "test.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        
        # Tentative d'ajout d'un fichier trop gros
        with self.assertRaises(ValidationError):
            DatacenterService.ajouter_media(
                mediatheque=mediatheque,
                donnees={
                    'titre': 'Test Vidéo',
                    'type_media': 'VIDEO',
                    'auteur': self.user,
                    'format': 'MP4',
                    'resolution': '1080p',
                    'taille': 1000,  # Plus grand que la capacité
                    'fichier': fichier,
                    'description': 'Test description'
                }
            )
