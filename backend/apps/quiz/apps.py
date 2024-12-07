from django.apps import AppConfig

class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.quiz'
    verbose_name = 'Quiz'

    def ready(self):
        try:
            import apps.quiz.signals
        except ImportError:
            pass
