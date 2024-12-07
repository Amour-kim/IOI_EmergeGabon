from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.universite.models import Universite
from apps.datacenter.models import (
    Datacenter, Bibliotheque, Documentation,
    Mediatheque, Livre, Document, Media
)

User = get_user_model()

class DatacenterModelTest(TestCase):
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
        self.datacenter = Datacenter.objects.create(
            universite=self.universite,
            nom='Datacenter Test',
            description='Description test',
            capacite_totale=1000,
            backup_actif=True,
            frequence_backup='QUOTIDIEN'
        )
    
    def test_creation_datacenter(self):
        """Test la création d'un datacenter"""
        self.assertEqual(self.datacenter.universite, self.universite)
        self.assertEqual(self.datacenter.nom, 'Datacenter Test')
        self.assertEqual(self.datacenter.capacite_totale, 1000)
        self.assertTrue(self.datacenter.backup_actif)
        self.assertEqual(self.datacenter.frequence_backup, 'QUOTIDIEN')
        self.assertEqual(self.datacenter.stockage_utilise, 0)
        self.assertTrue(self.datacenter.actif)

class BibliothequeModelTest(TestCase):
    def setUp(self):
        self.universite = Universite.objects.create(
            nom='Université Test',
            code='UT',
            domaine='test.edu'
        )
        self.datacenter = Datacenter.objects.create(
            universite=self.universite,
            nom='Datacenter Test',
            capacite_totale=1000
        )
        self.bibliotheque = Bibliotheque.objects.create(
            datacenter=self.datacenter,
            nom='Bibliothèque Test',
            description='Description test',
            capacite_stockage=500
        )
    
    def test_creation_bibliotheque(self):
        """Test la création d'une bibliothèque"""
        self.assertEqual(self.bibliotheque.datacenter, self.datacenter)
        self.assertEqual(self.bibliotheque.nom, 'Bibliothèque Test')
        self.assertEqual(self.bibliotheque.capacite_stockage, 500)
        self.assertEqual(self.bibliotheque.stockage_utilise, 0)

class DocumentationModelTest(TestCase):
    def setUp(self):
        self.universite = Universite.objects.create(
            nom='Université Test',
            code='UT',
            domaine='test.edu'
        )
        self.datacenter = Datacenter.objects.create(
            universite=self.universite,
            nom='Datacenter Test',
            capacite_totale=1000
        )
        self.documentation = Documentation.objects.create(
            datacenter=self.datacenter,
            nom='Documentation Test',
            description='Description test',
            capacite_stockage=300
        )
    
    def test_creation_documentation(self):
        """Test la création d'une documentation"""
        self.assertEqual(self.documentation.datacenter, self.datacenter)
        self.assertEqual(self.documentation.nom, 'Documentation Test')
        self.assertEqual(self.documentation.capacite_stockage, 300)
        self.assertEqual(self.documentation.stockage_utilise, 0)

class MediathequeModelTest(TestCase):
    def setUp(self):
        self.universite = Universite.objects.create(
            nom='Université Test',
            code='UT',
            domaine='test.edu'
        )
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
    
    def test_creation_mediatheque(self):
        """Test la création d'une médiathèque"""
        self.assertEqual(self.mediatheque.datacenter, self.datacenter)
        self.assertEqual(self.mediatheque.nom, 'Médiathèque Test')
        self.assertEqual(self.mediatheque.capacite_stockage, 200)
        self.assertEqual(self.mediatheque.stockage_utilise, 0)
