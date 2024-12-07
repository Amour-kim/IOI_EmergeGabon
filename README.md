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

### Backend
- Django 4.2.7 (Python)
- Django REST Framework 3.14.0
- PostgreSQL 13+
- JWT Authentication
- Celery pour les tâches asynchrones

### Frontend
- React 18+ avec TypeScript
- Material-UI
- Redux pour la gestion d'état
- React Router pour la navigation

### Infrastructure
- AWS/Google Cloud (planifié)
- Docker (planifié)
- NGINX (planifié)

## Fonctionnalités

### Gestion des Inscriptions
- Formulaire d'inscription en ligne
- Vérification automatique des informations
- Génération de certificats
- Suivi des dossiers en temps réel
- Notifications automatiques

### Gestion Financière
- Paiements en ligne sécurisés
- Suivi des paiements
- Génération automatique de reçus
- Rapports financiers détaillés
- Tableau de bord analytique

### Système de Tutorat
- Planification de sessions
- Messagerie directe tuteur-étudiant
- Suivi des progrès
- Partage de ressources pédagogiques
- Évaluation des sessions

### Gestion des Départements
- Organisation des cours par département
- Gestion des enseignants
- Publication d'annonces départementales
- Analyses de performance

### Gestion des Événements
- Calendrier académique intégré
- Système d'invitations et RSVP
- Rappels automatiques
- Sondages en temps réel

### Activités et Projets
- Gestion de projets académiques
- Collaboration en équipe
- Stockage et partage de fichiers
- Suivi de l'avancement

### Espace Communautaire
- Forums de discussion
- Messagerie privée
- Groupes d'intérêt
- Sondages communautaires

### Système d'Information
- Publication d'annonces
- Notifications push
- Archivage des communications
- Section opportunités

### Suivi des Diplômés
- Base de données des alumni
- Analyse des parcours professionnels
- Networking

### Bibliothèque Numérique
- Ressources pédagogiques en ligne
- Recherche avancée
- Recommandations personnalisées

## Prérequis

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis (pour Celery)
- pip et npm

## Installation

1. Cloner le repository
```bash
git clone https://github.com/Amour-kim/IOI_EmergeGabon.git
cd gabon-edu-platform
```

2. Configurer la base de données PostgreSQL
```bash
sudo -u postgres createdb gabon_edu_db
sudo -u postgres createuser gabon_edu
sudo -u postgres psql -c "ALTER USER gabon_edu WITH PASSWORD 'gabon_edu_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE gabon_edu_db TO gabon_edu;"
```

3. Installer et configurer le backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

4. Installer et lancer le frontend
```bash
cd frontend
npm install
npm start
```

## Structure du Projet

```
gabon-edu-platform/
├── backend/
│   ├── apps/
│   │   ├── users/         # Gestion des utilisateurs
│   │   ├── courses/       # Gestion des cours
│   │   ├── academic/      # Gestion académique
│   │   └── messaging/     # Système de messagerie
│   ├── config/            # Configuration Django
│   └── requirements.txt   # Dépendances Python
└── frontend/
    ├── src/
    │   ├── components/    # Composants React
    │   ├── pages/         # Pages de l'application
    │   └── services/      # Services API
    └── package.json       # Dépendances Node.js
```

## API Documentation

La documentation de l'API est disponible aux endpoints suivants :
- Swagger UI : `/swagger/`
- ReDoc : `/redoc/`

## Tests

```bash
# Backend
cd backend
python manage.py test

# Frontend
cd frontend
npm test
```

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Contact

- Email : nzilsamuel51@gmail.com
- Site Web : https://gabon-edu.com (à venir)
- GitHub : [@Amour-kim](https://github.com/Amour-kim)
