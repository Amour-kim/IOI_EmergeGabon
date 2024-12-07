from django.core.management.base import BaseCommand
from apps.bibliotheque.utils.search.elastic import bulk_index_ressources

class Command(BaseCommand):
    help = 'Indexe toutes les ressources dans Elasticsearch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la réindexation complète'
        )

    def handle(self, *args, **options):
        force = options.get('force', False)

        self.stdout.write(
            self.style.SUCCESS('Début de l\'indexation des ressources...')
        )

        try:
            bulk_index_ressources()
            self.stdout.write(
                self.style.SUCCESS('Indexation terminée avec succès')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de l\'indexation: {e}')
            )
