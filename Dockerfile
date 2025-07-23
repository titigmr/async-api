FROM python:3.11-slim
WORKDIR /app
# Install necessary packages
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest uv /usr/local/bin/uv
# Install dependencies
COPY pyproject.toml .
RUN uv sync
# Copying the application code
COPY api api
COPY listener listener
COPY migrations migrations
COPY alembic.ini .
COPY scripts/entrypoint.sh /app/

ENV PATH=/app/.venv/bin/:$PATH
CMD ["./entrypoint.sh"]