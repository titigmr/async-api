FROM python:3.11-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest uv /usr/local/bin/uv  
COPY pyproject.toml .
RUN uv sync
COPY app /app/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]