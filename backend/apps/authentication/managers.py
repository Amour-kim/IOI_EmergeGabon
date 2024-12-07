from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Gestionnaire personnalisé pour le modèle User où l'email est
    l'identifiant unique pour l'authentification au lieu du nom d'utilisateur.
    """
    
    def create_user(self, email, password, **extra_fields):
        """
        Crée et sauvegarde un utilisateur avec l'email et le mot de passe donnés.
        """
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        if not extra_fields.get('matricule'):
            raise ValueError(_('Le matricule est obligatoire'))
        if not extra_fields.get('nom'):
            raise ValueError(_('Le nom est obligatoire'))
        if not extra_fields.get('prenoms'):
            raise ValueError(_('Les prénoms sont obligatoires'))
        if not extra_fields.get('categorie'):
            raise ValueError(_('La catégorie est obligatoire'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        """
        Crée et sauvegarde un superutilisateur avec l'email et le mot de passe donnés.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('categorie', 'PROFESSIONNEL')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)
