from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
import pyotp
import ipaddress

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    """Authentification JWT personnalisée avec vérifications supplémentaires"""
    
    def authenticate(self, request):
        # Authentification JWT standard
        auth_response = super().authenticate(request)
        if not auth_response:
            return None
            
        user, token = auth_response
        
        # Vérifier si le compte est verrouillé
        if user.account_locked_until and user.account_locked_until > timezone.now():
            raise exceptions.AuthenticationFailed(
                'Compte temporairement verrouillé. Réessayez plus tard.'
            )
            
        # Vérifier si le mot de passe doit être changé
        if user.must_change_password:
            raise exceptions.AuthenticationFailed(
                'Vous devez changer votre mot de passe avant de continuer.'
            )
            
        # Vérifier l'expiration du mot de passe
        if user.check_password_expiry():
            user.must_change_password = True
            user.save()
            raise exceptions.AuthenticationFailed(
                'Votre mot de passe a expiré. Veuillez le changer.'
            )
            
        # Mettre à jour l'IP de dernière connexion
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            user.last_login_ip = x_forwarded_for.split(',')[0]
        else:
            user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save()
            
        return auth_response

class TwoFactorAuthentication:
    """Gestion de l'authentification à deux facteurs"""
    
    @staticmethod
    def generate_secret():
        """Générer un nouveau secret pour 2FA"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_totp(secret):
        """Générer un objet TOTP"""
        return pyotp.TOTP(secret)
    
    @staticmethod
    def verify_token(secret, token):
        """Vérifier un token 2FA"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    
    @staticmethod
    def get_qr_code_url(secret, email):
        """Obtenir l'URL du QR code pour l'application d'authentification"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name="Gabon Education Platform"
        )

class IPBasedRateThrottle:
    """Limitation des tentatives de connexion basée sur l'IP"""
    
    def __init__(self, get_cache=None):
        self.cache = get_cache() if get_cache else None
        self.rate = getattr(settings, 'LOGIN_ATTEMPT_LIMIT', 5)
        self.timeout = getattr(settings, 'LOGIN_ATTEMPT_TIMEOUT', 300)
    
    def get_cache_key(self, ip):
        return f'login_attempts_{ip}'
    
    def is_allowed(self, ip):
        """Vérifier si l'IP est autorisée à faire une nouvelle tentative"""
        if not self.cache:
            return True
            
        key = self.get_cache_key(ip)
        attempts = self.cache.get(key, 0)
        
        if attempts >= self.rate:
            return False
            
        self.cache.set(key, attempts + 1, self.timeout)
        return True
    
    def reset(self, ip):
        """Réinitialiser le compteur pour une IP"""
        if self.cache:
            self.cache.delete(self.get_cache_key(ip))

class SecurityMiddleware:
    """Middleware de sécurité personnalisé"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier l'IP
        ip = request.META.get('REMOTE_ADDR')
        if ip and self.is_blocked_ip(ip):
            raise exceptions.PermissionDenied(
                'Votre adresse IP est bloquée.'
            )
        
        response = self.get_response(request)
        
        # Ajouter des en-têtes de sécurité
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    def is_blocked_ip(self, ip):
        """Vérifier si une IP est bloquée"""
        blocked_ips = getattr(settings, 'BLOCKED_IPS', [])
        blocked_ranges = getattr(settings, 'BLOCKED_IP_RANGES', [])
        
        if ip in blocked_ips:
            return True
            
        ip_obj = ipaddress.ip_address(ip)
        return any(
            ip_obj in ipaddress.ip_network(block_range)
            for block_range in blocked_ranges
        )
