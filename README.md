# AsyncTaskAPI

## Introduction

AsyncTaskAPI is a generic API for managing asynchronous tasks across multiple services, designed for the cloud, application decoupling, and scalability.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- uv

1. Clone the repository

    ```bash
    git clone <url-du-repo>
    cd api
    ```

2. Launch the services

    ```bash
    docker-compose up -d
    ```

3. Install dependencies

    ```bash
    uv sync
    export PATH=$PATH:.venv/bin/
    source .venv/bin/activate
    ```

4. Start the api in dev mode

    ```bash
    uvicorn app.main:app --reload
    ```

5. Go to the swagger ui

    Swagger UI : [http://localhost:8000/docs](http://localhost:8000/docs)
    RabbitMQ UI : [http://localhost:8080/](http://localhost:8080/)

---

## Project structure

```bash
app/
  api/v1/routes/    # Routes FastAPI (tasks, services, health, ...)
  core/             # Config, logger, brokers, database
  models/           # Modèles de données
  schema/           # Schémas de donnés (validation, échanges)
  service/          # Logique métier (DB, queue, etc.)
  main.py           # Démarrage de l'application
docker-compose.yml  # Lancement du mode dev (Postgres, RabbitMQ)
```

---

## Contribution guide

### Conventional Commits

- **feat**: add a new feature
- **fix**: fix a bug
- **docs**: add docs
- **style**: format code
- **refactor**: refactor without bug and features
- **test**: add tests

**Exemples** :

```bash
feat(task): ajout de la création de tâche asynchrone
fix(db): correction de la connexion à PostgreSQL
docs(readme): ajout du guide de démarrage
```

---

## Tests

```bash
pytest
```
