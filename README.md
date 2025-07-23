# AsyncTaskAPI

## Introduction

AsyncTaskAPI est une API générique pour la gestion des tâches asynchrones à travers plusieurs services, conçue pour le cloud, le découplage d'applications et la scalabilité.

Cette API permet de :

- 📋 Gérer des tâches asynchrones multi-services
- 🔄 Orchestrer des workflows complexes
- 📊 Monitorer l'exécution des tâches
- 🚀 Scaler horizontalement les workers
- 🎯 Découpler les services producteurs et consommateurs

---

## 🚀 Démarrage rapide

### Prérequis

- **Python 3.11+**
- **Docker & Docker Compose**
- **uv** (gestionnaire de paquets Python moderne)

### Installation et lancement

1. **Cloner le repository**

   ```bash
   git clone <url-du-repo>
   cd api
   ```

2. **Installer uv** (si nécessaire)

   ```bash
   make install-uv
   ```

3. **Installer les dépendances**

   ```bash
   make install
   ```

4. **Lancer l'environnement complet**

   ```bash
   make up
   ```

5. **Accéder aux interfaces**
   - 📖 **API Documentation** : [http://localhost:8000/docs](http://localhost:8000/docs)
   - 🐰 **RabbitMQ Management** : [http://localhost:15672](http://localhost:15672) (login: `kalo` / password: `kalo`)
   - 🩺 **Health Check** : [http://localhost:8000/health](http://localhost:8000/health)

### Vérification du déploiement

```bash
# Vérifier l'état des services
make ps

# Vérifier la santé des services
make health-check

# Voir les logs
make logs
```

---

## 🏗️ Architecture du projet

```
api/
├── api/                    # Code de l'API FastAPI
│   ├── api/v1/            # Routes API version 1
│   ├── core/              # Configuration, base de données, sécurité
│   ├── models/            # Modèles SQLAlchemy
│   ├── repositories/      # Couche d'accès aux données
│   ├── schemas/           # Schémas Pydantic (validation)
│   ├── services/          # Logique métier
│   └── main.py            # Point d'entrée de l'API
├── listener/              # Service d'écoute des messages
│   ├── core/              # Configuration et services partagés
│   ├── services/          # Services d'écoute et notification
│   └── main.py            # Point d'entrée du listener
├── workers/               # Workers pour l'exécution des tâches
│   └── js/                # Workers JavaScript/Node.js
├── migration/             # Migrations Alembic
├── config/                # Fichiers de configuration
├── scripts/               # Scripts d'administration
├── tests/                 # Tests unitaires et d'intégration
└── docs/                  # Documentation technique
```

---

## 🛠️ Commandes de développement

### Gestion des services

```bash
# Démarrer tous les services
make up

# Arrêter tous les services
make down

# Redémarrer tous les services
make restart

# Redémarrer un service spécifique
make restart-api
make restart-listener
make restart-consumer
make restart-worker-python
```

### Logs et debugging

```bash
# Logs de tous les services
make logs

# Logs spécifiques
make logs-api
make logs-listener
make logs-db
make logs-rabbitmq
```

### Base de données

```bash
# Appliquer les migrations
make migrate

# Vérifier l'état des migrations
make migrate-check

# Voir l'historique des migrations
make migrate-history

# Créer une nouvelle migration
make upgrade-revision

# Accéder à la base de données
make exec-db
```

### Tests et qualité de code

```bash
# Lancer tous les tests
make test

# Test spécifique
make test-specific FILE=tests/api/test_example.py

# Couverture de code
make coverage

# Linting
make lint

# Formatage du code
make format
```

### Nettoyage

```bash
# Nettoyer le projet
make clean

# Nettoyer Docker
make clean-cache

# Nettoyage complet
make clean-all
```

---

## 🔧 Configuration

### Variables d'environnement

Le projet utilise les variables d'environnement suivantes :

```bash
# Base de données
DATABASE_URL=postgresql://postgres:postgres@db:5432/tasks

# Message broker
BROKER_URL=amqp://guest:guest@rabbitmq//

# API
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=1
LOG_LEVEL=info

# Services
SERVICES_CONFIG_FILE=./config/services.yaml
CLIENTS_CONFIG_FILE=./config/clients.yaml
```

### Configuration des services

Les services sont configurés via des fichiers YAML dans le dossier `config/` :

- `services.yaml` : Configuration des services disponibles
- `clients.yaml` : Configuration des clients et notifications

---

## 🧪 Tests

### Structure des tests

```bash
tests/
├── api/                   # Tests de l'API
├── listener/              # Tests du listener
├── resources/             # Ressources de test
└── utils/                 # Utilitaires de test
```

### Lancement des tests

```bash
# Tous les tests
make test

# Tests avec couverture
make coverage

# Test spécifique
make test-specific FILE=tests/api/test_tasks.py
```

---

## 📋 Guide de contribution

### Conventional Commits

Nous utilisons les conventions de commits suivantes :

- **feat**: 🎉 Nouvelle fonctionnalité
- **fix**: 🐛 Correction de bug
- **docs**: 📚 Documentation
- **style**: 💄 Formatage du code
- **refactor**: ♻️ Refactorisation
- **test**: 🧪 Tests
- **chore**: 🔧 Tâches de maintenance

**Exemples** :

```bash
feat(task): ajout de la création de tâche asynchrone
fix(db): correction de la connexion à PostgreSQL  
docs(readme): mise à jour du guide de démarrage
test(api): ajout des tests pour les endpoints de tâches
```

### Workflow de développement

1. **Créer une branche** à partir de `main`
2. **Développer** la fonctionnalité avec tests
3. **Linter** le code : `make lint`
4. **Tester** : `make test`
5. **Créer une PR** avec description détaillée

### Versioning

```bash
# Version patch (bug fixes)
make bump-patch

# Version minor (nouvelles fonctionnalités)  
make bump-minor
```

---

## 🚀 Déploiement

### Mode développement

```bash
# Démarrer en mode développement
make up

# Rebuild si nécessaire
make build
```

### Mode production

Le projet inclut des Dockerfiles optimisés pour la production avec :

- Images multi-stage pour réduire la taille
- Migrations automatiques au démarrage avec `pg_isready` et Alembic
- Health checks intégrés
- Gestion des signaux pour l'arrêt propre

---

## 📖 Documentation API

Une fois l'API lancée, accédez à :

- **Swagger UI** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** : [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema** : [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 🔍 Monitoring

L'API inclut des endpoints de monitoring :

- `/health` : Status de santé de l'API
- `/metrics` : Métriques Prometheus (si activé)

---

## 🆘 Dépannage

### Problèmes courants

1. **Base de données non accessible**

   ```bash
   make logs-db
   make health-check
   ```

2. **Migrations échouées**

   ```bash
   make migrate-check
   make migrate-history
   ```

3. **Services qui ne démarrent pas**

   ```bash
   make ps
   make logs
   ```

4. **Reset complet**

   ```bash
   make clean-all
   make up
   ```

### Nouvelles fonctionnalités de migration

Le système de migration a été modernisé pour utiliser :

- ✅ **pg_isready** pour vérifier la disponibilité de la base de données
- ✅ **Commandes Alembic natives** au lieu de scripts Python personnalisés
- ✅ **Gestion d'erreurs robuste** avec retry automatique
- ✅ **Logs détaillés** pour le debugging

---

## 📄 Licence

[Indiquer la licence du projet]
