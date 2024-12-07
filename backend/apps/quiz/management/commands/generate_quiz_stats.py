from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.quiz.models import Quiz, Tentative
from apps.quiz.utils import get_quiz_stats

class Command(BaseCommand):
    help = 'Génère les statistiques pour tous les quiz ou un quiz spécifique'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quiz-id',
            type=int,
            help='ID du quiz pour lequel générer les statistiques'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la régénération des statistiques même si elles existent déjà'
        )

    def handle(self, *args, **options):
        quiz_id = options.get('quiz_id')
        force = options.get('force', False)

        if quiz_id:
            try:
                quiz = Quiz.objects.get(id=quiz_id)
                stats = get_quiz_stats(quiz)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Statistiques générées pour le quiz "{quiz.titre}"'
                    )
                )
            except Quiz.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Quiz avec ID {quiz_id} non trouvé')
                )
        else:
            quiz_count = 0
            for quiz in Quiz.objects.filter(actif=True):
                if force or not quiz.derniere_maj_stats or (
                    timezone.now() - quiz.derniere_maj_stats
                ).days >= 1:
                    stats = get_quiz_stats(quiz)
                    quiz_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Statistiques générées pour {quiz_count} quiz'
                )
            )
