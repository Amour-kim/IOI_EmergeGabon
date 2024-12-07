from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from .models import DossierInscription, Document, Certificat
from .utils import verifier_documents_requis

@receiver(post_save, sender=Document)
def document_post_save(sender, instance, created, **kwargs):
    """Signal post-save pour le modèle Document"""
    # Invalide le cache des statistiques du dossier
    cache.delete(f'dossier_stats_{instance.dossier.id}')
    
    # Si le document est validé, vérifie si tous les documents sont complets
    if instance.valide:
        dossier = instance.dossier
        if (dossier.statut == 'INCOMPLET' and 
            verifier_documents_requis(dossier)):
            dossier.statut = 'EN_COURS'
            dossier.save()

@receiver(post_delete, sender=Document)
def document_post_delete(sender, instance, **kwargs):
    """Signal post-delete pour le modèle Document"""
    # Invalide le cache des statistiques du dossier
    cache.delete(f'dossier_stats_{instance.dossier.id}')
    
    # Si le document était validé, vérifie le statut du dossier
    if instance.valide:
        dossier = instance.dossier
        if not verifier_documents_requis(dossier):
            dossier.statut = 'INCOMPLET'
            dossier.save()

@receiver(post_save, sender=DossierInscription)
def dossier_post_save(sender, instance, created, **kwargs):
    """Signal post-save pour le modèle DossierInscription"""
    # Invalide les caches de statistiques
    cache.delete(f'dossier_stats_{instance.id}')
    cache.delete(f'stats_inscriptions_{instance.annee_academique}')
    cache.delete('stats_inscriptions_global')
    
    # Met à jour la date de validation si le statut est validé
    if instance.statut == 'VALIDE' and not instance.date_validation:
        instance.date_validation = timezone.now()
        instance.save()

@receiver(post_delete, sender=DossierInscription)
def dossier_post_delete(sender, instance, **kwargs):
    """Signal post-delete pour le modèle DossierInscription"""
    # Invalide les caches de statistiques
    cache.delete(f'stats_inscriptions_{instance.annee_academique}')
    cache.delete('stats_inscriptions_global')

@receiver(post_save, sender=Certificat)
def certificat_post_save(sender, instance, created, **kwargs):
    """Signal post-save pour le modèle Certificat"""
    # Invalide le cache des statistiques du dossier
    cache.delete(f'dossier_stats_{instance.dossier.id}')
