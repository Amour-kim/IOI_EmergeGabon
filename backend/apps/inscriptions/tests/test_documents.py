import os
from datetime import date
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management import call_command
from django.template.loader import render_to_string
from ..models import DossierInscription, Document, Certificat

User = get_user_model()

@override_settings(MEDIA_ROOT='/tmp/test_media/')
class DocumentsTests(TestCase):
    def setUp(self):
        # Création d'un utilisateur test
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Jean',
            last_name='Dupont',
            date_naissance=date(2000, 1, 1),
            lieu_naissance='Libreville',
            matricule='2023001'
        )
        
        # Création d'un dossier d'inscription
        self.dossier = DossierInscription.objects.create(
            etudiant=self.user,
            annee_academique='2023-2024',
            niveau_etude='Licence 1',
            statut='VALIDE'
        )
        
        # Création des documents requis
        self.document = Document.objects.create(
            dossier=self.dossier,
            type_document='IDENTITE',
            fichier=SimpleUploadedFile(
                'carte_identite.pdf',
                b'contenu factice'
            ),
            valide=True
        )

    def tearDown(self):
        # Nettoyage des fichiers de test
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        if os.path.exists(settings.MEDIA_ROOT):
            os.rmdir(settings.MEDIA_ROOT)

    def test_generation_certificat_scolarite(self):
        # Test du rendu du template
        context = {
            'etudiant': self.user,
            'certificat': Certificat.objects.create(
                dossier=self.dossier,
                type_certificat='SCOLARITE',
                numero='CS-2023001',
                valide_jusqu_au=date(2024, 9, 30)
            ),
            'universite': {
                'nom': 'Université Omar Bongo',
                'adresse': 'BP 13131 Libreville',
                'ville': 'Libreville',
                'site_web': 'https://uob.ga'
            }
        }
        
        html = render_to_string(
            'inscriptions/certificat_scolarite.html',
            context
        )
        
        self.assertIn(self.user.get_full_name(), html)
        self.assertIn(self.dossier.annee_academique, html)
        self.assertIn(self.dossier.niveau_etude, html)
        self.assertIn('CS-2023001', html)

    def test_generation_attestation_inscription(self):
        context = {
            'etudiant': self.user,
            'certificat': Certificat.objects.create(
                dossier=self.dossier,
                type_certificat='INSCRIPTION',
                numero='AI-2023001',
                valide_jusqu_au=date(2024, 9, 30)
            ),
            'universite': {
                'nom': 'Université Omar Bongo',
                'recteur': {
                    'titre': 'Professeur',
                    'nom': 'Jean SMITH'
                }
            }
        }
        
        html = render_to_string(
            'inscriptions/attestation_inscription.html',
            context
        )
        
        self.assertIn(self.user.get_full_name(), html)
        self.assertIn('AI-2023001', html)
        self.assertIn('Professeur Jean SMITH', html)

    def test_generation_carte_etudiant(self):
        context = {
            'etudiant': self.user,
            'certificat': Certificat.objects.create(
                dossier=self.dossier,
                type_certificat='CARTE',
                numero='CE-2023001',
                valide_jusqu_au=date(2024, 9, 30)
            ),
            'universite': {
                'nom': 'Université Omar Bongo',
                'nom_court': 'UOB'
            }
        }
        
        html = render_to_string(
            'inscriptions/carte_etudiant.html',
            context
        )
        
        self.assertIn(self.user.matricule, html)
        self.assertIn(self.user.get_full_name(), html)
        self.assertIn('2023-2024', html)

    def test_commande_generer_cartes(self):
        # Test de la commande de génération des cartes
        args = []
        opts = {'force': False, 'dossier': None}
        
        # Vérification qu'aucune carte n'existe
        self.assertEqual(
            Certificat.objects.filter(type_certificat='CARTE').count(),
            0
        )
        
        # Exécution de la commande
        call_command('generer_cartes', *args, **opts)
        
        # Vérification qu'une carte a été générée
        self.assertEqual(
            Certificat.objects.filter(type_certificat='CARTE').count(),
            1
        )
        
        # Vérification des détails de la carte
        carte = Certificat.objects.get(type_certificat='CARTE')
        self.assertEqual(carte.dossier, self.dossier)
        self.assertTrue(carte.fichier.name.endswith('.pdf'))
        self.assertTrue(os.path.exists(
            os.path.join(settings.MEDIA_ROOT, carte.fichier.name)
        ))
        
        # Test de la régénération forcée
        opts['force'] = True
        call_command('generer_cartes', *args, **opts)
        
        # Vérification qu'une seule carte existe toujours
        self.assertEqual(
            Certificat.objects.filter(type_certificat='CARTE').count(),
            1
        )
        
        # Test de la génération pour un dossier spécifique
        opts['dossier'] = self.dossier.id
        call_command('generer_cartes', *args, **opts)
        
        # Vérification que la carte a été régénérée
        carte.refresh_from_db()
        self.assertTrue(
            carte.date_generation > carte.date_generation
        )
