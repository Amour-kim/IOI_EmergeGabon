from django.db.models import Count, Avg, Q
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

def get_tuteur_stats(tuteur):
    """
    Calcule les statistiques d'un tuteur
    
    Args:
        tuteur: Instance du modèle Tuteur
    """
    cache_key = f'tuteur_stats_{tuteur.id}'
    stats = cache.get(cache_key)
    
    if not stats:
        seances = tuteur.seances.all()
        stats = {
            'nombre_seances': seances.count(),
            'nombre_etudiants': tuteur.seances.aggregate(
                total=Count('inscriptions__etudiant', distinct=True)
            )['total'] or 0,
            'seances_par_type': seances.values(
                'type_seance'
            ).annotate(total=Count('id')),
            'seances_par_modalite': seances.values(
                'modalite'
            ).annotate(total=Count('id')),
            'evaluations': {
                'moyenne': tuteur.note_moyenne,
                'nombre': tuteur.nombre_evaluations,
                'repartition': tuteur.seances.values(
                    'evaluations__note'
                ).annotate(total=Count('id'))
            }
        }
        
        # Cache pour 1 heure
        cache.set(cache_key, stats, timeout=3600)
    
    return stats

def get_seance_stats(seance):
    """
    Calcule les statistiques d'une séance
    
    Args:
        seance: Instance du modèle SeanceTutorat
    """
    cache_key = f'seance_stats_{seance.id}'
    stats = cache.get(cache_key)
    
    if not stats:
        stats = {
            'nombre_inscrits': seance.inscriptions.count(),
            'nombre_presents': seance.inscriptions.filter(
                presence_confirmee=True
            ).count(),
            'places_disponibles': max(
                0,
                seance.capacite_max - seance.inscriptions.filter(
                    statut='CONFIRMEE'
                ).count()
            ),
            'evaluations': {
                'moyenne': seance.evaluations.aggregate(
                    avg=Avg('note')
                )['avg'] or 0,
                'nombre': seance.evaluations.count(),
                'repartition': seance.evaluations.values(
                    'note'
                ).annotate(total=Count('id'))
            }
        }
        
        # Cache pour 1 heure
        cache.set(cache_key, stats, timeout=3600)
    
    return stats

def get_tuteurs_disponibles(cours, date_debut, date_fin):
    """
    Trouve les tuteurs disponibles pour un cours à une période donnée
    
    Args:
        cours: Instance du modèle Cours
        date_debut: Date et heure de début
        date_fin: Date et heure de fin
    """
    tuteurs = Tuteur.objects.filter(
        specialites=cours,
        statut='ACTIF'
    ).exclude(
        seances__date_debut__lt=date_fin,
        seances__date_fin__gt=date_debut,
        seances__statut__in=['PLANIFIEE', 'EN_COURS']
    )
    
    return tuteurs.distinct()

def get_prochaines_seances(etudiant):
    """
    Récupère les prochaines séances d'un étudiant
    
    Args:
        etudiant: Instance du modèle User (étudiant)
    """
    now = timezone.now()
    inscriptions = etudiant.inscriptions_tutorat.filter(
        Q(seance__date_debut__gt=now) |
        Q(seance__date_debut__lte=now, seance__date_fin__gt=now),
        statut='CONFIRMEE'
    ).select_related(
        'seance__tuteur__utilisateur',
        'seance__cours'
    )
    
    return [
        {
            'id': insc.seance.id,
            'cours': insc.seance.cours.intitule,
            'tuteur': insc.seance.tuteur.utilisateur.get_full_name(),
            'date_debut': insc.seance.date_debut,
            'date_fin': insc.seance.date_fin,
            'lieu': insc.seance.lieu,
            'modalite': insc.seance.get_modalite_display()
        }
        for insc in inscriptions
    ]

def get_historique_seances(etudiant):
    """
    Récupère l'historique des séances d'un étudiant
    
    Args:
        etudiant: Instance du modèle User (étudiant)
    """
    inscriptions = etudiant.inscriptions_tutorat.filter(
        seance__date_fin__lt=timezone.now(),
        presence_confirmee=True
    ).select_related(
        'seance__tuteur__utilisateur',
        'seance__cours'
    )
    
    return [
        {
            'id': insc.seance.id,
            'cours': insc.seance.cours.intitule,
            'tuteur': insc.seance.tuteur.utilisateur.get_full_name(),
            'date': insc.seance.date_debut.date(),
            'duree': (
                insc.seance.date_fin - insc.seance.date_debut
            ).total_seconds() / 3600,
            'evaluation': insc.seance.evaluations.filter(
                etudiant=etudiant
            ).exists()
        }
        for insc in inscriptions
    ]
