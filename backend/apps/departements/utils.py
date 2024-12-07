from django.db.models import Count, Avg
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

def get_departement_stats(departement):
    """
    Calcule les statistiques d'un département
    
    Args:
        departement: Instance du modèle Département
    """
    cache_key = f'departement_stats_{departement.id}'
    stats = cache.get(cache_key)
    
    if not stats:
        stats = {
            'nombre_programmes': departement.programmes.count(),
            'nombre_cours': departement.cours.count(),
            'nombre_enseignants': departement.personnel.filter(
                groups__name='Enseignants'
            ).count(),
            'nombre_etudiants': departement.etudiants.count(),
            'credits_total': departement.cours.aggregate(
                total=Sum('credits')
            )['total'] or 0,
            'cours_par_niveau': departement.cours.values(
                'niveau'
            ).annotate(total=Count('id')),
            'cours_par_semestre': departement.cours.values(
                'semestre'
            ).annotate(total=Count('id'))
        }
        
        # Cache pour 1 heure
        cache.set(cache_key, stats, timeout=3600)
    
    return stats

def get_programme_stats(programme):
    """
    Calcule les statistiques d'un programme
    
    Args:
        programme: Instance du modèle Programme
    """
    cache_key = f'programme_stats_{programme.id}'
    stats = cache.get(cache_key)
    
    if not stats:
        stats = {
            'nombre_cours': programme.cours.count(),
            'credits_total': programme.cours.aggregate(
                total=Sum('credits')
            )['total'] or 0,
            'nombre_etudiants': programme.etudiants.count(),
            'cours_par_semestre': programme.cours.values(
                'semestre'
            ).annotate(total=Count('id'))
        }
        
        # Cache pour 1 heure
        cache.set(cache_key, stats, timeout=3600)
    
    return stats

def get_cours_stats(cours):
    """
    Calcule les statistiques d'un cours
    
    Args:
        cours: Instance du modèle Cours
    """
    cache_key = f'cours_stats_{cours.id}'
    stats = cache.get(cache_key)
    
    if not stats:
        stats = {
            'nombre_inscrits': cours.etudiants.count(),
            'nombre_enseignants': cours.enseignants.count(),
            'moyenne_generale': cours.notes.aggregate(
                avg=Avg('valeur')
            )['avg'] or 0,
            'taux_reussite': calculate_taux_reussite(cours),
            'repartition_notes': cours.notes.values(
                'valeur'
            ).annotate(total=Count('id'))
        }
        
        # Cache pour 1 heure
        cache.set(cache_key, stats, timeout=3600)
    
    return stats

def calculate_taux_reussite(cours):
    """
    Calcule le taux de réussite pour un cours
    
    Args:
        cours: Instance du modèle Cours
    """
    total_notes = cours.notes.count()
    if total_notes == 0:
        return 0
        
    notes_reussite = cours.notes.filter(valeur__gte=10).count()
    return (notes_reussite / total_notes) * 100

def get_faculty_hierarchy(faculte):
    """
    Retourne la hiérarchie complète d'une faculté
    
    Args:
        faculte: Instance du modèle Faculté
    """
    return {
        'id': faculte.id,
        'nom': faculte.nom,
        'code': faculte.code,
        'departements': [
            {
                'id': dept.id,
                'nom': dept.nom,
                'code': dept.code,
                'programmes': [
                    {
                        'id': prog.id,
                        'nom': prog.nom,
                        'code': prog.code,
                        'niveau': prog.niveau,
                        'cours': [
                            {
                                'id': cours.id,
                                'code': cours.code,
                                'intitule': cours.intitule,
                                'credits': cours.credits
                            }
                            for cours in prog.cours.all()
                        ]
                    }
                    for prog in dept.programmes.all()
                ]
            }
            for dept in faculte.departements.all()
        ]
    }
