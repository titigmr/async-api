#!/bin/bash
# Script de démarrage de l'API FastAPI avec Uvicorn.
API_PORT="${PORT:-8000}"
API_HOST="${HOST:-0.0.0.0}"
APP="${APP:-api}"

# API MODE
if [[ "${APP,,}" == "api" ]]; then
    echo "===== API ====="
    exec uvicorn --host "$API_HOST" \
        --port "$API_PORT" api.main:app \
        --workers ${WORKERS:-1} \
        --log-level ${LOG_LEVEL:-info}

fi

# LISTENER MODE
if [[ "${APP}" == "listener" ]]; then
    echo "===== LISTENER ====="
    export PYTHONPATH=$(pwd)/
    exec python3 listener/main.py
fi