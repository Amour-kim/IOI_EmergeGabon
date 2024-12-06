from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

def role_required(roles):
    """
    Décorateur pour restreindre l'accès aux utilisateurs avec certains rôles
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse('login'))
                
            if isinstance(roles, str):
                required_roles = [roles]
            else:
                required_roles = roles
                
            if request.user.role in required_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            raise PermissionDenied
        return _wrapped_view
    return decorator

def password_change_required(view_func):
    """
    Décorateur pour rediriger vers le changement de mot de passe si nécessaire
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
            
        if request.user.must_change_password:
            messages.warning(request, 'Vous devez changer votre mot de passe.')
            return redirect(reverse('password_change'))
            
        if request.user.check_password_expiry():
            request.user.must_change_password = True
            request.user.save()
            messages.warning(request, 'Votre mot de passe a expiré.')
            return redirect(reverse('password_change'))
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def account_active_required(view_func):
    """
    Décorateur pour vérifier si le compte est actif et non verrouillé
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
            
        if not request.user.is_active:
            messages.error(request, 'Votre compte est désactivé.')
            return redirect(reverse('login'))
            
        if request.user.account_locked_until and request.user.account_locked_until > timezone.now():
            messages.error(request, 'Votre compte est temporairement verrouillé.')
            return redirect(reverse('login'))
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
