#!/bin/bash
# Script de démarrage de l'API FastAPI avec Uvicorn.

API_PORT="${PORT:-8000}"
API_HOST="${HOST:-0.0.0.0}"
DEVELOPMENT="${DEVELOPMENT:-false}"


if [[ "${DEVELOPMENT,,}" == "true" ]]; then
    echo "Mode développement activé"
    uvicorn --host "$API_HOST" --port "$API_PORT" api.main:app --reload
else
    exec uvicorn --host "$API_HOST" \
        --port "$API_PORT" api.main:app \
        --workers ${WORKERS:-1} \
        --log-level ${LOG_LEVEL:-info}
fi
