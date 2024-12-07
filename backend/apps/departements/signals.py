from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Faculte, Departement, Programme, Cours

@receiver(post_save, sender=Faculte)
@receiver(post_delete, sender=Faculte)
def clear_faculte_cache(sender, instance, **kwargs):
    """Nettoie le cache lié à la faculté"""
    cache.delete(f'faculte_detail_{instance.id}')
    cache.delete('facultes_list')

@receiver(post_save, sender=Departement)
@receiver(post_delete, sender=Departement)
def clear_departement_cache(sender, instance, **kwargs):
    """Nettoie le cache lié au département"""
    cache.delete(f'departement_detail_{instance.id}')
    cache.delete('departements_list')
    cache.delete(f'faculte_departements_{instance.faculte_id}')

@receiver(post_save, sender=Programme)
@receiver(post_delete, sender=Programme)
def clear_programme_cache(sender, instance, **kwargs):
    """Nettoie le cache lié au programme"""
    cache.delete(f'programme_detail_{instance.id}')
    cache.delete('programmes_list')
    cache.delete(f'departement_programmes_{instance.departement_id}')

@receiver(post_save, sender=Cours)
@receiver(post_delete, sender=Cours)
def clear_cours_cache(sender, instance, **kwargs):
    """Nettoie le cache lié au cours"""
    cache.delete(f'cours_detail_{instance.id}')
    cache.delete('cours_list')
    cache.delete(f'departement_cours_{instance.departement_id}')
