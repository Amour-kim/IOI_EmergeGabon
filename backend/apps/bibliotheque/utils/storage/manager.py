import os
import hashlib
from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.utils.text import slugify

class BibliothequeStorage(FileSystemStorage):
    """Gestionnaire de stockage personnalisé pour la bibliothèque"""

    def __init__(self):
        super().__init__(
            location=settings.MEDIA_ROOT,
            base_url=settings.MEDIA_URL
        )

    def _save(self, name, content):
        """
        Sauvegarde un fichier avec un nom unique basé sur son contenu
        
        Args:
            name: Nom original du fichier
            content: Contenu du fichier
        """
        # Calcul du hash du contenu
        if hasattr(content, 'chunks'):
            sha1 = hashlib.sha1()
            for chunk in content.chunks():
                sha1.update(chunk)
            file_hash = sha1.hexdigest()
        else:
            file_hash = hashlib.sha1(content.read()).hexdigest()
            content.seek(0)

        # Construction du chemin
        name = self._build_path(name, file_hash)
        
        # Vérification si le fichier existe déjà
        if self.exists(name):
            return name
        
        return super()._save(name, content)

    def _build_path(self, name, file_hash):
        """
        Construit le chemin du fichier
        
        Args:
            name: Nom original du fichier
            file_hash: Hash du contenu
        """
        # Extraction de l'extension
        ext = Path(name).suffix.lower()
        
        # Construction du chemin basé sur le hash
        path_parts = [
            'bibliotheque',
            'files',
            file_hash[:2],
            file_hash[2:4]
        ]
        
        # Création du nom final
        filename = f"{file_hash}{ext}"
        path_parts.append(filename)
        
        return os.path.join(*path_parts)

    def get_available_name(self, name, max_length=None):
        """
        Retourne un nom de fichier disponible
        
        Args:
            name: Nom du fichier
            max_length: Longueur maximale du nom
        """
        return name

    def get_thumbnail_path(self, name):
        """
        Retourne le chemin de la miniature
        
        Args:
            name: Nom du fichier
        """
        path = Path(name)
        thumbnail_name = f"{path.stem}_thumb.jpg"
        return os.path.join(
            'bibliotheque',
            'thumbnails',
            path.parent.name,
            thumbnail_name
        )

    def get_preview_path(self, name):
        """
        Retourne le chemin de la prévisualisation
        
        Args:
            name: Nom du fichier
        """
        path = Path(name)
        preview_name = f"{path.stem}_preview.pdf"
        return os.path.join(
            'bibliotheque',
            'previews',
            path.parent.name,
            preview_name
        )

class VirusScanner:
    """Scanner antivirus pour les fichiers uploadés"""

    def __init__(self):
        # TODO: Implémenter la connexion à ClamAV
        pass

    def scan_file(self, file):
        """
        Scanne un fichier pour détecter les virus
        
        Args:
            file: Fichier à scanner
        """
        # TODO: Implémenter le scan avec ClamAV
        return True

class FileValidator:
    """Validateur de fichiers"""

    def __init__(self):
        self.allowed_extensions = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        self.max_size = 50 * 1024 * 1024  # 50 MB

    def validate(self, file):
        """
        Valide un fichier
        
        Args:
            file: Fichier à valider
        """
        # Vérification de l'extension
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValueError(
                f"Extension de fichier non autorisée. "
                f"Extensions autorisées: {', '.join(self.allowed_extensions.keys())}"
            )

        # Vérification de la taille
        if file.size > self.max_size:
            raise ValueError(
                f"Fichier trop volumineux. "
                f"Taille maximale autorisée: {self.max_size / 1024 / 1024} MB"
            )

        # Vérification du type MIME
        mime_type = file.content_type
        if mime_type != self.allowed_extensions[ext]:
            raise ValueError(
                f"Type de fichier non autorisé. "
                f"Type attendu pour l'extension {ext}: {self.allowed_extensions[ext]}"
            )

        return True
