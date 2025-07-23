#!/bin/bash
API_PORT="${PORT:-8000}"
API_HOST="${HOST:-0.0.0.0}"
APP="${APP:-api}"

# API MODE
if [[ "${APP,,}" == "api" ]]; then
    echo "===== API ====="
    echo "Mode développement"
    export PYTHONPATH=$(pwd)/

    # Attendre que la base de données soit disponible
    echo "🔄 Attente de la disponibilité de la base de données..."
    DB_HOST="db"
    DB_PORT="5432"
    MAX_RETRIES=30
    RETRY_COUNT=0

    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U postgres > /dev/null 2>&1; do
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -gt $MAX_RETRIES ]; then
            echo "❌ Impossible de se connecter à la base de données après $MAX_RETRIES tentatives"
            exit 1
        fi
        echo "⏳ Tentative $RETRY_COUNT/$MAX_RETRIES - Base de données non disponible, attente..."
        sleep 2
    done

    echo "✅ Base de données disponible !"

    echo "🚀 Exécution des migrations..."
    alembic upgrade head
    if [ $? -ne 0 ]; then
        echo "❌ Échec des migrations. Arrêt du démarrage."
        exit 1
    fi

    echo "✅ Migrations appliquées avec succès !"

    uvicorn --host "$API_HOST" --port "$API_PORT" api.main:app --reload
fi

# LISTENER MODE
if [[ "${APP}" == "listener" ]]; then
    echo "===== LISTENER ====="
    echo "Mode développement"
    nodemon --legacy-watch --exec python3 listener/main.py
fi