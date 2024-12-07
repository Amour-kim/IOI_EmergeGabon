from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Ressource, Evaluation, Telechargement

@receiver(post_save, sender=Evaluation)
def update_ressource_stats_on_evaluation(sender, instance, created, **kwargs):
    """Met à jour les statistiques de la ressource après une évaluation"""
    if created:
        cache.delete(f'ressource_stats_{instance.ressource.id}')
        instance.ressource.save()  # Déclenche la mise à jour des stats

@receiver(post_delete, sender=Evaluation)
def update_ressource_stats_on_evaluation_delete(sender, instance, **kwargs):
    """Met à jour les statistiques de la ressource après suppression d'une évaluation"""
    cache.delete(f'ressource_stats_{instance.ressource.id}')
    instance.ressource.save()  # Déclenche la mise à jour des stats

@receiver(post_save, sender=Telechargement)
def update_ressource_downloads(sender, instance, created, **kwargs):
    """Met à jour le compteur de téléchargements"""
    if created:
        cache.delete(f'ressource_downloads_{instance.ressource.id}')

@receiver(post_save, sender=Ressource)
def clear_ressource_cache(sender, instance, **kwargs):
    """Nettoie le cache lié à la ressource"""
    cache.delete(f'ressource_detail_{instance.id}')
    cache.delete(f'ressource_stats_{instance.id}')
    cache.delete(f'ressource_downloads_{instance.id}')
