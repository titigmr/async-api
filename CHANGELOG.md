# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Non publié]

### Ajouté
- Guide de migration complet dans `docs/migrations.md`
- Documentation technique détaillée
- Scripts de test des migrations

### Modifié
- **BREAKING**: Migration complète du système de migrations vers Alembic natif
- README.md entièrement revu avec documentation moderne
- Scripts d'entrypoint refactorisés avec gestion d'erreurs robuste
- Makefile enrichi avec nouvelles commandes de migration
- Dockerfiles optimisés avec installation de postgresql-client

### Supprimé
- Dépendance au script Python `run_migrations.py` (remplacé par Alembic direct)

## [0.1.0] - 2025-07-23

### Ajouté
- Système de migration automatique avec `pg_isready`
- Intégration Alembic native dans les scripts de démarrage
- Commandes Makefile pour la gestion des migrations
- Gestion robuste des erreurs de migration
- Retry automatique pour la connexion base de données
- Variables d'environnement configurables pour les migrations
- Scripts de test et validation des migrations

### Technique
- Utilisation de `pg_isready` pour vérifier la disponibilité PostgreSQL
- Commandes `alembic upgrade head` en remplacement des scripts Python
- Fonctions bash modulaires dans `entrypoint.sh`
- Gestion des signaux SIGTERM/SIGINT pour arrêt propre
- Installation automatique de postgresql-client dans les conteneurs

### Documentation
- README.md modernisé avec emojis et structure claire
- Guide détaillé des commandes de développement
- Section dépannage avec solutions aux problèmes courants
- Architecture du projet mise à jour
- Guide de contribution avec Conventional Commits

### Infrastructure
- Dockerfile optimisé avec installation PostgreSQL client
- Scripts d'entrypoint refactorisés pour robustesse
- Nouvelles commandes Makefile pour migration et monitoring
- Scripts de test automatisés
