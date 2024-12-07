from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from ..models import (
    Departement, Cycle, Filiere, UE, ECUE,
    Programme, Seance
)

User = get_user_model()

class APITestCase(APITestCase):
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
        self.etudiant = User.objects.create_user(
            email='etudiant@example.com',
            password='etudiant123'
        )
        
        # Création des objets de base
        self.departement = Departement.objects.create(
            nom='Informatique',
            code='INFO',
            responsable=self.admin
        )
        
        self.cycle = Cycle.objects.create(
            nom='Licence',
            niveau='LICENCE',
            duree=6
        )
        
        self.filiere = Filiere.objects.create(
            nom='Génie Logiciel',
            code='GL',
            departement=self.departement,
            cycle=self.cycle,
            responsable=self.admin
        )
        
        self.ue = UE.objects.create(
            code='INF301',
            intitule='POO',
            credits=6,
            filiere=self.filiere,
            semestre=3,
            responsable=self.enseignant
        )
        
        self.ecue = ECUE.objects.create(
            code='INF301-1',
            intitule='Java',
            credits=3,
            ue=self.ue,
            enseignant=self.enseignant
        )

    def test_departement_list(self):
        """Test de la liste des départements"""
        url = reverse('pedagogie:departement-list')
        
        # Sans authentification
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # En tant qu'étudiant
        self.client.force_authenticate(user=self.etudiant)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # En tant qu'admin
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, {
            'nom': 'Mathématiques',
            'code': 'MATH',
            'responsable': self.admin.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filiere_maquette(self):
        """Test de la maquette d'une filière"""
        url = reverse('pedagogie:filiere-maquette', args=[self.filiere.id])
        
        self.client.force_authenticate(user=self.enseignant)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['filiere']['code'], 'GL')
        self.assertEqual(len(response.data['ues']), 1)

    def test_ecue_progression(self):
        """Test de la progression d'un ECUE"""
        url = reverse('pedagogie:ecue-progression', args=[self.ecue.id])
        
        # Création de séances
        now = timezone.now()
        Seance.objects.create(
            ecue=self.ecue,
            type_seance='CM',
            date_debut=now - timedelta(days=1),
            date_fin=now - timedelta(days=1) + timedelta(hours=3),
            salle='A101',
            enseignant=self.enseignant,
            statut='TERMINE'
        )
        
        self.client.force_authenticate(user=self.enseignant)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['volume_realise'], 3)

    def test_seance_lifecycle(self):
        """Test du cycle de vie d'une séance"""
        # Création d'une séance
        now = timezone.now()
        seance = Seance.objects.create(
            ecue=self.ecue,
            type_seance='CM',
            date_debut=now,
            date_fin=now + timedelta(hours=3),
            salle='A101',
            enseignant=self.enseignant
        )
        
        self.client.force_authenticate(user=self.enseignant)
        
        # Commencer la séance
        url = reverse('pedagogie:seance-commencer', args=[seance.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], 'EN_COURS')
        
        # Terminer la séance
        url = reverse('pedagogie:seance-terminer', args=[seance.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], 'TERMINE')
        
        # Essayer d'annuler une séance terminée
        url = reverse('pedagogie:seance-annuler', args=[seance.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_planning(self):
        """Test du planning des séances"""
        now = timezone.now()
        
        # Création de plusieurs séances
        Seance.objects.create(
            ecue=self.ecue,
            type_seance='CM',
            date_debut=now + timedelta(days=1),
            date_fin=now + timedelta(days=1, hours=3),
            salle='A101',
            enseignant=self.enseignant
        )
        Seance.objects.create(
            ecue=self.ecue,
            type_seance='TD',
            date_debut=now + timedelta(days=2),
            date_fin=now + timedelta(days=2, hours=2),
            salle='B202',
            enseignant=self.enseignant
        )
        
        self.client.force_authenticate(user=self.enseignant)
        url = reverse('pedagogie:seance-planning')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Test avec filtres
        response = self.client.get(
            f"{url}?date_debut={now.date()}&date_fin={now.date()}"
        )
        self.assertEqual(len(response.data), 0)

    def test_permissions(self):
        """Test des permissions"""
        # Test création d'UE
        url = reverse('pedagogie:ue-list')
        
        self.client.force_authenticate(user=self.etudiant)
        response = self.client.post(url, {
            'code': 'INF302',
            'intitule': 'Test',
            'credits': 6,
            'filiere': self.filiere.id,
            'semestre': 3
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test modification d'ECUE
        url = reverse('pedagogie:ecue-detail', args=[self.ecue.id])
        
        self.client.force_authenticate(user=self.enseignant)
        response = self.client.patch(url, {
            'intitule': 'Java Avancé'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test suppression de département
        url = reverse('pedagogie:departement-detail', args=[self.departement.id])
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
