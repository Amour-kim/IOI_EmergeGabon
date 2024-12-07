from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings
import weasyprint
from apps.inscriptions.models import DossierInscription, Certificat
from apps.inscriptions.utils import generer_qr_code
import os

class Command(BaseCommand):
    help = 'Génère les cartes étudiantes pour les dossiers validés'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la régénération des cartes existantes'
        )
        parser.add_argument(
            '--dossier',
            type=int,
            help='ID du dossier spécifique'
        )

    def handle(self, *args, **options):
        # Filtrage des dossiers
        dossiers = DossierInscription.objects.filter(statut='VALIDE')
        if options['dossier']:
            dossiers = dossiers.filter(id=options['dossier'])
        
        total = dossiers.count()
        self.stdout.write(
            self.style.SUCCESS(f'Génération des cartes pour {total} dossiers...')
        )
        
        processed = 0
        errors = 0
        
        for dossier in dossiers:
            try:
                # Vérification si la carte existe déjà
                carte_existante = dossier.certificats.filter(
                    type_certificat='CARTE'
                ).first()
                
                if carte_existante and not options['force']:
                    self.stdout.write(
                        f'Carte déjà existante pour le dossier {dossier.id}'
                    )
                    continue
                
                # Génération du QR code
                qr_code = generer_qr_code(
                    f"{settings.SITE_URL}/verifier-carte/{dossier.etudiant.matricule}"
                )
                
                # Contexte pour le template
                context = {
                    'etudiant': dossier.etudiant,
                    'dossier': dossier,
                    'universite': {
                        'nom': settings.NOM_UNIVERSITE,
                        'nom_court': settings.NOM_COURT_UNIVERSITE,
                        'logo_url': settings.LOGO_URL,
                    },
                    'qr_code_url': qr_code,
                    'annee_academique': dossier.annee_academique,
                }
                
                # Génération du HTML
                html = render_to_string(
                    'inscriptions/carte_etudiant.html',
                    context
                )
                
                # Génération du PDF
                pdf = weasyprint.HTML(string=html).write_pdf()
                
                # Sauvegarde du fichier
                filename = f'carte_{dossier.etudiant.matricule}.pdf'
                filepath = os.path.join('certificats', filename)
                
                # Création ou mise à jour du certificat
                if carte_existante:
                    carte = carte_existante
                else:
                    carte = Certificat(
                        dossier=dossier,
                        type_certificat='CARTE'
                    )
                
                carte.numero = f"CARTE-{dossier.etudiant.matricule}"
                carte.valide_jusqu_au = timezone.now().date().replace(
                    month=9, day=30
                )
                if timezone.now().month >= 9:
                    carte.valide_jusqu_au = carte.valide_jusqu_au.replace(
                        year=carte.valide_jusqu_au.year + 1
                    )
                
                # Sauvegarde du fichier dans le storage
                with open(filepath, 'wb') as f:
                    f.write(pdf)
                carte.fichier.name = filepath
                carte.save()
                
                processed += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Carte générée pour {dossier.etudiant.get_full_name()}'
                    )
                )
                
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Erreur pour le dossier {dossier.id}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nTraitement terminé:\n'
                f'- Cartes générées: {processed}/{total}\n'
                f'- Erreurs: {errors}'
            )
        )
