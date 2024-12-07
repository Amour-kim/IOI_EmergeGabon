from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models import (
    Departement, Cycle, Filiere, UE, ECUE,
    Programme, Seance
)

User = get_user_model()

class ModelsTestCase(TestCase):
    def setUp(self):
        # Création des utilisateurs
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        self.enseignant = User.objects.create_user(
            email='prof@example.com',
            password='prof123',
            first_name='Jean',
            last_name='Dupont'
        )
        
        # Création des objets de base
        self.departement = Departement.objects.create(
            nom='Informatique',
            code='INFO',
            description='Département Informatique',
            responsable=self.admin
        )
        
        self.cycle = Cycle.objects.create(
            nom='Licence Informatique',
            niveau='LICENCE',
            duree=6,
            description='Cycle Licence'
        )
        
        self.filiere = Filiere.objects.create(
            nom='Génie Logiciel',
            code='GL',
            description='Filière Génie Logiciel',
            departement=self.departement,
            cycle=self.cycle,
            responsable=self.admin
        )
        
        self.ue = UE.objects.create(
            code='INF301',
            intitule='Programmation Orientée Objet',
            credits=6,
            volume_horaire_cm=24,
            volume_horaire_td=24,
            volume_horaire_tp=12,
            filiere=self.filiere,
            semestre=3,
            responsable=self.enseignant
        )
        
        self.ecue = ECUE.objects.create(
            code='INF301-1',
            intitule='Java et POO',
            credits=3,
            coefficient=1.5,
            volume_horaire_cm=12,
            volume_horaire_td=12,
            volume_horaire_tp=6,
            ue=self.ue,
            enseignant=self.enseignant
        )

    def test_departement(self):
        self.assertEqual(str(self.departement), 'INFO - Informatique')
        self.assertEqual(self.departement.responsable, self.admin)
        self.assertTrue(self.departement.filieres.exists())

    def test_cycle(self):
        self.assertEqual(str(self.cycle), 'LICENCE - Licence Informatique')
        self.assertEqual(self.cycle.duree, 6)
        self.assertTrue(self.cycle.filieres.exists())

    def test_filiere(self):
        self.assertEqual(str(self.filiere), 'GL - Génie Logiciel')
        self.assertEqual(self.filiere.departement, self.departement)
        self.assertEqual(self.filiere.cycle, self.cycle)
        self.assertEqual(self.filiere.responsable, self.admin)

    def test_ue(self):
        self.assertEqual(str(self.ue), 'INF301 - Programmation Orientée Objet')
        self.assertEqual(self.ue.credits, 6)
        self.assertEqual(self.ue.volume_horaire_total, 60)
        self.assertEqual(self.ue.filiere, self.filiere)
        self.assertEqual(self.ue.responsable, self.enseignant)

    def test_ecue(self):
        self.assertEqual(str(self.ecue), 'INF301-1 - Java et POO')
        self.assertEqual(self.ecue.credits, 3)
        self.assertEqual(self.ecue.coefficient, 1.5)
        self.assertEqual(self.ecue.volume_horaire_total, 30)
        self.assertEqual(self.ecue.ue, self.ue)
        self.assertEqual(self.ecue.enseignant, self.enseignant)

    def test_programme(self):
        programme = Programme.objects.create(
            ecue=self.ecue,
            titre='Introduction à Java',
            description='Bases de Java',
            objectifs='Maîtriser les bases de Java',
            prerequis='Aucun',
            contenu='1. Variables\n2. Classes\n3. Objets',
            bibliographie='Livre Java',
            methode_evaluation='Contrôle continu et examen'
        )
        
        self.assertEqual(
            str(programme),
            'INF301-1 - Introduction à Java'
        )
        self.assertEqual(programme.ecue, self.ecue)

    def test_seance(self):
        now = timezone.now()
        seance = Seance.objects.create(
            ecue=self.ecue,
            type_seance='CM',
            date_debut=now,
            date_fin=now + timedelta(hours=3),
            salle='A101',
            enseignant=self.enseignant,
            description='Première séance'
        )
        
        self.assertEqual(
            str(seance),
            f'INF301-1 - Cours Magistral du {now.strftime("%Y-%m-%d %H:%M")}'
        )
        self.assertEqual(seance.duree, timedelta(hours=3))
        self.assertEqual(seance.statut, 'PLANIFIE')
        self.assertEqual(seance.enseignant, self.enseignant)
