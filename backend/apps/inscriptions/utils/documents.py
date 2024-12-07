import qrcode
import io
import base64
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
import weasyprint

def generer_qr_code(data):
    """
    Génère un QR code à partir d'une chaîne de caractères et
    retourne une URL data en base64.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Conversion de l'image en base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f'data:image/png;base64,{img_str}'

def generer_pdf(template_name, context, output_file=None):
    """
    Génère un fichier PDF à partir d'un template HTML et d'un contexte.
    Retourne le contenu du PDF ou le sauvegarde dans un fichier.
    """
    # Génération du HTML
    html = render_to_string(template_name, context)
    
    # Génération du PDF
    pdf = weasyprint.HTML(string=html).write_pdf()
    
    if output_file:
        with open(output_file, 'wb') as f:
            f.write(pdf)
        return output_file
    
    return ContentFile(pdf)

def generer_numero_certificat(type_certificat, matricule):
    """
    Génère un numéro unique pour un certificat.
    """
    prefixes = {
        'SCOLARITE': 'CS',
        'INSCRIPTION': 'AI',
        'CARTE': 'CE'
    }
    prefix = prefixes.get(type_certificat, 'XX')
    return f"{prefix}-{matricule}"

def preparer_contexte_document(certificat):
    """
    Prépare le contexte pour la génération d'un document.
    """
    return {
        'etudiant': certificat.dossier.etudiant,
        'dossier': certificat.dossier,
        'certificat': certificat,
        'universite': {
            'nom': settings.NOM_UNIVERSITE,
            'nom_court': settings.NOM_COURT_UNIVERSITE,
            'adresse': settings.ADRESSE_UNIVERSITE,
            'ville': settings.VILLE_UNIVERSITE,
            'site_web': settings.SITE_URL,
            'recteur': settings.RECTEUR,
            'logo_url': settings.LOGO_URL,
        },
        'qr_code_url': generer_qr_code(
            f"{settings.SITE_URL}/verifier/{certificat.numero}"
        ),
    }
