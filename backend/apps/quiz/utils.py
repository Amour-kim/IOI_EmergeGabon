from django.db.models import Avg, Count, Q
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

def get_quiz_stats(quiz):
    """
    Calcule les statistiques d'un quiz
    
    Args:
        quiz: Instance du modèle Quiz
    """
    cache_key = f'quiz_stats_{quiz.id}_global'
    stats = cache.get(cache_key)
    
    if not stats:
        tentatives = quiz.tentatives.filter(statut='TERMINEE')
        stats = {
            'participation': {
                'total': tentatives.count(),
                'en_cours': quiz.tentatives.filter(
                    statut='EN_COURS'
                ).count(),
                'moyenne_tentatives': quiz.tentatives.values(
                    'etudiant'
                ).annotate(
                    count=Count('id')
                ).aggregate(avg=Avg('count'))['avg'] or 0
            },
            'resultats': {
                'note_moyenne': tentatives.aggregate(
                    avg=Avg('note')
                )['avg'] or 0,
                'temps_moyen': tentatives.aggregate(
                    avg=Avg('temps_passe')
                )['avg'],
                'repartition': tentatives.values(
                    'note'
                ).annotate(total=Count('id')),
                'taux_reussite': (
                    tentatives.filter(
                        note__gte=quiz.note_passage
                    ).count() / tentatives.count() * 100
                    if tentatives.exists() else 0
                )
            },
            'questions': []
        }
        
        for question in quiz.questions.all():
            reponses = question.reponses_etudiant.filter(
                tentative__in=tentatives
            )
            stats['questions'].append({
                'id': question.id,
                'texte': question.texte,
                'type': question.type_question,
                'reponses': {
                    'total': reponses.count(),
                    'correctes': reponses.filter(
                        correcte=True
                    ).count(),
                    'taux_reussite': (
                        reponses.filter(
                            correcte=True
                        ).count() / reponses.count() * 100
                        if reponses.exists() else 0
                    )
                }
            })
        
        # Cache pour 1 heure
        cache.set(cache_key, stats, timeout=3600)
    
    return stats

def get_student_quiz_progress(etudiant, quiz=None):
    """
    Calcule la progression d'un étudiant dans les quiz
    
    Args:
        etudiant: Instance du modèle User (étudiant)
        quiz: Instance optionnelle du modèle Quiz
    """
    if quiz:
        cache_key = f'student_quiz_{etudiant.id}_{quiz.id}_progress'
    else:
        cache_key = f'student_quiz_{etudiant.id}_progress'
    
    progress = cache.get(cache_key)
    
    if not progress:
        tentatives = etudiant.tentatives_quiz
        if quiz:
            tentatives = tentatives.filter(quiz=quiz)
        
        terminees = tentatives.filter(statut='TERMINEE')
        progress = {
            'total_tentatives': tentatives.count(),
            'terminees': terminees.count(),
            'en_cours': tentatives.filter(
                statut='EN_COURS'
            ).count(),
            'note_moyenne': terminees.aggregate(
                avg=Avg('note')
            )['avg'] or 0,
            'temps_moyen': terminees.aggregate(
                avg=Avg('temps_passe')
            )['avg'],
            'meilleures_notes': terminees.values(
                'quiz__titre'
            ).annotate(
                max_note=Max('note')
            ).order_by('-max_note')[:5],
            'derniers_quiz': terminees.select_related(
                'quiz'
            ).order_by('-date_fin')[:5]
        }
        
        if quiz:
            progress.update({
                'meilleure_note': terminees.aggregate(
                    max=Max('note')
                )['max'],
                'derniere_tentative': terminees.order_by(
                    '-date_fin'
                ).first(),
                'tentatives_restantes': max(
                    0,
                    quiz.nombre_tentatives - tentatives.count()
                )
            })
        
        # Cache pour 1 heure
        cache.set(cache_key, progress, timeout=3600)
    
    return progress

def get_question_stats(question):
    """
    Calcule les statistiques d'une question
    
    Args:
        question: Instance du modèle Question
    """
    cache_key = f'question_stats_{question.id}'
    stats = cache.get(cache_key)
    
    if not stats:
        reponses = question.reponses_etudiant.filter(
            tentative__statut='TERMINEE'
        )
        stats = {
            'total_reponses': reponses.count(),
            'correctes': reponses.filter(
                correcte=True
            ).count(),
            'taux_reussite': (
                reponses.filter(
                    correcte=True
                ).count() / reponses.count() * 100
                if reponses.exists() else 0
            )
        }
        
        if question.type_question in ['QCM', 'QCU', 'VRAI_FAUX']:
            stats['repartition_reponses'] = (
                reponses.values(
                    'reponses__texte'
                ).annotate(total=Count('id'))
            )
        
        # Cache pour 1 heure
        cache.set(cache_key, stats, timeout=3600)
    
    return stats
