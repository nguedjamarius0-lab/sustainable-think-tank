# by_nguedjamarius

Site web du by_nguedjamarius — think tank indépendant dédié à la recherche et à l'innovation pour un développement durable et inclusif en Afrique.

## Prérequis

- Python 3.12+
- pip
- PostgreSQL (production) ou SQLite (développement)

## Installation

```bash
# Cloner le dépôt
git clone <url-du-depot>
cd tendereo

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# Initialiser la base de données
flask db upgrade

# Créer un compte administrateur
python seed.py

# Lancer le serveur de développement
python run.py
```

## Configuration

Copiez `.env.example` en `.env` et configurez :

| Variable | Description | Défaut |
|---|---|---|
| `SECRET_KEY` | Clé secrète Flask | (générée) |
| `DATABASE_URL` | URL de la base PostgreSQL | SQLite locale |
| `MAIL_SERVER` | Serveur SMTP | smtp.gmail.com |
| `MAIL_PORT` | Port SMTP | 587 |
| `MAIL_USERNAME` | Email SMTP | — |
| `MAIL_PASSWORD` | Mot de passe SMTP | — |
| `DONATION_URL` | Lien de don externe | — |
| `ADMIN_REG_CODE` | Code d'inscription admin | — |

## Structure du projet

```
tendereo/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── models.py            # Modèles SQLAlchemy (16 modèles)
│   ├── routes/              # Blueprints Flask (10 blueprints)
│   ├── services/            # Services (email)
│   ├── static/              # CSS, images, uploads
│   └── templates/           # Templates Jinja2
├── config.py                # Configuration Flask
├── run.py                   # Point d'entrée dev
├── seed.py                  # Seed base de données
├── requirements.txt         # Dépendances Python
├── render.yaml              # Déploiement Render
├── Dockerfile               # Configuration Docker
└── docker-compose.yml       # Orchestration Docker
```

## Déploiement

### Render (production)

Le fichier `render.yaml` configure automatiquement :
- Service web avec Gunicorn
- Base de données PostgreSQL
- Python 3.12

### Docker

```bash
docker-compose up -d
```

## Commandes utiles

```bash
python run.py                    # Serveur dev
flask db migrate -m "message"    # Générer une migration
flask db upgrade                 # Appliquer les migrations
python seed.py                   # Seed admin (admin@by-nguedjamarius.com)
pytest                           # Lancer les tests
```

## Licence

© 2026 by_nguedjamarius. Tous droits réservés.
