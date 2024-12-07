from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from .models import Tuteur, SeanceTutorat, Inscription, Evaluation

@receiver([post_save, post_delete], sender=Tuteur)
def clear_tuteur_cache(sender, instance, **kwargs):
    """Nettoie le cache lié aux tuteurs"""
    cache.delete(f'tuteur_{instance.id}')
    cache.delete('tuteurs_list')
    cache.delete(f'tuteurs_dept_{instance.departement_id}')

@receiver(post_save, sender=SeanceTutorat)
def handle_seance_save(sender, instance, created, **kwargs):
    """Gère la sauvegarde des séances"""
    # Nettoie le cache
    cache.delete(f'seance_{instance.id}')
    cache.delete(f'seances_tuteur_{instance.tuteur_id}')
    
    # Met à jour le statut automatiquement
    now = timezone.now()
    if instance.date_debut <= now <= instance.date_fin:
        if instance.statut != 'EN_COURS':
            instance.statut = 'EN_COURS'
            instance.save(update_fields=['statut'])
    elif now > instance.date_fin:
        if instance.statut != 'TERMINEE':
            instance.statut = 'TERMINEE'
            instance.save(update_fields=['statut'])

@receiver(post_save, sender=Inscription)
def handle_inscription_save(sender, instance, created, **kwargs):
    """Gère la sauvegarde des inscriptions"""
    if created and instance.statut == 'CONFIRMEE':
        # Vérifie la capacité
        seance = instance.seance
        inscriptions_confirmees = seance.inscriptions.filter(
            statut='CONFIRMEE'
        ).count()
        
        if inscriptions_confirmees > seance.capacite_max:
            instance.statut = 'EN_ATTENTE'
            instance.save(update_fields=['statut'])
    
    # Nettoie le cache
    cache.delete(f'inscription_{instance.id}')
    cache.delete(f'inscriptions_seance_{instance.seance_id}')
    cache.delete(f'inscriptions_etudiant_{instance.etudiant_id}')

@receiver(post_save, sender=Evaluation)
def handle_evaluation_save(sender, instance, created, **kwargs):
    """Gère la sauvegarde des évaluations"""
    if created:
        # Met à jour la note moyenne du tuteur
        tuteur = instance.seance.tuteur
        tuteur.mettre_a_jour_note(instance.note)
    
    # Nettoie le cache
    cache.delete(f'evaluation_{instance.id}')
    cache.delete(f'evaluations_seance_{instance.seance_id}')
    cache.delete(f'evaluations_etudiant_{instance.etudiant_id}')
