from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from apps.departements.models import Departement, Cours
from ...models import (
    Categorie, Ressource, Evaluation,
    Telechargement, Collection
)

User = get_user_model()

class CategorieTests(TestCase):
    def setUp(self):
        self.parent = Categorie.objects.create(
            nom="Sciences",
            description="Ressources scientifiques"
        )
        self.enfant = Categorie.objects.create(
            nom="Physique",
            description="Ressources de physique",
            parent=self.parent
        )

    def test_creation_categorie(self):
        """Test de création d'une catégorie"""
        self.assertEqual(self.parent.nom, "Sciences")
        self.assertEqual(self.enfant.parent, self.parent)

    def test_chemin_complet(self):
        """Test du chemin complet d'une catégorie"""
        self.assertEqual(self.parent.chemin_complet, "Sciences")
        self.assertEqual(self.enfant.chemin_complet, "Sciences > Physique")

class RessourceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="prof@univ-gabon.ga",
            password="testpass123"
        )
        self.departement = Departement.objects.create(
            nom="Physique",
            code="PHY"
        )
        self.cours = Cours.objects.create(
            intitule="Mécanique quantique",
            code="PHY301",
            departement=self.departement,
            credits=6
        )
        self.categorie = Categorie.objects.create(
            nom="Physique quantique",
            description="Ressources de physique quantique"
        )
        self.ressource = Ressource.objects.create(
            titre="Introduction à la mécanique quantique",
            type_ressource="LIVRE",
            description="Manuel d'introduction",
            auteur="Dr. Einstein",
            langue="FR",
            annee_publication=2023,
            categorie=self.categorie,
            cours=self.cours,
            proprietaire=self.user,
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )

    def test_creation_ressource(self):
        """Test de création d'une ressource"""
        self.assertEqual(self.ressource.titre, "Introduction à la mécanique quantique")
        self.assertEqual(self.ressource.type_ressource, "LIVRE")
        self.assertEqual(self.ressource.proprietaire, self.user)

    def test_statistiques(self):
        """Test des statistiques d'une ressource"""
        self.assertEqual(self.ressource.nombre_telechargements, 0)
        self.assertEqual(self.ressource.note_moyenne, 0)

class EvaluationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.categorie = Categorie.objects.create(
            nom="Physique",
            description="Ressources de physique"
        )
        self.ressource = Ressource.objects.create(
            titre="Introduction à la physique",
            type_ressource="LIVRE",
            description="Manuel d'introduction",
            auteur="Dr. Einstein",
            categorie=self.categorie,
            proprietaire=self.user,
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        self.evaluation = Evaluation.objects.create(
            ressource=self.ressource,
            utilisateur=self.user,
            note=4,
            commentaire="Très bon livre"
        )

    def test_creation_evaluation(self):
        """Test de création d'une évaluation"""
        self.assertEqual(self.evaluation.note, 4)
        self.assertEqual(self.evaluation.utilisateur, self.user)

    def test_mise_a_jour_statistiques(self):
        """Test de la mise à jour des statistiques"""
        self.ressource.refresh_from_db()
        self.assertEqual(self.ressource.note_moyenne, 4)
        self.assertEqual(self.ressource.nombre_evaluations, 1)

class TelechargementTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.categorie = Categorie.objects.create(
            nom="Physique",
            description="Ressources de physique"
        )
        self.ressource = Ressource.objects.create(
            titre="Introduction à la physique",
            type_ressource="LIVRE",
            description="Manuel d'introduction",
            auteur="Dr. Einstein",
            categorie=self.categorie,
            proprietaire=self.user,
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        self.telechargement = Telechargement.objects.create(
            ressource=self.ressource,
            utilisateur=self.user,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0"
        )

    def test_creation_telechargement(self):
        """Test de création d'un téléchargement"""
        self.assertEqual(self.telechargement.ip_address, "127.0.0.1")
        self.assertEqual(self.telechargement.utilisateur, self.user)

    def test_mise_a_jour_statistiques(self):
        """Test de la mise à jour des statistiques"""
        self.ressource.refresh_from_db()
        self.assertEqual(self.ressource.nombre_telechargements, 1)

class CollectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.categorie = Categorie.objects.create(
            nom="Physique",
            description="Ressources de physique"
        )
        self.ressource = Ressource.objects.create(
            titre="Introduction à la physique",
            type_ressource="LIVRE",
            description="Manuel d'introduction",
            auteur="Dr. Einstein",
            categorie=self.categorie,
            proprietaire=self.user,
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        self.collection = Collection.objects.create(
            nom="Mes livres de physique",
            description="Collection personnelle",
            utilisateur=self.user
        )
        self.collection.ressources.add(self.ressource)

    def test_creation_collection(self):
        """Test de création d'une collection"""
        self.assertEqual(self.collection.nom, "Mes livres de physique")
        self.assertEqual(self.collection.utilisateur, self.user)

    def test_ajout_ressource(self):
        """Test d'ajout d'une ressource à la collection"""
        self.assertEqual(self.collection.ressources.count(), 1)
        self.assertIn(self.ressource, self.collection.ressources.all())
