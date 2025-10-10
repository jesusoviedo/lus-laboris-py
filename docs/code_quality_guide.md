<div align="center">

**Language / Idioma:**
[🇺🇸 English](#code-quality-guide) | [🇪🇸 Español](#guía-de-calidad-de-código)

</div>

---

# Code Quality Guide

This guide explains the code quality and testing strategy implemented in the Lus Laboris project.

## Quality Assurance Strategy

The project implements a **multi-layer QA approach**:

1. **Pre-commit Hooks** - Local validation before commits
2. **GitHub Actions** - Automated CI/CD quality checks
3. **Linting & Formatting** - Code style consistency
4. **Type Checking** - Static type validation
5. **Security Scanning** - Vulnerability detection
6. **Testing** - Unit and integration tests

---

## Tools Used

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Ruff** | Linting + Formatting (replaces black, isort, flake8) | `pyproject.toml` |
| **Mypy** | Type checking | `pyproject.toml` |
| **Bandit** | Security scanning | `pyproject.toml` |
| **Pytest** | Testing framework | `pyproject.toml` |
| **Pre-commit** | Git hooks automation | `.pre-commit-config.yaml` |
| **Gitleaks** | Secrets detection | `.pre-commit-config.yaml` |
| **Markdownlint** | Markdown linting | `.pre-commit-config.yaml` |
| **Hadolint** | Dockerfile linting | `.pre-commit-config.yaml` |

---

## Quick Start

### 1. Install Pre-commit Hooks

```bash
# Install pre-commit
uv tool install pre-commit

# Install hooks in your local repository
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

### 2. Install Development Dependencies

```bash
# For API
cd src/lus_laboris_api
uv sync --extra dev

# For Processing
cd src/processing
uv sync --extra dev

# For Utils
cd utils
uv sync --extra dev
```

### 3. Run Quality Checks Locally

```bash
# Lint with ruff
uv run ruff check .

# Format with ruff
uv run ruff format .

# Type check with mypy
uv run mypy .

# Security scan with bandit
uv run bandit -r . -c pyproject.toml

# Run tests
uv run pytest tests/ -v --cov
```

---

## Pre-commit Hooks

The `.pre-commit-config.yaml` file configures the following hooks:

### General File Checks

- ✅ Remove trailing whitespace
- ✅ Fix end of files
- ✅ Check YAML syntax
- ✅ Check JSON syntax
- ✅ Check TOML syntax
- ✅ Detect large files (>1MB)
- ✅ Detect merge conflicts
- ✅ Detect private keys
- ✅ Fix line endings (LF)
- ✅ Check docstrings
- ✅ Detect debug statements

### Python Code Quality

- ✅ **Ruff linter** - Fast Python linter
- ✅ **Ruff formatter** - Fast Python formatter
- ✅ **Mypy** - Type checking
- ✅ **Bandit** - Security vulnerability scanning

### Security

- ✅ **Gitleaks** - Detect secrets and credentials
- ✅ **Bandit** - Python security issues

### Documentation

- ✅ **Markdownlint** - Markdown file linting
- ✅ **YAML formatter** - YAML file formatting

### Docker

- ✅ **Hadolint** - Dockerfile best practices

---

## GitHub Actions Workflow

The `code-quality.yml` workflow runs automatically on:

- Push to any branch (affecting Python, YAML, or Markdown files)
- Pull requests to any branch

### Jobs Executed

1. **Pre-commit** - Runs all pre-commit hooks
2. **Lint API** - Lints API code with ruff
3. **Lint Processing** - Lints processing scripts with ruff
4. **Lint Utils** - Lints utility scripts with ruff
5. **Security Scan** - Runs bandit security checks
6. **Type Check** - Runs mypy type checking
7. **Test API** - Runs pytest with coverage
8. **Summary** - Generates quality report

### Viewing Results

- Check the **Actions** tab in GitHub
- View detailed logs for each job
- Download artifacts (coverage reports, security reports)

---

## 🎨 Code Style Configuration

### Ruff Configuration

**Line Length:** 100 characters
**Python Version:** 3.13+
**Quote Style:** Double quotes

**Enabled Rules:**

- E, W: pycodestyle
- F: pyflakes
- I: isort (import sorting)
- N: pep8-naming
- UP: pyupgrade
- B: flake8-bugbear
- C4: flake8-comprehensions
- And many more...

**Auto-fix:** Enabled for most rules

### Example

```python
# Before ruff
import os
import sys
from typing import Dict,List
def my_function(x,y,z):
    return x+y+z

# After ruff
import os
import sys
from typing import Dict, List


def my_function(x: int, y: int, z: int) -> int:
    return x + y + z
```

---

## 🔍 Type Checking with Mypy

Mypy is configured to:

- ✅ Warn on return type issues
- ✅ Check untyped definitions
- ✅ Warn on redundant casts
- ✅ Warn on unused ignores
- ✅ Check for unreachable code
- ✅ Enforce strict equality

**Note:** Type checking is not strict by default to allow gradual adoption.

### Adding Type Hints

```python
# Without type hints
def process_data(data):
    return data.upper()

# With type hints
def process_data(data: str) -> str:
    return data.upper()
```

---

## Security Scanning

### Bandit

Scans for common security issues:

- SQL injection vulnerabilities
- Hardcoded passwords
- Use of insecure functions
- Weak cryptography
- And more...

### Gitleaks

Detects secrets in code:

- API keys
- Passwords
- Private keys
- Tokens
- Credentials

**Important:** Gitleaks runs on all commits to prevent secret leaks.

---

## 🧪 Testing Strategy

### Test Structure

```text
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_rag_service.py
│   ├── test_qdrant_service.py
│   └── test_auth.py
├── integration/             # Integration tests (slower, with dependencies)
│   ├── test_api_endpoints.py
│   └── test_vectorstore.py
└── conftest.py             # Pytest fixtures and configuration
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_rag_service.py

# Run tests by marker
uv run pytest -m unit          # Only unit tests
uv run pytest -m "not slow"    # Skip slow tests
```

### Writing Tests

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## Coverage Reports

Coverage reports are generated automatically:

- **Terminal:** Summary in console
- **HTML:** Detailed report in `htmlcov/`
- **XML:** For CI/CD integration

### Viewing Coverage

```bash
# Generate HTML report
uv run pytest --cov=. --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Workflow Integration

### Local Development

```bash
# 1. Make changes to code
vim src/lus_laboris_api/api/endpoints/rag.py

# 2. Run pre-commit (automatic on git commit)
git add .
git commit -m "feat: add new feature"
# Pre-commit runs automatically

# 3. If pre-commit fails, fix issues and retry
ruff check --fix .
git add .
git commit -m "feat: add new feature"
```

### CI/CD Pipeline

```text
Push/PR → GitHub Actions Triggered
  ↓
Pre-commit Hooks (all files)
  ↓
Parallel Jobs:
  ├─ Lint API
  ├─ Lint Processing
  ├─ Lint Utils
  ├─ Security Scan
  ├─ Type Check
  └─ Tests
  ↓
Quality Summary
  ↓
✅ Pass → Merge allowed
❌ Fail → Fix required
```

---

## Quality Gates

### Minimum Requirements

- ✅ All pre-commit hooks pass
- ✅ No linting errors (ruff)
- ✅ No security vulnerabilities (bandit)
- ✅ No secrets detected (gitleaks)
- ✅ All tests pass (pytest)
- ⚠️ Type checking warnings allowed (gradual adoption)

### Recommended Targets

- 📊 Test coverage: >80%
- 🔒 Security score: A grade
- 📝 Docstring coverage: >70%
- 🎨 Code complexity: <10 (cyclomatic)

---

## Common Commands

### Linting

```bash
# Check for issues
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Check specific file
uv run ruff check src/lus_laboris_api/api/main.py
```

### Formatting

```bash
# Check formatting
uv run ruff format --check .

# Apply formatting
uv run ruff format .
```

### Type Checking

```bash
# Check types
uv run mypy .

# Check specific module
uv run mypy src/lus_laboris_api/api/
```

### Security

```bash
# Run security scan
uv run bandit -r src/ -c pyproject.toml

# Generate JSON report
uv run bandit -r src/ -c pyproject.toml -f json -o security-report.json
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=. --cov-report=term-missing

# Run specific test
uv run pytest tests/unit/test_rag_service.py::test_specific_function
```

---

## Best Practices

### 1. Commit Frequently

- Make small, focused commits
- Let pre-commit catch issues early

### 2. Fix Issues Immediately

- Don't skip pre-commit hooks
- Address linting errors before pushing

### 3. Write Tests

- Add tests for new features
- Maintain test coverage

### 4. Use Type Hints

- Add type hints to function signatures
- Helps catch bugs early

### 5. Review Security Warnings

- Take bandit warnings seriously
- Never commit secrets

### 6. Keep Dependencies Updated

- Regularly update dependencies
- Check for security vulnerabilities

---

## Troubleshooting

### Pre-commit Hook Fails

```bash
# Update hooks
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Ruff Issues

```bash
# Show detailed error
uv run ruff check --show-source .

# Ignore specific rule for a line
# ruff: noqa: E501

# Ignore specific rule for a file
# Add to pyproject.toml per-file-ignores
```

### Mypy Errors

```bash
# Ignore missing imports
# type: ignore[import]

# Skip type checking for a function
# type: ignore
```

---

## Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)

---

# Guía de Calidad de Código

Esta guía explica la estrategia de calidad de código y testing implementada en el proyecto Lus Laboris.

## Estrategia de Aseguramiento de Calidad

El proyecto implementa un **enfoque de QA multi-capa**:

1. **Pre-commit Hooks** - Validación local antes de commits
2. **GitHub Actions** - Verificaciones automáticas de calidad en CI/CD
3. **Linting & Formateo** - Consistencia de estilo de código
4. **Verificación de Tipos** - Validación de tipos estáticos
5. **Escaneo de Seguridad** - Detección de vulnerabilidades
6. **Testing** - Pruebas unitarias y de integración

---

## Herramientas Utilizadas

| Herramienta | Propósito | Configuración |
|-------------|-----------|---------------|
| **Ruff** | Linting + Formateo (reemplaza black, isort, flake8) | `pyproject.toml` |
| **Mypy** | Verificación de tipos | `pyproject.toml` |
| **Bandit** | Escaneo de seguridad | `pyproject.toml` |
| **Pytest** | Framework de testing | `pyproject.toml` |
| **Pre-commit** | Automatización de hooks de git | `.pre-commit-config.yaml` |
| **Gitleaks** | Detección de secretos | `.pre-commit-config.yaml` |
| **Markdownlint** | Linting de Markdown | `.pre-commit-config.yaml` |
| **Hadolint** | Linting de Dockerfile | `.pre-commit-config.yaml` |

---

## Inicio Rápido

### 1. Instalar Pre-commit Hooks

```bash
# Instalar pre-commit
uv tool install pre-commit

# Instalar hooks en tu repositorio local
pre-commit install

# Ejecutar hooks manualmente en todos los archivos
pre-commit run --all-files
```

### 2. Instalar Dependencias de Desarrollo

```bash
# Para API
cd src/lus_laboris_api
uv sync --extra dev

# Para Processing
cd src/processing
uv sync --extra dev

# Para Utils
cd utils
uv sync --extra dev
```

### 3. Ejecutar Verificaciones de Calidad Localmente

```bash
# Lint con ruff
uv run ruff check .

# Formatear con ruff
uv run ruff format .

# Verificar tipos con mypy
uv run mypy .

# Escaneo de seguridad con bandit
uv run bandit -r . -c pyproject.toml

# Ejecutar pruebas
uv run pytest tests/ -v --cov
```

---

## Pre-commit Hooks

El archivo `.pre-commit-config.yaml` configura los siguientes hooks:

### Verificaciones Generales de Archivos

- ✅ Eliminar espacios en blanco al final
- ✅ Arreglar fin de archivos
- ✅ Verificar sintaxis YAML
- ✅ Verificar sintaxis JSON
- ✅ Verificar sintaxis TOML
- ✅ Detectar archivos grandes (>1MB)
- ✅ Detectar conflictos de merge
- ✅ Detectar claves privadas
- ✅ Arreglar finales de línea (LF)
- ✅ Verificar docstrings
- ✅ Detectar declaraciones de debug

### Calidad de Código Python

- ✅ **Ruff linter** - Linter rápido de Python
- ✅ **Ruff formatter** - Formateador rápido de Python
- ✅ **Mypy** - Verificación de tipos
- ✅ **Bandit** - Escaneo de vulnerabilidades de seguridad

### Seguridad

- ✅ **Gitleaks** - Detectar secretos y credenciales
- ✅ **Bandit** - Problemas de seguridad en Python

### Documentación

- ✅ **Markdownlint** - Linting de archivos Markdown
- ✅ **YAML formatter** - Formateo de archivos YAML

### Docker

- ✅ **Hadolint** - Mejores prácticas de Dockerfile

---

## Workflow de GitHub Actions

El workflow `code-quality.yml` se ejecuta automáticamente en:

- Push a cualquier rama (afectando archivos Python, YAML o Markdown)
- Pull requests a cualquier rama

### Jobs Ejecutados

1. **Pre-commit** - Ejecuta todos los hooks de pre-commit
2. **Lint API** - Lintea código de API con ruff
3. **Lint Processing** - Lintea scripts de procesamiento con ruff
4. **Lint Utils** - Lintea scripts de utilidad con ruff
5. **Security Scan** - Ejecuta verificaciones de seguridad con bandit
6. **Type Check** - Ejecuta verificación de tipos con mypy
7. **Test API** - Ejecuta pytest con cobertura
8. **Summary** - Genera reporte de calidad

### Ver Resultados

- Revisa la pestaña **Actions** en GitHub
- Ver logs detallados de cada job
- Descargar artefactos (reportes de cobertura, reportes de seguridad)

---

## Configuración de Estilo de Código

### Configuración de Ruff

**Longitud de Línea:** 100 caracteres
**Versión de Python:** 3.13+
**Estilo de Comillas:** Comillas dobles

**Reglas Habilitadas:**

- E, W: pycodestyle
- F: pyflakes
- I: isort (ordenamiento de imports)
- N: pep8-naming
- UP: pyupgrade
- B: flake8-bugbear
- C4: flake8-comprehensions
- Y muchas más...

**Auto-fix:** Habilitado para la mayoría de reglas

### Ejemplo

```python
# Antes de ruff
import os
import sys
from typing import Dict,List
def mi_funcion(x,y,z):
    return x+y+z

# Después de ruff
import os
import sys
from typing import Dict, List


def mi_funcion(x: int, y: int, z: int) -> int:
    return x + y + z
```

---

## Verificación de Tipos con Mypy

Mypy está configurado para:

- ✅ Advertir sobre problemas de tipo de retorno
- ✅ Verificar definiciones sin tipos
- ✅ Advertir sobre casts redundantes
- ✅ Advertir sobre ignores no usados
- ✅ Verificar código inalcanzable
- ✅ Aplicar igualdad estricta

**Nota:** La verificación de tipos no es estricta por defecto para permitir adopción gradual.

### Agregar Type Hints

```python
# Sin type hints
def procesar_datos(datos):
    return datos.upper()

# Con type hints
def procesar_datos(datos: str) -> str:
    return datos.upper()
```

---

## Escaneo de Seguridad

### Bandit

Escanea problemas comunes de seguridad:

- Vulnerabilidades de inyección SQL
- Contraseñas hardcodeadas
- Uso de funciones inseguras
- Criptografía débil
- Y más...

### Gitleaks

Detecta secretos en el código:

- Claves API
- Contraseñas
- Claves privadas
- Tokens
- Credenciales

**Importante:** Gitleaks se ejecuta en todos los commits para prevenir fugas de secretos.

---

## Estrategia de Testing

### Estructura de Tests

```text
tests/
├── unit/                    # Pruebas unitarias (rápidas, aisladas)
│   ├── test_rag_service.py
│   ├── test_qdrant_service.py
│   └── test_auth.py
├── integration/             # Pruebas de integración (más lentas, con dependencias)
│   ├── test_api_endpoints.py
│   └── test_vectorstore.py
└── conftest.py             # Fixtures y configuración de pytest
```

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
uv run pytest

# Ejecutar con cobertura
uv run pytest --cov=. --cov-report=html

# Ejecutar archivo de prueba específico
uv run pytest tests/unit/test_rag_service.py

# Ejecutar pruebas por marcador
uv run pytest -m unit          # Solo pruebas unitarias
uv run pytest -m "not slow"    # Saltar pruebas lentas
```

### Escribir Pruebas

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## Reportes de Cobertura

Los reportes de cobertura se generan automáticamente:

- **Terminal:** Resumen en consola
- **HTML:** Reporte detallado en `htmlcov/`
- **XML:** Para integración CI/CD

### Ver Cobertura

```bash
# Generar reporte HTML
uv run pytest --cov=. --cov-report=html

# Abrir en navegador
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Integración de Workflow

### Desarrollo Local

```bash
# 1. Hacer cambios al código
vim src/lus_laboris_api/api/endpoints/rag.py

# 2. Ejecutar pre-commit (automático en git commit)
git add .
git commit -m "feat: agregar nueva característica"
# Pre-commit se ejecuta automáticamente

# 3. Si pre-commit falla, corregir problemas y reintentar
ruff check --fix .
git add .
git commit -m "feat: agregar nueva característica"
```

### Pipeline CI/CD

```text
Push/PR → GitHub Actions Activado
  ↓
Pre-commit Hooks (todos los archivos)
  ↓
Jobs Paralelos:
  ├─ Lint API
  ├─ Lint Processing
  ├─ Lint Utils
  ├─ Escaneo de Seguridad
  ├─ Verificación de Tipos
  └─ Pruebas
  ↓
Resumen de Calidad
  ↓
✅ Pasa → Merge permitido
❌ Falla → Corrección requerida
```

---

## Puertas de Calidad

### Requisitos Mínimos

- ✅ Todos los hooks de pre-commit pasan
- ✅ Sin errores de linting (ruff)
- ✅ Sin vulnerabilidades de seguridad (bandit)
- ✅ Sin secretos detectados (gitleaks)
- ✅ Todas las pruebas pasan (pytest)
- ⚠️ Advertencias de verificación de tipos permitidas (adopción gradual)

### Objetivos Recomendados

- 📊 Cobertura de pruebas: >80%
- 🔒 Puntuación de seguridad: Grado A
- 📝 Cobertura de docstrings: >70%
- 🎨 Complejidad de código: <10 (ciclomática)

---

## Comandos Comunes

### Linting

```bash
# Verificar problemas
uv run ruff check .

# Corregir problemas auto-corregibles
uv run ruff check --fix .

# Verificar archivo específico
uv run ruff check src/lus_laboris_api/api/main.py
```

### Formateo

```bash
# Verificar formateo
uv run ruff format --check .

# Aplicar formateo
uv run ruff format .
```

### Verificación de Tipos

```bash
# Verificar tipos
uv run mypy .

# Verificar módulo específico
uv run mypy src/lus_laboris_api/api/
```

### Seguridad

```bash
# Ejecutar escaneo de seguridad
uv run bandit -r src/ -c pyproject.toml

# Generar reporte JSON
uv run bandit -r src/ -c pyproject.toml -f json -o reporte-seguridad.json
```

### Testing

```bash
# Ejecutar todas las pruebas
uv run pytest

# Ejecutar con salida verbose
uv run pytest -v

# Ejecutar con cobertura
uv run pytest --cov=. --cov-report=term-missing

# Ejecutar prueba específica
uv run pytest tests/unit/test_rag_service.py::test_funcion_especifica
```

---

## Mejores Prácticas

### 1. Hacer Commits Frecuentes

- Hacer commits pequeños y enfocados
- Dejar que pre-commit detecte problemas temprano

### 2. Corregir Problemas Inmediatamente

- No saltarse los hooks de pre-commit
- Atender errores de linting antes de hacer push

### 3. Escribir Pruebas

- Agregar pruebas para nuevas características
- Mantener cobertura de pruebas

### 4. Usar Type Hints

- Agregar type hints a firmas de funciones
- Ayuda a detectar bugs temprano

### 5. Revisar Advertencias de Seguridad

- Tomar en serio las advertencias de bandit
- Nunca hacer commit de secretos

### 6. Mantener Dependencias Actualizadas

- Actualizar dependencias regularmente
- Verificar vulnerabilidades de seguridad

---

## Solución de Problemas

### Hook de Pre-commit Falla

```bash
# Actualizar hooks
pre-commit autoupdate

# Limpiar caché
pre-commit clean

# Reinstalar hooks
pre-commit uninstall
pre-commit install
```

### Problemas con Ruff

```bash
# Mostrar error detallado
uv run ruff check --show-source .

# Ignorar regla específica para una línea
# ruff: noqa: E501

# Ignorar regla específica para un archivo
# Agregar a pyproject.toml per-file-ignores
```

### Errores de Mypy

```bash
# Ignorar imports faltantes
# type: ignore[import]

# Saltar verificación de tipos para una función
# type: ignore
```

---

## Recursos Adicionales

- [Documentación de Ruff](https://docs.astral.sh/ruff/)
- [Documentación de Mypy](https://mypy.readthedocs.io/)
- [Documentación de Bandit](https://bandit.readthedocs.io/)
- [Documentación de Pytest](https://docs.pytest.org/)
- [Documentación de Pre-commit](https://pre-commit.com/)
