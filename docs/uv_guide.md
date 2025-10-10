<div align="center">

**Language / Idioma:**
[🇺🇸 English](#uv-guide---python-package-manager) | [🇪🇸 Español](#guía-de-uv---gestor-de-paquetes-python)

</div>

---

## UV Guide - Python Package Manager

UV is a fast Python package installer and resolver, written in Rust. It's designed to be a drop-in replacement for pip and pip-tools, offering significant speed improvements and better dependency resolution.

## Installation

### Install UV

```bash
# Install UV using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Or using pipx
pipx install uv
```

### Verify Installation

```bash
uv --version
```

## Basic Usage

### Project Initialization

```bash
# Create a new Python project
uv init my-project
cd my-project

# Initialize in existing directory
uv init
```

### Dependency Management

```bash
# Add a dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Add a specific version
uv add "django>=4.0,<5.0"

# Add from requirements.txt
uv add -r requirements.txt

# Remove a dependency
uv remove requests
```

### Running Commands

```bash
# Run a Python script
uv run script.py

# Run with specific Python version
uv run --python 3.11 script.py

# Run a command in the virtual environment
uv run pytest

# Run Jupyter notebook
uv run jupyter notebook
```

### Virtual Environment Management

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Deactivate
deactivate
```

### Sync Dependencies

```bash
# Install all dependencies from pyproject.toml
uv sync

# Sync and install dev dependencies
uv sync --dev

# Sync with lock file
uv sync --frozen
```

## Project Configuration

### pyproject.toml Structure

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.25.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "black>=21.0",
    "flake8>=3.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Lock File

UV automatically generates a `uv.lock` file that pins exact versions of all dependencies for reproducible builds.

## Advanced Usage

### Workspace Management

```bash
# Create a workspace with multiple packages
uv init --workspace
uv add --package my-package requests
```

### Caching

```bash
# Clear cache
uv cache clean

# Show cache info
uv cache dir
```

### Python Version Management

```bash
# Install specific Python version
uv python install 3.11

# List available Python versions
uv python list

# Use specific Python version for project
uv python pin 3.11
```

## Migration from pip

### From requirements.txt

```bash
# Convert requirements.txt to pyproject.toml
uv init
uv add -r requirements.txt
```

### From pip-tools

```bash
# Replace pip-compile
uv add --dev package-name

# Replace pip-sync
uv sync
```

## Best Practices

1. **Always use `uv sync`** instead of `pip install`
2. **Commit `uv.lock`** to version control
3. **Use `uv run`** for scripts and commands
4. **Pin Python version** in `pyproject.toml`
5. **Separate dev dependencies** using optional dependencies

## Troubleshooting

### Common Issues

```bash
# Clear cache if having issues
uv cache clean

# Recreate virtual environment
rm -rf .venv
uv sync

# Check for conflicts
uv tree
```

### Performance Tips

- UV is much faster than pip, but you can still use `--no-cache` if needed
- Use `uv sync --frozen` in CI/CD for faster builds
- Consider using `uv add --no-sync` for multiple additions

---

## Guía de UV - Gestor de Paquetes Python

UV es un instalador y resolvedor de paquetes Python rápido, escrito en Rust. Está diseñado para ser un reemplazo directo de pip y pip-tools, ofreciendo mejoras significativas de velocidad y mejor resolución de dependencias.

## Instalación

### Instalar UV

```bash
# Instalar UV usando el instalador oficial
curl -LsSf https://astral.sh/uv/install.sh | sh

# O usando pip
pip install uv

# O usando pipx
pipx install uv
```

### Verificar Instalación

```bash
uv --version
```

## Uso Básico

### Inicialización de Proyecto

```bash
# Crear un nuevo proyecto Python
uv init mi-proyecto
cd mi-proyecto

# Inicializar en directorio existente
uv init
```

### Gestión de Dependencias

```bash
# Agregar una dependencia
uv add requests

# Agregar una dependencia de desarrollo
uv add --dev pytest

# Agregar una versión específica
uv add "django>=4.0,<5.0"

# Agregar desde requirements.txt
uv add -r requirements.txt

# Remover una dependencia
uv remove requests
```

### Ejecutar Comandos

```bash
# Ejecutar un script Python
uv run script.py

# Ejecutar con versión específica de Python
uv run --python 3.11 script.py

# Ejecutar un comando en el entorno virtual
uv run pytest

# Ejecutar Jupyter notebook
uv run jupyter notebook
```

### Gestión de Entorno Virtual

```bash
# Crear entorno virtual
uv venv

# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Desactivar
deactivate
```

### Sincronizar Dependencias

```bash
# Instalar todas las dependencias desde pyproject.toml
uv sync

# Sincronizar e instalar dependencias de desarrollo
uv sync --dev

# Sincronizar con archivo lock
uv sync --frozen
```

## Configuración del Proyecto

### Estructura de pyproject.toml

```toml
[project]
name = "mi-proyecto"
version = "0.1.0"
description = "Mi proyecto increíble"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.25.0",
    "click>=8.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "black>=21.0",
    "flake8>=3.8",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Archivo Lock

UV genera automáticamente un archivo `uv.lock` que fija las versiones exactas de todas las dependencias para builds reproducibles.

## Uso Avanzado

### Gestión de Workspace

```bash
# Crear un workspace con múltiples paquetes
uv init --workspace
uv add --package mi-paquete requests
```

### Caché

```bash
# Limpiar caché
uv cache clean

# Mostrar información del caché
uv cache dir
```

### Gestión de Versiones de Python

```bash
# Instalar versión específica de Python
uv python install 3.11

# Listar versiones disponibles de Python
uv python list

# Usar versión específica de Python para el proyecto
uv python pin 3.11
```

## Migración desde pip

### Desde requirements.txt

```bash
# Convertir requirements.txt a pyproject.toml
uv init
uv add -r requirements.txt
```

### Desde pip-tools

```bash
# Reemplazar pip-compile
uv add --dev nombre-paquete

# Reemplazar pip-sync
uv sync
```

## Mejores Prácticas

1. **Siempre usar `uv sync`** en lugar de `pip install`
2. **Hacer commit de `uv.lock`** al control de versiones
3. **Usar `uv run`** para scripts y comandos
4. **Fijar versión de Python** en `pyproject.toml`
5. **Separar dependencias de desarrollo** usando dependencias opcionales

## Solución de Problemas

### Problemas Comunes

```bash
# Limpiar caché si hay problemas
uv cache clean

# Recrear entorno virtual
rm -rf .venv
uv sync

# Verificar conflictos
uv tree
```

### Consejos de Rendimiento

- UV es mucho más rápido que pip, pero puedes usar `--no-cache` si es necesario
- Usar `uv sync --frozen` en CI/CD para builds más rápidos
- Considerar usar `uv add --no-sync` para múltiples adiciones
