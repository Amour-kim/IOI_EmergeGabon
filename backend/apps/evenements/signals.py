from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import Evenement, Inscription, Document, Feedback

@receiver([post_save, post_delete], sender=Evenement)
def clear_evenement_cache(sender, instance, **kwargs):
    """Nettoie le cache lié aux événements"""
    cache.delete(f'evenement_{instance.id}')
    cache.delete('evenements_list')
    cache.delete(f'evenements_dept_{instance.departement_id}')

@receiver(post_save, sender=Inscription)
def update_places_disponibles(sender, instance, created, **kwargs):
    """Met à jour le nombre de places disponibles"""
    if created and instance.statut == 'CONFIRMEE':
        evenement = instance.evenement
        evenement.places_disponibles = max(0, evenement.places_disponibles - 1)
        evenement.save(update_fields=['places_disponibles'])

@receiver([post_save, post_delete], sender=Document)
def clear_document_cache(sender, instance, **kwargs):
    """Nettoie le cache lié aux documents"""
    cache.delete(f'document_{instance.id}')
    cache.delete(f'documents_evenement_{instance.evenement_id}')

@receiver([post_save, post_delete], sender=Feedback)
def update_evenement_stats(sender, instance, **kwargs):
    """Met à jour les statistiques de l'événement"""
    evenement = instance.evenement
    feedbacks = evenement.feedbacks.all()
    
    # Calcul de la note moyenne
    notes = [f.note for f in feedbacks]
    if notes:
        moyenne = sum(notes) / len(notes)
        cache.set(
            f'evenement_{evenement.id}_note_moyenne',
            moyenne,
            timeout=settings.CACHE_TIMEOUT
        )
    
    # Mise à jour du cache des feedbacks
    cache.delete(f'feedbacks_evenement_{evenement.id}')
