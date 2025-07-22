#!/bin/bash
API_PORT="${PORT:-8000}"
API_HOST="${HOST:-0.0.0.0}"
APP="${APP:-api}"

# API MODE
if [[ "${APP,,}" == "api" ]]; then
    echo "===== API ====="
    echo "Mode développement"
    export PYTHONPATH=$(pwd)/
    echo "🚀 Exécution des migrations..."
    python run_migrations.py
    if [ $? -ne 0 ]; then
        echo "❌ Échec des migrations. Arrêt du démarrage."
        exit 1
    fi

    uvicorn --host "$API_HOST" --port "$API_PORT" api.main:app --reload
fi

# LISTENER MODE
if [[ "${APP}" == "listener" ]]; then
    echo "===== LISTENER ====="
    echo "Mode développement"
    nodemon --legacy-watch --exec python3 listener/main.py
fi