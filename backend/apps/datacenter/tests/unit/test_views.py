from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.universite.models import Universite
from apps.datacenter.models import (
    Datacenter, Bibliotheque, Documentation,
    Mediatheque, Livre, Document, Media
)

User = get_user_model()

class DatacenterViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.universite = Universite.objects.create(
            nom='Université Test',
            code='UT',
            domaine='test.edu'
        )
        self.user.universite = self.universite
        self.user.save()
        
        self.datacenter = Datacenter.objects.create(
            universite=self.universite,
            nom='Datacenter Test',
            description='Description test',
            capacite_totale=1000,
            backup_actif=True,
            frequence_backup='QUOTIDIEN'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_liste_datacenters(self):
        """Test la liste des datacenters"""
        url = reverse('datacenter-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom'], 'Datacenter Test')
    
    def test_detail_datacenter(self):
        """Test le détail d'un datacenter"""
        url = reverse('datacenter-detail', args=[self.datacenter.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom'], 'Datacenter Test')
    
    def test_statistiques_datacenter(self):
        """Test les statistiques d'un datacenter"""
        url = reverse('datacenter-statistiques', args=[self.datacenter.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('bibliotheque', response.data)
        self.assertIn('documentation', response.data)
        self.assertIn('mediatheque', response.data)
    
    def test_activer_backup(self):
        """Test l'activation du backup"""
        url = reverse('datacenter-activer-backup', args=[self.datacenter.id])
        data = {
            'frequence': 'QUOTIDIEN',
            'retention': 30
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.datacenter.refresh_from_db()
        self.assertTrue(self.datacenter.backup_actif)
        self.assertEqual(self.datacenter.frequence_backup, 'QUOTIDIEN')
    
    def test_desactiver_backup(self):
        """Test la désactivation du backup"""
        url = reverse('datacenter-desactiver-backup', args=[self.datacenter.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.datacenter.refresh_from_db()
        self.assertFalse(self.datacenter.backup_actif)

class MediathequeViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.universite = Universite.objects.create(
            nom='Université Test',
            code='UT',
            domaine='test.edu'
        )
        self.user.universite = self.universite
        self.user.save()
        
        self.datacenter = Datacenter.objects.create(
            universite=self.universite,
            nom='Datacenter Test',
            capacite_totale=1000
        )
        
        self.mediatheque = Mediatheque.objects.create(
            datacenter=self.datacenter,
            nom='Médiathèque Test',
            description='Description test',
            capacite_stockage=200
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_liste_mediatheques(self):
        """Test la liste des médiathèques"""
        url = reverse('mediatheque-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom'], 'Médiathèque Test')
    
    def test_ajouter_media(self):
        """Test l'ajout d'un média"""
        url = reverse('mediatheque-ajouter-media', args=[self.mediatheque.id])
        
        # Création d'un fichier test
        fichier = SimpleUploadedFile(
            "test.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        
        data = {
            'titre': 'Test Vidéo',
            'type_media': 'VIDEO',
            'format': 'MP4',
            'resolution': '1080p',
            'taille': 100,  # Mo
            'fichier': fichier,
            'description': 'Test description'
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['titre'], 'Test Vidéo')
        self.assertEqual(response.data['type_media'], 'VIDEO')
        
        # Vérification de la mise à jour du stockage
        self.mediatheque.refresh_from_db()
        self.assertEqual(self.mediatheque.stockage_utilise, 100)
    
    def test_ajouter_media_stockage_insuffisant(self):
        """Test l'ajout d'un média avec stockage insuffisant"""
        url = reverse('mediatheque-ajouter-media', args=[self.mediatheque.id])
        
        fichier = SimpleUploadedFile(
            "test.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        
        data = {
            'titre': 'Test Vidéo',
            'type_media': 'VIDEO',
            'format': 'MP4',
            'resolution': '1080p',
            'taille': 300,  # Plus grand que la capacité
            'fichier': fichier,
            'description': 'Test description'
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
