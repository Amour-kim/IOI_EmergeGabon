from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import random
from apps.pedagogie.models import ECUE, Seance

User = get_user_model()

class Command(BaseCommand):
    help = 'Génère un planning de cours pour une période donnée'

    def add_arguments(self, parser):
        parser.add_argument(
            '--semaines',
            type=int,
            default=1,
            help='Nombre de semaines à générer'
        )
        parser.add_argument(
            '--date_debut',
            type=str,
            help='Date de début (format YYYY-MM-DD)'
        )
        parser.add_argument(
            '--filiere',
            type=str,
            help='Code de la filière'
        )
        parser.add_argument(
            '--semestre',
            type=int,
            help='Numéro du semestre'
        )

    def handle(self, *args, **options):
        # Configuration des paramètres
        nb_semaines = options['semaines']
        date_debut = options['date_debut']
        filiere_code = options['filiere']
        semestre = options['semestre']

        if date_debut:
            date_debut = timezone.datetime.strptime(
                date_debut,
                '%Y-%m-%d'
            ).date()
        else:
            date_debut = timezone.now().date()

        # Récupération des ECUEs
        ecues = ECUE.objects.filter(
            ue__filiere__code=filiere_code,
            ue__semestre=semestre
        ) if filiere_code and semestre else ECUE.objects.all()

        if not ecues.exists():
            self.stdout.write(
                self.style.ERROR('Aucun ECUE trouvé avec les critères spécifiés')
            )
            return

        # Configuration des créneaux horaires
        creneaux = [
            # Matin
            {'debut': '08:00', 'fin': '10:00'},
            {'debut': '10:15', 'fin': '12:15'},
            # Après-midi
            {'debut': '14:00', 'fin': '16:00'},
            {'debut': '16:15', 'fin': '18:15'},
        ]

        # Salles disponibles
        salles = [
            'A101', 'A102', 'A103',  # Amphis
            'B201', 'B202', 'B203',  # TD
            'C301', 'C302', 'C303',  # TP
        ]

        # Génération des séances
        seances_creees = 0
        date_courante = date_debut

        for _ in range(nb_semaines):
            for jour in range(5):  # Lundi à Vendredi
                date = date_courante + timedelta(days=jour)
                
                # Éviter les jours fériés (à implémenter)
                if self.est_jour_ferie(date):
                    continue

                salles_utilisees = set()
                for creneau in creneaux:
                    for ecue in ecues:
                        # Vérifier le volume horaire restant
                        if not self.volume_horaire_disponible(ecue):
                            continue

                        # Éviter les conflits d'emploi du temps
                        if self.a_conflit(ecue, date, creneau):
                            continue

                        # Sélection aléatoire d'une salle disponible
                        salles_dispo = [
                            s for s in salles 
                            if s not in salles_utilisees
                        ]
                        if not salles_dispo:
                            continue
                        
                        salle = random.choice(salles_dispo)
                        salles_utilisees.add(salle)

                        # Création de la séance
                        debut = timezone.datetime.combine(
                            date,
                            timezone.datetime.strptime(
                                creneau['debut'],
                                '%H:%M'
                            ).time()
                        )
                        fin = timezone.datetime.combine(
                            date,
                            timezone.datetime.strptime(
                                creneau['fin'],
                                '%H:%M'
                            ).time()
                        )

                        type_seance = self.determiner_type_seance(ecue, salle)
                        
                        Seance.objects.create(
                            ecue=ecue,
                            type_seance=type_seance,
                            date_debut=debut,
                            date_fin=fin,
                            salle=salle,
                            enseignant=ecue.enseignant,
                            description=f'Séance de {type_seance} - {ecue.intitule}'
                        )
                        seances_creees += 1

            date_courante += timedelta(days=7)

        self.stdout.write(
            self.style.SUCCESS(
                f'{seances_creees} séances ont été générées avec succès'
            )
        )

    def est_jour_ferie(self, date):
        """Vérifie si une date est un jour férié"""
        # À implémenter selon le calendrier gabonais
        return False

    def volume_horaire_disponible(self, ecue):
        """Vérifie s'il reste du volume horaire pour l'ECUE"""
        volume_total = ecue.volume_horaire_total
        volume_planifie = Seance.objects.filter(
            ecue=ecue,
            statut__in=['PLANIFIE', 'EN_COURS', 'TERMINE']
        ).count() * 2  # 2 heures par séance

        return volume_planifie < volume_total

    def a_conflit(self, ecue, date, creneau):
        """Vérifie s'il y a des conflits d'emploi du temps"""
        debut = timezone.datetime.combine(
            date,
            timezone.datetime.strptime(creneau['debut'], '%H:%M').time()
        )
        fin = timezone.datetime.combine(
            date,
            timezone.datetime.strptime(creneau['fin'], '%H:%M').time()
        )

        # Vérifier les conflits pour l'enseignant
        conflit_enseignant = Seance.objects.filter(
            enseignant=ecue.enseignant,
            date_debut__lt=fin,
            date_fin__gt=debut
        ).exists()

        # Vérifier les conflits pour la filière
        conflit_filiere = Seance.objects.filter(
            ecue__ue__filiere=ecue.ue.filiere,
            date_debut__lt=fin,
            date_fin__gt=debut
        ).exists()

        return conflit_enseignant or conflit_filiere

    def determiner_type_seance(self, ecue, salle):
        """Détermine le type de séance en fonction de la salle et des volumes horaires"""
        if salle.startswith('A'):  # Amphi
            return 'CM'
        elif salle.startswith('B'):  # Salle de TD
            return 'TD'
        else:  # Salle de TP
            return 'TP'
