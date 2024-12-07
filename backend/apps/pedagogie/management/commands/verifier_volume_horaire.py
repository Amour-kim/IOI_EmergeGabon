from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, Count, F
from apps.pedagogie.models import ECUE, Seance

class Command(BaseCommand):
    help = 'Vérifie et rapporte le volume horaire des ECUEs'

    def add_arguments(self, parser):
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
        parser.add_argument(
            '--format',
            type=str,
            choices=['text', 'csv'],
            default='text',
            help='Format de sortie'
        )

    def handle(self, *args, **options):
        # Filtrage des ECUEs
        ecues = ECUE.objects.all()
        if options['filiere']:
            ecues = ecues.filter(ue__filiere__code=options['filiere'])
        if options['semestre']:
            ecues = ecues.filter(ue__semestre=options['semestre'])

        # Récupération des statistiques
        stats = []
        for ecue in ecues:
            # Volume horaire prévu
            volume_cm = ecue.volume_horaire_cm
            volume_td = ecue.volume_horaire_td
            volume_tp = ecue.volume_horaire_tp
            volume_total = ecue.volume_horaire_total

            # Volume horaire réalisé
            seances = Seance.objects.filter(ecue=ecue)
            volume_realise = {
                'CM': seances.filter(
                    type_seance='CM',
                    statut='TERMINE'
                ).count() * 2,
                'TD': seances.filter(
                    type_seance='TD',
                    statut='TERMINE'
                ).count() * 2,
                'TP': seances.filter(
                    type_seance='TP',
                    statut='TERMINE'
                ).count() * 2
            }
            volume_realise_total = sum(volume_realise.values())

            # Volume horaire planifié
            volume_planifie = {
                'CM': seances.filter(
                    type_seance='CM',
                    statut__in=['PLANIFIE', 'EN_COURS']
                ).count() * 2,
                'TD': seances.filter(
                    type_seance='TD',
                    statut__in=['PLANIFIE', 'EN_COURS']
                ).count() * 2,
                'TP': seances.filter(
                    type_seance='TP',
                    statut__in=['PLANIFIE', 'EN_COURS']
                ).count() * 2
            }
            volume_planifie_total = sum(volume_planifie.values())

            # Calcul des pourcentages
            if volume_total > 0:
                progression = (volume_realise_total / volume_total) * 100
                planification = (
                    (volume_realise_total + volume_planifie_total) / volume_total
                ) * 100
            else:
                progression = 0
                planification = 0

            stats.append({
                'code': ecue.code,
                'intitule': ecue.intitule,
                'ue': ecue.ue.code,
                'filiere': ecue.ue.filiere.code,
                'semestre': ecue.ue.semestre,
                'enseignant': ecue.enseignant.get_full_name(),
                'volume_prevu': {
                    'CM': volume_cm,
                    'TD': volume_td,
                    'TP': volume_tp,
                    'total': volume_total
                },
                'volume_realise': volume_realise,
                'volume_planifie': volume_planifie,
                'progression': progression,
                'planification': planification
            })

        # Affichage des résultats
        if options['format'] == 'csv':
            self.afficher_csv(stats)
        else:
            self.afficher_text(stats)

    def afficher_text(self, stats):
        """Affiche les statistiques en format texte"""
        self.stdout.write('\nRapport de volume horaire des ECUEs\n')
        self.stdout.write('=' * 80 + '\n')

        for stat in stats:
            self.stdout.write(f"\nECUE: {stat['code']} - {stat['intitule']}")
            self.stdout.write(f"UE: {stat['ue']}")
            self.stdout.write(
                f"Filière: {stat['filiere']} - Semestre {stat['semestre']}"
            )
            self.stdout.write(f"Enseignant: {stat['enseignant']}")
            self.stdout.write('-' * 40)
            
            # Volume prévu
            self.stdout.write('\nVolume prévu:')
            self.stdout.write(f"  CM: {stat['volume_prevu']['CM']}h")
            self.stdout.write(f"  TD: {stat['volume_prevu']['TD']}h")
            self.stdout.write(f"  TP: {stat['volume_prevu']['TP']}h")
            self.stdout.write(
                f"  Total: {stat['volume_prevu']['total']}h"
            )
            
            # Volume réalisé
            self.stdout.write('\nVolume réalisé:')
            self.stdout.write(f"  CM: {stat['volume_realise']['CM']}h")
            self.stdout.write(f"  TD: {stat['volume_realise']['TD']}h")
            self.stdout.write(f"  TP: {stat['volume_realise']['TP']}h")
            self.stdout.write(
                f"  Total: {sum(stat['volume_realise'].values())}h"
            )
            
            # Volume planifié
            self.stdout.write('\nVolume planifié:')
            self.stdout.write(f"  CM: {stat['volume_planifie']['CM']}h")
            self.stdout.write(f"  TD: {stat['volume_planifie']['TD']}h")
            self.stdout.write(f"  TP: {stat['volume_planifie']['TP']}h")
            self.stdout.write(
                f"  Total: {sum(stat['volume_planifie'].values())}h"
            )
            
            # Progression
            self.stdout.write(
                f"\nProgression: {stat['progression']:.1f}%"
            )
            self.stdout.write(
                f"Planification: {stat['planification']:.1f}%"
            )
            
            if stat['progression'] < 50:
                self.stdout.write(
                    self.style.WARNING(
                        '\n⚠️ Attention: Progression inférieure à 50%'
                    )
                )
            
            self.stdout.write('=' * 80 + '\n')

    def afficher_csv(self, stats):
        """Affiche les statistiques en format CSV"""
        import csv
        import sys

        writer = csv.writer(sys.stdout)
        
        # En-tête
        writer.writerow([
            'Code ECUE', 'Intitulé', 'UE', 'Filière', 'Semestre', 'Enseignant',
            'CM Prévu', 'TD Prévu', 'TP Prévu', 'Total Prévu',
            'CM Réalisé', 'TD Réalisé', 'TP Réalisé', 'Total Réalisé',
            'CM Planifié', 'TD Planifié', 'TP Planifié', 'Total Planifié',
            'Progression (%)', 'Planification (%)'
        ])
        
        # Données
        for stat in stats:
            writer.writerow([
                stat['code'],
                stat['intitule'],
                stat['ue'],
                stat['filiere'],
                stat['semestre'],
                stat['enseignant'],
                stat['volume_prevu']['CM'],
                stat['volume_prevu']['TD'],
                stat['volume_prevu']['TP'],
                stat['volume_prevu']['total'],
                stat['volume_realise']['CM'],
                stat['volume_realise']['TD'],
                stat['volume_realise']['TP'],
                sum(stat['volume_realise'].values()),
                stat['volume_planifie']['CM'],
                stat['volume_planifie']['TD'],
                stat['volume_planifie']['TP'],
                sum(stat['volume_planifie'].values()),
                f"{stat['progression']:.1f}",
                f"{stat['planification']:.1f}"
            ])
