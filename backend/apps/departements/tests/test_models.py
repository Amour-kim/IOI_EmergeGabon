from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Faculte, Departement, Programme, Cours

User = get_user_model()

class FaculteTests(TestCase):
    def setUp(self):
        self.doyen = User.objects.create_user(
            username="doyen@univ-gabon.ga",
            password="testpass123"
        )
        self.faculte = Faculte.objects.create(
            nom="Sciences",
            code="FST",
            description="Faculté des Sciences et Techniques",
            doyen=self.doyen
        )

    def test_creation_faculte(self):
        """Test de création d'une faculté"""
        self.assertEqual(self.faculte.nom, "Sciences")
        self.assertEqual(self.faculte.code, "FST")
        self.assertEqual(self.faculte.doyen, self.doyen)

class DepartementTests(TestCase):
    def setUp(self):
        self.doyen = User.objects.create_user(
            username="doyen@univ-gabon.ga",
            password="testpass123"
        )
        self.chef_dept = User.objects.create_user(
            username="chef@univ-gabon.ga",
            password="testpass123"
        )
        self.faculte = Faculte.objects.create(
            nom="Sciences",
            code="FST",
            doyen=self.doyen
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO",
            faculte=self.faculte,
            chef_departement=self.chef_dept
        )

    def test_creation_departement(self):
        """Test de création d'un département"""
        self.assertEqual(self.departement.nom, "Informatique")
        self.assertEqual(self.departement.code, "INFO")
        self.assertEqual(self.departement.faculte, self.faculte)
        self.assertEqual(self.departement.chef_departement, self.chef_dept)

class ProgrammeTests(TestCase):
    def setUp(self):
        self.faculte = Faculte.objects.create(
            nom="Sciences",
            code="FST"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO",
            faculte=self.faculte
        )
        self.programme = Programme.objects.create(
            nom="Licence Informatique",
            code="LI",
            departement=self.departement,
            niveau="L",
            duree=3
        )

    def test_creation_programme(self):
        """Test de création d'un programme"""
        self.assertEqual(self.programme.nom, "Licence Informatique")
        self.assertEqual(self.programme.code, "LI")
        self.assertEqual(self.programme.departement, self.departement)
        self.assertEqual(self.programme.niveau, "L")
        self.assertEqual(self.programme.duree, 3)

class CoursTests(TestCase):
    def setUp(self):
        self.faculte = Faculte.objects.create(
            nom="Sciences",
            code="FST"
        )
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO",
            faculte=self.faculte
        )
        self.enseignant = User.objects.create_user(
            username="prof@univ-gabon.ga",
            password="testpass123"
        )
        self.cours = Cours.objects.create(
            code="INF101",
            intitule="Introduction à la programmation",
            departement=self.departement,
            credits=6,
            niveau="L1",
            semestre="S1"
        )
        self.cours.enseignants.add(self.enseignant)

    def test_creation_cours(self):
        """Test de création d'un cours"""
        self.assertEqual(self.cours.code, "INF101")
        self.assertEqual(self.cours.intitule, "Introduction à la programmation")
        self.assertEqual(self.cours.departement, self.departement)
        self.assertEqual(self.cours.credits, 6)
        self.assertEqual(self.cours.niveau, "L1")
        self.assertEqual(self.cours.semestre, "S1")
        self.assertEqual(self.cours.enseignants.count(), 1)
        self.assertTrue(self.enseignant in self.cours.enseignants.all())
