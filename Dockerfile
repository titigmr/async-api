FROM python:3.11-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest uv /usr/local/bin/uv
COPY pyproject.toml .
RUN uv sync
COPY api api
COPY scripts/entrypoint.sh /app/
COPY json_schemas /json_schemas
ENV PATH=/app/.venv/bin/:$PATH
CMD ["./entrypoint.sh"]