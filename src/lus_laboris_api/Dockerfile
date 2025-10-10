# Light Python 3.13 image
FROM python:3.13.5-slim-bookworm

# Copy uv from official image to handle dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install build dependencies for uv lock file generation and create non-root user
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        && rm -rf /var/lib/apt/lists/* \
        && useradd --create-home --shell /bin/bash apiuser

# Set working directory
WORKDIR /app

# Environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy dependencies files to leverage cache
COPY --chown=apiuser:apiuser pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --locked

# Copy source code
COPY --chown=apiuser:apiuser api ./api

# Switch to non-root user
USER apiuser

# Expose port
EXPOSE 8000

# Entrypoint to execute the script
ENTRYPOINT ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
