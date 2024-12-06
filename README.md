# Plateforme Éducative en Ligne pour les Universités Gabonaises

Une plateforme moderne et centralisée pour la gestion des universités gabonaises.

## Description

Cette plateforme offre une solution complète pour la gestion académique et administrative des universités gabonaises, incluant :
- Gestion des inscriptions et dossiers étudiants
- Système de e-learning
- Planning et emplois du temps
- Gestion des notes
- Messagerie interne
- Analyses et statistiques

## Technologies Utilisées

- **Backend**: Django (Python)
- **Frontend**: React avec TypeScript
- **Base de données**: PostgreSQL
- **Infrastructure**: AWS/Google Cloud
- **Sécurité**: HTTPS, authentification JWT

## Prérequis

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- pip et npm

## Installation

1. Cloner le repository
```bash
git clone [https://github.com/Amour-kim/IOI_EmergeGabon.giturl-du-repo]
cd gabon-edu-platform
```

2. Installer les dépendances backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Installer les dépendances frontend
```bash
cd frontend
npm install
```

4. Configuration de la base de données
```bash
cd backend
python manage.py migrate
```

5. Lancer le serveur de développement
```bash
# Backend
python manage.py runserver

# Frontend (dans un autre terminal)
cd frontend
npm start
```

## Structure du Projet

```
gabon-edu-platform/
├── backend/                 # API Django
│   ├── apps/               # Applications Django
│   ├── config/             # Configuration du projet
│   └── requirements.txt    # Dépendances Python
├── frontend/               # Application React
│   ├── src/               # Code source React
│   ├── public/            # Fichiers statiques
│   └── package.json       # Dépendances Node.js
└── docs/                  # Documentation
```

## Contribution

Pour contribuer au projet, veuillez suivre les étapes suivantes :
1. Créer une branche pour votre fonctionnalité
2. Commiter vos changements
3. Créer une Pull Request

## Licence

Ce projet est sous licence [À définir]
