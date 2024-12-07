from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.universite.models import Universite
from apps.datacenter.models import (
    Datacenter, Bibliotheque, Documentation,
    Mediatheque, Livre, Document, Media
)
from apps.datacenter.serializers import (
    DatacenterSerializer, BibliothequeSerializer,
    DocumentationSerializer, MediathequeSerializer,
    LivreSerializer, DocumentSerializer, MediaSerializer
)

User = get_user_model()

class DatacenterSerializerTest(TestCase):
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
        self.serializer = DatacenterSerializer(instance=self.datacenter)
    
    def test_contient_champs_attendus(self):
        """Test que le sérialiseur contient les champs attendus"""
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {
                'id', 'universite', 'nom', 'description',
                'capacite_totale', 'stockage_utilise',
                'stockage_utilise_pourcentage',
                'backup_actif', 'frequence_backup',
                'retention_backup', 'actif',
                'date_creation', 'date_modification'
            }
        )
    
    def test_stockage_utilise_pourcentage(self):
        """Test le calcul du pourcentage de stockage utilisé"""
        self.datacenter.stockage_utilise = 250  # 25% de 1000
        self.datacenter.save()
        
        serializer = DatacenterSerializer(instance=self.datacenter)
        self.assertEqual(serializer.data['stockage_utilise_pourcentage'], 25.0)

class BibliothequeSerializerTest(TestCase):
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
        self.serializer = BibliothequeSerializer(instance=self.bibliotheque)
    
    def test_contient_champs_attendus(self):
        """Test que le sérialiseur contient les champs attendus"""
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {
                'id', 'datacenter', 'nom', 'description',
                'capacite_stockage', 'stockage_utilise',
                'stockage_utilise_pourcentage'
            }
        )
    
    def test_stockage_utilise_pourcentage(self):
        """Test le calcul du pourcentage de stockage utilisé"""
        self.bibliotheque.stockage_utilise = 100  # 20% de 500
        self.bibliotheque.save()
        
        serializer = BibliothequeSerializer(instance=self.bibliotheque)
        self.assertEqual(serializer.data['stockage_utilise_pourcentage'], 20.0)

class DocumentationSerializerTest(TestCase):
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
        self.serializer = DocumentationSerializer(instance=self.documentation)
    
    def test_contient_champs_attendus(self):
        """Test que le sérialiseur contient les champs attendus"""
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {
                'id', 'datacenter', 'nom', 'description',
                'capacite_stockage', 'stockage_utilise',
                'stockage_utilise_pourcentage'
            }
        )
    
    def test_stockage_utilise_pourcentage(self):
        """Test le calcul du pourcentage de stockage utilisé"""
        self.documentation.stockage_utilise = 60  # 20% de 300
        self.documentation.save()
        
        serializer = DocumentationSerializer(instance=self.documentation)
        self.assertEqual(serializer.data['stockage_utilise_pourcentage'], 20.0)

class MediathequeSerializerTest(TestCase):
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
        self.serializer = MediathequeSerializer(instance=self.mediatheque)
    
    def test_contient_champs_attendus(self):
        """Test que le sérialiseur contient les champs attendus"""
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {
                'id', 'datacenter', 'nom', 'description',
                'capacite_stockage', 'stockage_utilise',
                'stockage_utilise_pourcentage'
            }
        )
    
    def test_stockage_utilise_pourcentage(self):
        """Test le calcul du pourcentage de stockage utilisé"""
        self.mediatheque.stockage_utilise = 40  # 20% de 200
        self.mediatheque.save()
        
        serializer = MediathequeSerializer(instance=self.mediatheque)
        self.assertEqual(serializer.data['stockage_utilise_pourcentage'], 20.0)
