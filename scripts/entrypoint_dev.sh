#!/bin/bash
# Script de démarrage de l'API FastAPI avec Uvicorn.
API_PORT="${PORT:-8000}"
API_HOST="${HOST:-0.0.0.0}"
APP="${APP:-api}"

# API MODE
if [[ "${APP,,}" == "api" ]]; then
    echo "===== API ====="
    echo "Mode développement"
    uvicorn --host "$API_HOST" --port "$API_PORT" api.main:app --reload 
fi

# LISTENER MODE
if [[ "${APP}" == "listener" ]]; then
    echo "===== LISTENER ====="
    echo "Mode développement"
    export PYTHONPATH=$(pwd)/
    nodemon --legacy-watch --exec python3 listener/main.py
fi