from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import (
    Categorie,
    Ressource,
    Evaluation,
    Collection
)

User = get_user_model()

class CategorieTests(TestCase):
    def setUp(self):
        self.categorie_parent = Categorie.objects.create(
            nom="Informatique",
            description="Ressources informatiques"
        )
        self.categorie_enfant = Categorie.objects.create(
            nom="Programmation",
            description="Ressources de programmation",
            parent=self.categorie_parent
        )

    def test_chemin_complet(self):
        """Test du chemin complet d'une catégorie"""
        self.assertEqual(
            self.categorie_enfant.chemin_complet,
            "Informatique > Programmation"
        )

class RessourceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@test.com",
            password="testpass123"
        )
        self.categorie = Categorie.objects.create(
            nom="Informatique",
            description="Ressources informatiques"
        )
        self.ressource = Ressource.objects.create(
            titre="Python pour débutants",
            auteurs="John Doe",
            annee_publication=2023,
            description="Guide complet pour débuter avec Python",
            type_ressource="LIVRE",
            contributeur=self.user,
            mots_cles="python, programmation, débutant",
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        self.ressource.categories.add(self.categorie)

    def test_creation_ressource(self):
        """Test de création d'une ressource"""
        self.assertEqual(self.ressource.titre, "Python pour débutants")
        self.assertEqual(self.ressource.type_ressource, "LIVRE")
        self.assertEqual(self.ressource.categories.count(), 1)

    def test_mise_a_jour_statistiques(self):
        """Test de mise à jour des statistiques"""
        Evaluation.objects.create(
            ressource=self.ressource,
            utilisateur=self.user,
            note=4
        )
        self.ressource.refresh_from_db()
        self.assertEqual(self.ressource.note_moyenne, 4.00)
        self.assertEqual(self.ressource.nombre_evaluations, 1)

class EvaluationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@test.com",
            password="testpass123"
        )
        self.ressource = Ressource.objects.create(
            titre="Python pour débutants",
            auteurs="John Doe",
            annee_publication=2023,
            description="Guide complet pour débuter avec Python",
            type_ressource="LIVRE",
            contributeur=self.user,
            mots_cles="python, programmation, débutant",
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )

    def test_creation_evaluation(self):
        """Test de création d'une évaluation"""
        evaluation = Evaluation.objects.create(
            ressource=self.ressource,
            utilisateur=self.user,
            note=4,
            commentaire="Très bon livre"
        )
        self.assertEqual(evaluation.note, 4)
        self.assertEqual(evaluation.commentaire, "Très bon livre")

class CollectionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@test.com",
            password="testpass123"
        )
        self.ressource = Ressource.objects.create(
            titre="Python pour débutants",
            auteurs="John Doe",
            annee_publication=2023,
            description="Guide complet pour débuter avec Python",
            type_ressource="LIVRE",
            contributeur=self.user,
            mots_cles="python, programmation, débutant",
            fichier=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        self.collection = Collection.objects.create(
            nom="Mes livres Python",
            description="Collection de livres Python",
            utilisateur=self.user
        )

    def test_ajout_ressource(self):
        """Test d'ajout d'une ressource à une collection"""
        self.collection.ressources.add(self.ressource)
        self.assertEqual(self.collection.ressources.count(), 1)
        self.assertEqual(
            self.collection.ressources.first().titre,
            "Python pour débutants"
        )
