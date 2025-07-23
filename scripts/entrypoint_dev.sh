#!/bin/bash

set -e

API_PORT="${PORT:-8000}"
API_HOST="${HOST:-0.0.0.0}"
APP="${APP:-api}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
MAX_RETRIES="${MAX_RETRIES:-30}"
RETRY_INTERVAL="${RETRY_INTERVAL:-2}"


wait_for_database() {
    local retry_count=0

    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
        retry_count=$((retry_count + 1))

        if [ $retry_count -gt $MAX_RETRIES ]; then
            echo "❌ Unable to connect to database after $MAX_RETRIES attempts"
            echo "   Please verify that PostgreSQL is running and accessible"
            exit 1
        fi

        echo "⏳ Attempt $retry_count/$MAX_RETRIES - Database unavailable, waiting ${RETRY_INTERVAL}s..."
        sleep $RETRY_INTERVAL
    done
    echo "✅ Database is available!"
}

run_migrations() {
    echo "🚀 Verifying and running Alembic migrations..."

    if [ ! -f "alembic.ini" ]; then
        echo "❌ alembic.ini file not found"
        exit 1
    fi

    if [ ! -d "migrations" ]; then
        echo "❌ migrations directory not found"
        exit 1
    fi

    echo "⬆️  Applying migrations..."
    if ! alembic upgrade head; then
        echo "❌ Failed to apply migrations"
        echo "   Check the logs above for more details"
        exit 1
    fi
    echo "✅ Migrations applied successfully!"
}

start_api_dev() {
    uvicorn --host "$API_HOST" \
        --port "$API_PORT" api.main:app \
        --reload \
        --log-level ${LOG_LEVEL:-debug}
}
start_listener_dev() {
    nodemon --legacy-watch --exec python3 listener/main.py
}

main() {
    echo "🐳 Starting container - Mode: $APP (development)"

    case "${APP,,}" in
        "api")
            wait_for_database
            run_migrations
            start_api_dev
            ;;
        "listener")
            wait_for_database
            start_listener_dev
            ;;
        *)
            echo "❌ Unrecognized application mode: $APP"
            echo "   Available modes: api, listener"
            exit 1
            ;;
    esac
}

trap 'echo "🛑 Stopping development service..."; exit 0' SIGTERM SIGINT
main "$@"