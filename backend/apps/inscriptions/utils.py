import os
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Q
from datetime import timedelta

def generer_numero_certificat(type_certificat, annee_academique):
    """
    Génère un numéro unique pour un certificat
    
    Args:
        type_certificat: Type du certificat (SCOLARITE, INSCRIPTION, CARTE)
        annee_academique: Année académique (format: 2023-2024)
    """
    prefix = {
        'SCOLARITE': 'CS',
        'INSCRIPTION': 'AI',
        'CARTE': 'CE'
    }.get(type_certificat, 'XX')
    
    annee = annee_academique.split('-')[0]
    cache_key = f'certificat_counter_{type_certificat}_{annee}'
    
    counter = cache.get(cache_key, 0) + 1
    cache.set(cache_key, counter)
    
    return f"{prefix}-{annee}-{counter:04d}"

def get_dossier_stats(dossier):
    """
    Calcule les statistiques d'un dossier d'inscription
    
    Args:
        dossier: Instance du modèle DossierInscription
    """
    cache_key = f'dossier_stats_{dossier.id}'
    stats = cache.get(cache_key)
    
    if not stats:
        documents = dossier.documents.all()
        stats = {
            'documents': {
                'total': documents.count(),
                'valides': documents.filter(valide=True).count(),
                'en_attente': documents.filter(valide=False).count(),
                'par_type': documents.values(
                    'type_document'
                ).annotate(total=Count('id'))
            },
            'certificats': {
                'total': dossier.certificats.count(),
                'par_type': dossier.certificats.values(
                    'type_certificat'
                ).annotate(total=Count('id'))
            },
            'timeline': {
                'soumission': dossier.date_soumission,
                'derniere_modification': dossier.updated_at,
                'validation': dossier.date_validation
            }
        }
        
        # Cache pour 1 heure
        cache.set(cache_key, stats, timeout=3600)
    
    return stats

def verifier_documents_requis(dossier):
    """
    Vérifie si tous les documents requis sont présents et validés
    
    Args:
        dossier: Instance du modèle DossierInscription
    """
    documents_requis = {
        'IDENTITE': False,
        'DIPLOME': False,
        'RELEVE': False,
        'MEDICAL': False,
        'PHOTO': False
    }
    
    for doc in dossier.documents.filter(valide=True):
        if doc.type_document in documents_requis:
            documents_requis[doc.type_document] = True
    
    return all(documents_requis.values())

def get_statistiques_inscriptions(annee_academique=None):
    """
    Calcule les statistiques globales des inscriptions
    
    Args:
        annee_academique: Année académique optionnelle (format: 2023-2024)
    """
    if annee_academique:
        cache_key = f'stats_inscriptions_{annee_academique}'
    else:
        cache_key = 'stats_inscriptions_global'
    
    stats = cache.get(cache_key)
    
    if not stats:
        from .models import DossierInscription
        
        queryset = DossierInscription.objects.all()
        if annee_academique:
            queryset = queryset.filter(annee_academique=annee_academique)
        
        stats = {
            'total': queryset.count(),
            'par_statut': queryset.values(
                'statut'
            ).annotate(total=Count('id')),
            'par_niveau': queryset.values(
                'niveau_etude'
            ).annotate(total=Count('id')),
            'par_departement': queryset.values(
                'departement__nom'
            ).annotate(total=Count('id')),
            'evolution': {
                'derniere_semaine': queryset.filter(
                    date_soumission__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'dernier_mois': queryset.filter(
                    date_soumission__gte=timezone.now() - timedelta(days=30)
                ).count()
            }
        }
        
        # Cache pour 1 heure
        cache.set(cache_key, stats, timeout=3600)
    
    return stats

def nettoyer_fichiers_obsoletes():
    """
    Nettoie les fichiers obsolètes du système de fichiers
    """
    from .models import Document, Certificat
    
    # Liste tous les fichiers dans les dossiers de stockage
    document_files = set()
    certificat_files = set()
    
    for doc in Document.objects.all():
        if doc.fichier:
            document_files.add(doc.fichier.path)
    
    for cert in Certificat.objects.all():
        if cert.fichier:
            certificat_files.add(cert.fichier.path)
    
    # Vérifie les dossiers de stockage
    for directory in ['documents_inscription', 'certificats']:
        storage_path = os.path.join('media', directory)
        if os.path.exists(storage_path):
            for root, _, files in os.walk(storage_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if (directory == 'documents_inscription' and 
                        file_path not in document_files):
                        os.remove(file_path)
                    elif (directory == 'certificats' and 
                          file_path not in certificat_files):
                        os.remove(file_path)
