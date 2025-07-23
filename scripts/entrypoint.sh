#!/bin/bash
# Script de démarrage de l'API FastAPI avec Uvicorn et migration Alembic.

set -e  # Arrêter le script en cas d'erreur

API_PORT="${PORT:-8000}"
API_HOST="${HOST:-0.0.0.0}"
APP="${APP:-api}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
MAX_RETRIES="${MAX_RETRIES:-30}"
RETRY_INTERVAL="${RETRY_INTERVAL:-2}"

wait_for_database() {
    echo "🔍 Attente de la disponibilité de la base de données..."
    echo "   Host: $DB_HOST"
    echo "   Port: $DB_PORT"
    echo "   User: $DB_USER"

    local retry_count=0

    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
        retry_count=$((retry_count + 1))

        if [ $retry_count -gt $MAX_RETRIES ]; then
            echo "❌ Impossible de se connecter à la base de données après $MAX_RETRIES tentatives"
            echo "   Vérifiez que PostgreSQL est démarré et accessible"
            exit 1
        fi

        echo "⏳ Tentative $retry_count/$MAX_RETRIES - Base de données non disponible, attente ${RETRY_INTERVAL}s..."
        sleep $RETRY_INTERVAL
    done

    echo "✅ Base de données disponible !"
}

run_migrations() {
    echo "🚀 Vérification et exécution des migrations Alembic..."

    if [ ! -f "alembic.ini" ]; then
        echo "❌ Fichier alembic.ini non trouvé"
        exit 1
    fi

    echo "📋 Vérification de l'état des migrations..."
    if ! alembic current > /dev/null 2>&1; then
        echo "⚠️  Aucune migration trouvée, initialisation..."
        if ! alembic stamp head > /dev/null 2>&1; then
            echo "❌ Impossible d'initialiser Alembic"
            exit 1
        fi
    fi

    echo "⬆️  Application des migrations..."
    if ! alembic upgrade head; then
        echo "❌ Échec de l'application des migrations"
        echo "   Vérifiez les logs ci-dessus pour plus de détails"
        exit 1
    fi

    echo "✅ Migrations appliquées avec succès !"
    echo "📊 État final des migrations :"
    alembic current
}

start_api() {
    echo "🚀 Démarrage de l'API FastAPI..."
    echo "   Host: $API_HOST"
    echo "   Port: $API_PORT"
    echo "   Workers: ${WORKERS:-1}"
    echo "   Log Level: ${LOG_LEVEL:-info}"

    exec uvicorn --host "$API_HOST" \
        --port "$API_PORT" api.main:app \
        --workers ${WORKERS:-1} \
        --log-level ${LOG_LEVEL:-info}
}

start_listener() {
    echo "🎧 Démarrage du service Listener..."
    wait_for_database

    echo "✅ Démarrage du listener..."
    exec python3 listener/main.py
}

main() {
    echo "================================================"
    echo "🐳 Démarrage du conteneur - Mode: $APP"
    echo "================================================"

    case "${APP,,}" in
        "api")
            echo "===== MODE API ====="
            wait_for_database
            run_migrations
            start_api
            ;;
        "listener")
            echo "===== MODE LISTENER ====="
            start_listener
            ;;
        *)
            echo "❌ Mode d'application non reconnu: $APP"
            echo "   Modes disponibles: api, listener"
            exit 1
            ;;
    esac
}

trap 'echo "🛑 Arrêt du service..."; exit 0' SIGTERM SIGINT
main "$@"