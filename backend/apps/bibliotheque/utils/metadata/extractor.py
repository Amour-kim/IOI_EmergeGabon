import os
import fitz  # PyMuPDF
from PIL import Image
import easyocr
import magic
from django.conf import settings
from django.core.files.storage import default_storage

class MetadataExtractor:
    """Classe pour extraire les métadonnées des fichiers"""

    def __init__(self):
        self.mime = magic.Magic(mime=True)
        self.ocr = easyocr.Reader(['fr', 'en'])

    def extract_metadata(self, file_path):
        """
        Extrait les métadonnées d'un fichier
        
        Args:
            file_path: Chemin du fichier
        """
        mime_type = self.mime.from_file(file_path)
        
        if mime_type == 'application/pdf':
            return self._extract_pdf_metadata(file_path)
        elif mime_type.startswith('image/'):
            return self._extract_image_metadata(file_path)
        elif mime_type == 'application/msword' or \
             mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return self._extract_doc_metadata(file_path)
        else:
            return {}

    def _extract_pdf_metadata(self, file_path):
        """Extrait les métadonnées d'un PDF"""
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            
            # Extraction du texte de la première page
            first_page = doc[0]
            text = first_page.get_text()
            
            # Génération de la miniature
            pix = first_page.get_pixmap()
            thumbnail_path = self._generate_thumbnail_path(file_path)
            pix.save(thumbnail_path)
            
            result = {
                'titre': metadata.get('title'),
                'auteur': metadata.get('author'),
                'sujet': metadata.get('subject'),
                'mots_cles': metadata.get('keywords'),
                'createur': metadata.get('creator'),
                'producteur': metadata.get('producer'),
                'date_creation': metadata.get('creationDate'),
                'date_modification': metadata.get('modDate'),
                'nombre_pages': len(doc),
                'texte_premiere_page': text[:1000],
                'miniature': thumbnail_path
            }
            
            doc.close()
            return result
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées PDF: {e}")
            return {}

    def _extract_image_metadata(self, file_path):
        """Extrait les métadonnées d'une image"""
        try:
            with Image.open(file_path) as img:
                # Extraction du texte avec OCR
                text = self.ocr.readtext(file_path)
                text = ' '.join([t[1] for t in text])
                
                # Génération de la miniature
                thumbnail_path = self._generate_thumbnail_path(file_path)
                img.thumbnail((200, 200))
                img.save(thumbnail_path)
                
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'taille': img.size,
                    'texte_extrait': text[:1000],
                    'miniature': thumbnail_path
                }
                
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées image: {e}")
            return {}

    def _extract_doc_metadata(self, file_path):
        """Extrait les métadonnées d'un document Word"""
        try:
            # TODO: Implémenter l'extraction des métadonnées Word
            # Utiliser python-docx pour les fichiers .docx
            # et antiword pour les fichiers .doc
            return {}
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées Word: {e}")
            return {}

    def _generate_thumbnail_path(self, file_path):
        """Génère le chemin de la miniature"""
        base_name = os.path.basename(file_path)
        name, _ = os.path.splitext(base_name)
        thumbnail_name = f"{name}_thumb.jpg"
        return os.path.join(
            settings.MEDIA_ROOT,
            'bibliotheque',
            'thumbnails',
            thumbnail_name
        )

    def clean_metadata(self, metadata):
        """Nettoie les métadonnées extraites"""
        cleaned = {}
        
        for key, value in metadata.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            elif isinstance(value, (list, tuple)):
                cleaned[key] = [str(v).strip() for v in value if v]
            elif value is not None:
                cleaned[key] = value
        
        return cleaned
