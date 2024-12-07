import uuid
from django.core.signing import TimestampSigner
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent(request):
    """Récupère le User-Agent du client"""
    return request.META.get('HTTP_USER_AGENT', '')[:255]

def generate_download_link(file_path, expires_in=3600):
    """
    Génère un lien de téléchargement temporaire sécurisé
    
    Args:
        file_path: Chemin du fichier
        expires_in: Durée de validité en secondes (défaut: 1 heure)
    """
    signer = TimestampSigner()
    token = str(uuid.uuid4())
    signed_token = signer.sign(token)
    
    # Stockage du token en cache avec expiration
    cache_key = f'download_token_{token}'
    cache.set(
        cache_key,
        {
            'file_path': str(file_path),
            'expires_at': timezone.now() + timedelta(seconds=expires_in)
        },
        timeout=expires_in
    )
    
    # Génération de l'URL
    download_url = reverse('bibliotheque:download', kwargs={'token': signed_token})
    return settings.SITE_URL + download_url

def validate_download_token(signed_token):
    """
    Valide un token de téléchargement
    
    Args:
        signed_token: Token signé
    
    Returns:
        tuple: (is_valid, file_path)
    """
    try:
        signer = TimestampSigner()
        token = signer.unsign(signed_token, max_age=3600)
        
        cache_key = f'download_token_{token}'
        download_info = cache.get(cache_key)
        
        if not download_info:
            return False, None
            
        if timezone.now() > download_info['expires_at']:
            cache.delete(cache_key)
            return False, None
            
        return True, download_info['file_path']
        
    except:
        return False, None

def format_file_size(size):
    """
    Formate une taille de fichier en format lisible
    
    Args:
        size: Taille en bytes
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def extract_text_from_file(file_path):
    """
    Extrait le texte d'un fichier pour l'indexation
    
    Args:
        file_path: Chemin du fichier
    """
    # TODO: Implémenter l'extraction de texte selon le type de fichier
    pass
