from rest_framework import permissions

class IsQuizCreator(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur est le créateur du quiz"""
    def has_object_permission(self, request, view, obj):
        return obj.createur == request.user

class CanTakeQuiz(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur peut passer le quiz"""
    def has_object_permission(self, request, view, obj):
        # Les créateurs et les administrateurs peuvent toujours accéder
        if request.user.is_staff or obj.createur == request.user:
            return True
        
        # Vérifie si l'étudiant est inscrit au cours
        return request.user.cours_inscrits.filter(
            id=obj.cours.id
        ).exists()

class IsQuizParticipant(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur participe au quiz"""
    def has_object_permission(self, request, view, obj):
        # Les créateurs et les administrateurs peuvent toujours accéder
        if request.user.is_staff or obj.quiz.createur == request.user:
            return True
        
        # Vérifie si l'utilisateur est l'étudiant qui a fait la tentative
        return obj.etudiant == request.user

class CanModifyResponse(permissions.BasePermission):
    """Permission pour vérifier si l'utilisateur peut modifier une réponse"""
    def has_object_permission(self, request, view, obj):
        # Seul l'étudiant qui a fait la tentative peut modifier ses réponses
        if obj.tentative.etudiant != request.user:
            return False
        
        # La modification n'est possible que si la tentative est en cours
        return obj.tentative.statut == 'EN_COURS'
