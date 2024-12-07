"""
Configuration spécifique pour l'application inscriptions.
Ces paramètres doivent être importés dans le fichier settings principal.
"""

# Informations de l'université
NOM_UNIVERSITE = "Université Omar Bongo"
NOM_COURT_UNIVERSITE = "UOB"
ADRESSE_UNIVERSITE = "BP 13131 Libreville - Gabon"
VILLE_UNIVERSITE = "Libreville"
SITE_URL = "https://uob.ga"

# Information du recteur
RECTEUR = {
    'titre': 'Professeur',
    'nom': 'Jean SMITH',
    'fonction': 'Recteur'
}

# Chemins des ressources
LOGO_URL = 'static/images/logo_uob.png'
SIGNATURE_RECTEUR_URL = 'static/images/signature_recteur.png'
CACHET_URL = 'static/images/cachet_uob.png'

# Configuration des documents
DOCUMENTS_SETTINGS = {
    'CERTIFICAT_SCOLARITE': {
        'validite': 365,  # jours
        'prefix': 'CS'
    },
    'ATTESTATION_INSCRIPTION': {
        'validite': 365,
        'prefix': 'AI'
    },
    'CARTE_ETUDIANT': {
        'validite': 365,
        'prefix': 'CE'
    }
}

# Configuration des notifications
NOTIFICATIONS_SETTINGS = {
    'DOCUMENT_GENERE': {
        'email': True,
        'sms': False,
        'delai_expiration': 30  # jours avant expiration
    }
}

# Configuration du stockage
DOCUMENTS_STORAGE = {
    'backend': 'django.core.files.storage.FileSystemStorage',
    'options': {
        'location': 'media/documents',
        'base_url': '/media/documents/'
    }
}
