# Imagen base ligera de Python 3.13
FROM python:3.13.5-slim-bookworm

# Copiar uv desde la imagen oficial para manejar dependencias
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Establecer directorio de trabajo
WORKDIR /app

# Variables de entorno
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copiar archivos de dependencias para aprovechar cache
COPY pyproject.toml uv.lock ./

# Instalar dependencias
RUN uv sync --locked

# Copiar codigo fuente
COPY extract_law_text.py ./

# Crear usuario no-root y asignar permisos
RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser /app
USER appuser

# Comando por defecto
CMD ["uv", "run", "extract_law_text.py", "--mode", "gcs", "--bucket-name", "py-labor-law-rag-bucket"]
