from rest_framework import permissions

class IsTuteurOrReadOnly(permissions.BasePermission):
    """
    Permission permettant uniquement aux tuteurs de modifier leurs séances.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Vérifie si l'utilisateur est le tuteur
        if hasattr(obj, 'tuteur'):
            return obj.tuteur.utilisateur == request.user
        elif hasattr(obj, 'seance'):
            return obj.seance.tuteur.utilisateur == request.user
        return False

class IsEtudiantInscrit(permissions.BasePermission):
    """
    Permission permettant uniquement aux étudiants inscrits
    d'accéder aux supports et de soumettre des évaluations.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Vérifie si l'étudiant est inscrit à la séance
        seance = obj.seance if hasattr(obj, 'seance') else obj
        return seance.inscriptions.filter(
            etudiant=request.user,
            statut='CONFIRMEE'
        ).exists()

class IsAdminOrTuteur(permissions.BasePermission):
    """
    Permission pour les actions réservées aux administrateurs
    et aux tuteurs validés.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.user.is_staff:
            return True
            
        return hasattr(request.user, 'profil_tuteur') and \
               request.user.profil_tuteur.statut == 'ACTIF'
