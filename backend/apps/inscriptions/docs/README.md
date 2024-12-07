# Module de Gestion des Documents Officiels

Ce module fait partie de l'application Inscriptions et gère la génération, la validation et le suivi des documents officiels pour les étudiants.

## Types de Documents

1. **Certificat de Scolarité**
   - Format A4 portrait
   - En-tête officiel de l'université
   - QR code de vérification
   - Signature du recteur
   - Numéro unique format CS-XXXXX

2. **Attestation d'Inscription**
   - Format A4 portrait
   - En-tête officiel
   - QR code de vérification
   - Signature et cachet
   - Numéro unique format AI-XXXXX

3. **Carte Étudiante**
   - Format carte bancaire (85.6mm x 53.98mm)
   - Photo de l'étudiant
   - QR code de vérification
   - Numéro unique format CE-XXXXX

## API Endpoints

### Génération de Documents

```http
POST /api/inscriptions/documents/{dossier_id}/certificat-scolarite/
POST /api/inscriptions/documents/{dossier_id}/attestation-inscription/
POST /api/inscriptions/documents/{dossier_id}/carte-etudiant/
```

### Vérification de Documents

```http
GET /api/inscriptions/verifier/{numero}/
```

### Liste des Documents

```http
GET /api/inscriptions/documents/mes-certificats/
```

## Permissions

- `IsAdminOrScolarite` : Administrateurs et personnel de la scolarité
- `IsOwnerOrAdmin` : Étudiant propriétaire ou administrateurs

## Configuration

Les paramètres sont configurables dans `settings.py` :

```python
# Informations de l'université
NOM_UNIVERSITE = "Université Omar Bongo"
NOM_COURT_UNIVERSITE = "UOB"

# Configuration des documents
DOCUMENTS_SETTINGS = {
    'CERTIFICAT_SCOLARITE': {
        'validite': 365,
        'prefix': 'CS'
    },
    ...
}
```

## Commandes de Gestion

Génération des cartes étudiantes :

```bash
python manage.py generer_cartes
```

Options :
- `--force` : Régénère les cartes existantes
- `--dossier ID` : Génère pour un dossier spécifique

## Système de Vérification

Les documents peuvent être vérifiés via :
1. QR code sur le document
2. Numéro unique sur le site web
3. API de vérification

## Sécurité

- Filigrane sur les documents
- QR codes uniques
- Numéros de série
- Signatures cryptographiques
- Vérification en ligne

## Stockage

Les documents sont stockés dans :
- `media/certificats/` : PDFs générés
- Base de données : Métadonnées et références

## Notifications

Le système notifie automatiquement :
- Génération de nouveau document
- Expiration proche (30 jours avant)
- Document expiré

## Tests

Exécuter les tests :

```bash
python manage.py test apps.inscriptions.tests.test_documents
python manage.py test apps.inscriptions.tests.test_api
```
