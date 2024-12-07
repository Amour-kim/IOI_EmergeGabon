from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from .models import Quiz, Question, Reponse, Tentative, ReponseEtudiant

@receiver(post_save, sender=Quiz)
def quiz_post_save(sender, instance, created, **kwargs):
    """Signal post-save pour le modèle Quiz"""
    # Invalide les caches liés au quiz
    cache.delete_pattern(f'quiz_stats_{instance.id}_*')
    cache.delete_pattern(f'quiz_questions_{instance.id}_*')

@receiver(post_delete, sender=Quiz)
def quiz_post_delete(sender, instance, **kwargs):
    """Signal post-delete pour le modèle Quiz"""
    # Invalide les caches liés au quiz
    cache.delete_pattern(f'quiz_stats_{instance.id}_*')
    cache.delete_pattern(f'quiz_questions_{instance.id}_*')

@receiver(post_save, sender=Question)
def question_post_save(sender, instance, created, **kwargs):
    """Signal post-save pour le modèle Question"""
    # Invalide les caches liés aux questions du quiz
    cache.delete(f'quiz_questions_{instance.quiz.id}_list')
    cache.delete(f'quiz_questions_{instance.quiz.id}_detail')

@receiver(post_delete, sender=Question)
def question_post_delete(sender, instance, **kwargs):
    """Signal post-delete pour le modèle Question"""
    # Invalide les caches liés aux questions du quiz
    cache.delete(f'quiz_questions_{instance.quiz.id}_list')
    cache.delete(f'quiz_questions_{instance.quiz.id}_detail')

@receiver(post_save, sender=Tentative)
def tentative_post_save(sender, instance, created, **kwargs):
    """Signal post-save pour le modèle Tentative"""
    # Invalide les caches liés aux statistiques du quiz
    cache.delete(f'quiz_stats_{instance.quiz.id}_global')
    
    # Met à jour la date de fin si le statut est terminé
    if instance.statut == 'TERMINEE' and not instance.date_fin:
        instance.date_fin = timezone.now()
        instance.save()

@receiver([post_save, post_delete], sender=ReponseEtudiant)
def reponse_etudiant_post_save_delete(sender, instance, **kwargs):
    """Signal post-save/delete pour le modèle ReponseEtudiant"""
    # Invalide les caches liés aux statistiques de la question
    cache.delete(
        f'question_stats_{instance.question.id}'
    )
    
    # Recalcule les points de la tentative
    if instance.tentative.statut == 'EN_COURS':
        total_points = sum(
            r.points_obtenus
            for r in instance.tentative.reponses_etudiant.all()
        )
        max_points = sum(
            q.points
            for q in instance.tentative.quiz.questions.all()
        )
        
        if max_points > 0:
            instance.tentative.note = (
                total_points / max_points
            ) * 100
            instance.tentative.save()
