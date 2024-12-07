from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from apps.bibliotheque.models import Ressource
from apps.bibliotheque.utils.metadata.extractor import MetadataExtractor

class Command(BaseCommand):
    help = 'Génère les miniatures pour les ressources sans miniature'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la régénération des miniatures existantes'
        )
        parser.add_argument(
            '--resource-id',
            type=int,
            help='ID de la ressource spécifique à traiter'
        )

    def handle(self, *args, **options):
        extractor = MetadataExtractor()
        force = options.get('force', False)
        resource_id = options.get('resource_id')

        # Filtrage des ressources
        resources = Ressource.objects.all()
        if resource_id:
            resources = resources.filter(id=resource_id)
        if not force:
            resources = resources.filter(miniature='')

        total = resources.count()
        processed = 0
        errors = 0

        self.stdout.write(
            self.style.SUCCESS(
                f'Génération des miniatures pour {total} ressources...'
            )
        )

        for resource in resources:
            try:
                # Vérification du fichier source
                if not default_storage.exists(resource.fichier.name):
                    self.stdout.write(
                        self.style.WARNING(
                            f'Fichier non trouvé pour la ressource {resource.id}'
                        )
                    )
                    errors += 1
                    continue

                # Extraction des métadonnées et génération de la miniature
                metadata = extractor.extract_metadata(
                    default_storage.path(resource.fichier.name)
                )

                if 'miniature' in metadata:
                    resource.miniature = metadata['miniature']
                    resource.save(update_fields=['miniature'])
                    processed += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Miniature générée pour la ressource {resource.id}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Impossible de générer la miniature pour la ressource {resource.id}'
                        )
                    )
                    errors += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Erreur lors du traitement de la ressource {resource.id}: {e}'
                    )
                )
                errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTraitement terminé:\n'
                f'- Ressources traitées: {processed}/{total}\n'
                f'- Erreurs: {errors}\n'
            )
        )
