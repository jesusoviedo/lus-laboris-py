# Light Python 3.13 image
FROM python:3.13.5-slim-bookworm

# Copy uv from official image to handle dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy dependencies files to leverage cache
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --locked

# Copy source code
COPY --chown=appuser:appuser extract_law_text.py ./

# Switch to non-root user
USER appuser

# Entrypoint to execute the script
ENTRYPOINT ["uv", "run", "extract_law_text.py"]

# CMD empty to allow flexible args
CMD []
