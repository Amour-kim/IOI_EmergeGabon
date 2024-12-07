from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.departements.models import Departement, Cours
from ..models import Tuteur, SeanceTutorat, Inscription, Evaluation, Support

User = get_user_model()

class TuteurTests(TestCase):
    def setUp(self):
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.utilisateur = User.objects.create_user(
            username="tuteur@univ-gabon.ga",
            password="testpass123"
        )
        self.tuteur = Tuteur.objects.create(
            utilisateur=self.utilisateur,
            niveau="MASTER",
            departement=self.departement,
            biographie="Tuteur expérimenté",
            disponibilites="Lundi au vendredi"
        )

    def test_creation_tuteur(self):
        """Test de création d'un tuteur"""
        self.assertEqual(self.tuteur.niveau, "MASTER")
        self.assertEqual(self.tuteur.departement, self.departement)
        self.assertEqual(self.tuteur.note_moyenne, 0.00)
        self.assertEqual(self.tuteur.nombre_evaluations, 0)

    def test_mise_a_jour_note(self):
        """Test de mise à jour de la note moyenne"""
        self.tuteur.mettre_a_jour_note(4.0)
        self.assertEqual(self.tuteur.note_moyenne, 4.00)
        self.assertEqual(self.tuteur.nombre_evaluations, 1)

        self.tuteur.mettre_a_jour_note(5.0)
        self.assertEqual(self.tuteur.note_moyenne, 4.50)
        self.assertEqual(self.tuteur.nombre_evaluations, 2)

class SeanceTutoratTests(TestCase):
    def setUp(self):
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.utilisateur = User.objects.create_user(
            username="tuteur@univ-gabon.ga",
            password="testpass123"
        )
        self.tuteur = Tuteur.objects.create(
            utilisateur=self.utilisateur,
            niveau="MASTER",
            departement=self.departement,
            biographie="Tuteur expérimenté",
            disponibilites="Lundi au vendredi"
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )
        self.seance = SeanceTutorat.objects.create(
            tuteur=self.tuteur,
            cours=self.cours,
            type_seance="INDIVIDUEL",
            modalite="PRESENTIEL",
            date_debut=timezone.now() + timedelta(days=1),
            date_fin=timezone.now() + timedelta(days=1, hours=2),
            lieu="Salle 101",
            capacite_max=5,
            description="Séance d'introduction",
            objectifs="Comprendre les bases",
            tarif_horaire=5000
        )

    def test_creation_seance(self):
        """Test de création d'une séance"""
        self.assertEqual(self.seance.tuteur, self.tuteur)
        self.assertEqual(self.seance.cours, self.cours)
        self.assertEqual(self.seance.type_seance, "INDIVIDUEL")
        self.assertEqual(self.seance.modalite, "PRESENTIEL")
        self.assertEqual(self.seance.capacite_max, 5)
        self.assertEqual(self.seance.tarif_horaire, 5000)

class InscriptionTests(TestCase):
    def setUp(self):
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.tuteur_user = User.objects.create_user(
            username="tuteur@univ-gabon.ga",
            password="testpass123"
        )
        self.tuteur = Tuteur.objects.create(
            utilisateur=self.tuteur_user,
            niveau="MASTER",
            departement=self.departement
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )
        self.seance = SeanceTutorat.objects.create(
            tuteur=self.tuteur,
            cours=self.cours,
            type_seance="INDIVIDUEL",
            modalite="PRESENTIEL",
            date_debut=timezone.now() + timedelta(days=1),
            date_fin=timezone.now() + timedelta(days=1, hours=2),
            lieu="Salle 101",
            capacite_max=5,
            tarif_horaire=5000
        )
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.inscription = Inscription.objects.create(
            seance=self.seance,
            etudiant=self.etudiant
        )

    def test_creation_inscription(self):
        """Test de création d'une inscription"""
        self.assertEqual(self.inscription.seance, self.seance)
        self.assertEqual(self.inscription.etudiant, self.etudiant)
        self.assertEqual(self.inscription.statut, "EN_ATTENTE")
        self.assertFalse(self.inscription.presence_confirmee)

class EvaluationTests(TestCase):
    def setUp(self):
        self.departement = Departement.objects.create(
            nom="Informatique",
            code="INFO"
        )
        self.tuteur_user = User.objects.create_user(
            username="tuteur@univ-gabon.ga",
            password="testpass123"
        )
        self.tuteur = Tuteur.objects.create(
            utilisateur=self.tuteur_user,
            niveau="MASTER",
            departement=self.departement
        )
        self.cours = Cours.objects.create(
            intitule="Python",
            code="INF101",
            departement=self.departement,
            credits=6
        )
        self.seance = SeanceTutorat.objects.create(
            tuteur=self.tuteur,
            cours=self.cours,
            type_seance="INDIVIDUEL",
            modalite="PRESENTIEL",
            date_debut=timezone.now() - timedelta(days=1),
            date_fin=timezone.now() - timedelta(hours=2),
            lieu="Salle 101",
            capacite_max=5,
            tarif_horaire=5000,
            statut="TERMINEE"
        )
        self.etudiant = User.objects.create_user(
            username="etudiant@univ-gabon.ga",
            password="testpass123"
        )
        self.inscription = Inscription.objects.create(
            seance=self.seance,
            etudiant=self.etudiant,
            statut="CONFIRMEE",
            presence_confirmee=True
        )
        self.evaluation = Evaluation.objects.create(
            seance=self.seance,
            etudiant=self.etudiant,
            note=5,
            commentaire="Excellent cours"
        )

    def test_creation_evaluation(self):
        """Test de création d'une évaluation"""
        self.assertEqual(self.evaluation.seance, self.seance)
        self.assertEqual(self.evaluation.etudiant, self.etudiant)
        self.assertEqual(self.evaluation.note, 5)
        self.assertEqual(self.evaluation.commentaire, "Excellent cours")
