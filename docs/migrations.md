# Guide des Migrations - AsyncTaskAPI

## Vue d'ensemble

Ce guide détaille le système de migration de base de données d'AsyncTaskAPI, qui utilise Alembic avec des vérifications robustes de disponibilité de la base de données.

## Architecture des migrations

### Composants principaux

- **Alembic** : Outil de migration SQLAlchemy
- **pg_isready** : Utilitaire PostgreSQL pour vérifier la disponibilité de la DB
- **Scripts d'entrypoint** : Orchestration du démarrage avec migrations automatiques

### Flux de démarrage

1. **Vérification de la DB** avec `pg_isready`
2. **Application des migrations** avec `alembic upgrade head`
3. **Démarrage de l'application**

## Commandes disponibles

### Gestion des migrations

```bash
# Appliquer toutes les migrations en attente
make migrate

# Vérifier l'état actuel des migrations
make migrate-check

# Voir l'historique complet des migrations
make migrate-history

# Créer une nouvelle migration
make upgrade-revision
```

### Commandes Alembic directes

```bash
# Dans le conteneur API
docker compose exec api alembic current
docker compose exec api alembic history
docker compose exec api alembic upgrade head
docker compose exec api alembic downgrade -1
```

## Création d'une nouvelle migration

1. **Modifier vos modèles** dans `api/models/`
2. **Générer la migration**:
   ```bash
   make upgrade-revision
   # Ou directement:
   docker compose exec api alembic revision --autogenerate -m "Description"
   ```
3. **Vérifier le fichier généré** dans `migration/versions/`
4. **Tester la migration**:
   ```bash
   make migrate
   make migrate-check
   ```

## Résolution de problèmes

### Migration échouée

```bash
# Voir l'état actuel
make migrate-check

# Voir les détails de l'erreur
make logs-api

# Forcer une révision particulière (ATTENTION!)
docker compose exec api alembic stamp <revision_id>
```

### Base de données corrompue

```bash
# Reset complet de la DB
make down
docker volume rm api_postgres_data
make up
```

### Conflit de migration

1. **Voir l'historique**:
   ```bash
   make migrate-history
   ```
2. **Résoudre manuellement** les conflits dans les fichiers de migration
3. **Appliquer la correction**:
   ```bash
   make migrate
   ```

## Bonnes pratiques

### Avant de créer une migration

- ✅ Tester localement d'abord
- ✅ Vérifier que les modèles sont cohérents
- ✅ S'assurer que la migration est réversible

### Nommage des migrations

```bash
# Bon
alembic revision --autogenerate -m "add_task_status_column"
alembic revision --autogenerate -m "create_user_table"

# Moins bon
alembic revision --autogenerate -m "fix"
alembic revision --autogenerate -m "update"
```

### Tests des migrations

```bash
# Tester la migration complète
make down && make up

# Tester avec données existantes
make test-specific FILE=tests/migration/
```

## Configuration avancée

### Variables d'environnement

```bash
# Customisation du wait de la DB
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
MAX_RETRIES=30
RETRY_INTERVAL=2
```

### Configuration Alembic

Le fichier `alembic.ini` permet de configurer :
- Localisation des scripts de migration
- Format des noms de fichiers
- Options de logging

## Monitoring des migrations

### Logs de migration

```bash
# Voir les logs complets du démarrage
make logs-api | grep -E "(migration|alembic)"

# Monitoring en temps réel
make logs-api -f
```

### Métriques

L'état des migrations peut être exposé via l'endpoint `/health` qui inclut :
- Version de la base de données
- Status des migrations en attente
- Temps de dernière migration

## Automatisation

### CI/CD

Les migrations sont automatiquement appliquées au démarrage de l'API, ce qui permet :
- Déploiements sans intervention manuelle
- Cohérence entre les environnements
- Rollbacks simplifiés

### Scripts de maintenance

```bash
# Script de sauvegarde avant migration
scripts/backup_db.sh

# Script de test de migration
scripts/test_migrations.sh

# Script de rollback d'urgence
scripts/emergency_rollback.sh
```
