<div align="center">

**Language / Idioma:**
[🇺🇸 English](#tests) | [🇪🇸 Español](#pruebas)

</div>

---

# Tests

This directory contains unit and integration tests for the RAG system.

## Directory Structure

```text
tests/
├── unit/                           # Unit tests (29 tests)
│   ├── test_health_endpoints.py    # 11 tests (health checks)
│   ├── test_vectorstore_endpoints.py # 10 tests (data & collections)
│   ├── test_rag_endpoints.py       # 4 tests (RAG queries)
│   └── test_status_endpoints.py    # 4 tests (status & root)
├── integration/                    # Integration tests
│   └── integration_test_e2e.sh     # End-to-end test script
├── conftest.py                     # Pytest fixtures & mocks
├── pyproject.toml                  # Test dependencies & config
└── README.md                       # This file
```

## Unit Tests

**Coverage**: 29 tests covering 24/24 endpoints (100%)

**Run all unit tests:**

```bash
cd tests
uv run pytest unit/ -v
```

**Run specific test file:**

```bash
cd tests
uv run pytest unit/test_rag_endpoints.py -v
```

**Run specific test:**

```bash
cd tests
uv run pytest unit/test_rag_endpoints.py::test_ask_question_returns_200 -v
```

### Test Categories

**Health Endpoints** (11 tests)

- `GET /api/health/` - Main health check
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/qdrant` - Qdrant status
- `GET /api/health/gcp` - GCP status
- `GET /api/health/embeddings` - Embedding service status
- `GET /api/health/reranking` - Reranking service status
- `GET /api/health/rag` - RAG service status
- `GET /api/health/phoenix` - Phoenix monitoring status
- `GET /docs` - API documentation

**Status Endpoints** (4 tests)

- `GET /` - Root endpoint
- `GET /api/status` - Service status

**Vectorstore Endpoints** (10 tests)

- `GET /api/data/collections` - List collections
- `GET /api/data/collections/{name}` - Get collection info
- `DELETE /api/data/collections/{name}` - Delete collection
- `POST /api/data/load-to-vectorstore-local` - Load data from local
- `POST /api/data/load-to-vectorstore-gcp` - Load data from GCP
- `GET /api/data/jobs` - List background jobs

**RAG Endpoints** (4 tests)

- `POST /api/rag/ask` - Ask questions
- Pydantic validation (min/max length)
- Error handling

### Features

✅ **Mock external services**: No need for Qdrant, GCP, or LLMs  
✅ **Fast execution**: ~26 seconds for 29 tests  
✅ **Isolated tests**: No dependencies between tests  
✅ **Comprehensive**: Status codes, JSON structure, error cases  
✅ **100% endpoint coverage**: All 24 endpoints tested  
✅ **Clean output**: 0 warnings

## Integration Tests

### `integration_test_e2e.sh` - End-to-End Integration Test

Complete end-to-end flow testing all system components together.

**What it does:**

1. ✅ **Services**: Starts Qdrant and Phoenix with `docker compose up -d`
2. ✅ **Data extraction**: Runs `extract_law_text.py --mode local` (with Phoenix tracing)
3. ✅ **API**: Starts FastAPI API with `docker compose up -d`
4. ✅ **Authentication**: Generates JWT token
5. ✅ **Vectorization**: POST to `/api/data/load-to-vectorstore-local`
6. ✅ **Polling**: Checks job status via `GET /api/data/jobs`
7. ✅ **RAG Query**: POST to `/api/rag/ask` with test question
8. ✅ **Verification**: 6 automatic checks on response
9. ✅ **Cleanup**: Automatic resource cleanup (trap)

**Usage:**

```bash
# From project root
./tests/integration/integration_test_e2e.sh

# Or from tests directory
cd tests
./integration/integration_test_e2e.sh
```

**Prerequisites:**

- Docker running
- `jq` installed (JSON parser) - Install: `sudo apt-get install jq` (Ubuntu) or `brew install jq` (macOS)
- Configured `.env` file
- JWT keys (auto-generated if missing)
- UV installed

**Duration:** ~3-5 minutes

**Verifications:**

1. Success flag in response
2. Non-empty LLM answer
3. Documents retrieved from Qdrant
4. Document structure validation
5. Session ID for tracking
6. Relevant keywords in answer

For detailed information about the integration test, check the script's header comments or run it with `-h` flag.

> **⚠️ Important Note**: The integration tests may be updated and improved in the coming days. We recommend checking this folder regularly for updates and enhancements to the test suite. Always review the latest version of the integration test script before running it.

## Configuration

### Pytest Settings

The `pyproject.toml` file contains pytest configuration:

```toml
[tool.pytest.ini_options]
# Filter out deprecation warnings from external libraries
filterwarnings = [
    "ignore::pydantic.warnings.PydanticDeprecatedSince20",
    "ignore::pydantic.warnings.PydanticDeprecatedSince212",
]

# Register custom pytest marks
markers = [
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "slow: marks tests as slow",
]
```

### Using Marks

```bash
# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Exclude slow tests
pytest -m "not slow"
```

## Debugging

### View Service Logs

```bash
# Qdrant
cd services/vectordb && docker compose logs -f

# Phoenix
cd services/monitoring && docker compose logs -f

# API
cd src/lus_laboris_api && docker compose logs -f
```

### Manual Service Checks

```bash
# Health checks
curl http://localhost:6333          # Qdrant
curl http://localhost:6006          # Phoenix  
curl http://localhost:8000/api/health  # API

# Collections
curl http://localhost:6333/collections
```

## CI/CD Integration

These tests are designed for GitHub Actions integration:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: |
          cd tests
          uv run pytest unit/ -v

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: ./tests/integration/integration_test_e2e.sh
        timeout-minutes: 10
```

## Contributing

To add new tests:

1. Create test file in appropriate directory (`unit/` or `integration/`)
2. Use fixtures from `conftest.py` for mocking
3. Follow naming convention: `test_*.py`
4. Update this README with new test information

---

# Pruebas

Este directorio contiene pruebas unitarias e de integración para el sistema RAG.

## Estructura de Directorios

```text
tests/
├── unit/                           # Pruebas unitarias (29 tests)
│   ├── test_health_endpoints.py    # 11 tests (health checks)
│   ├── test_vectorstore_endpoints.py # 10 tests (datos & colecciones)
│   ├── test_rag_endpoints.py       # 4 tests (consultas RAG)
│   └── test_status_endpoints.py    # 4 tests (status & raíz)
├── integration/                    # Pruebas de integración
│   └── integration_test_e2e.sh     # Script de prueba end-to-end
├── conftest.py                     # Fixtures & mocks de pytest
├── pyproject.toml                  # Dependencias & configuración
└── README.md                       # Este archivo
```

## Pruebas Unitarias

**Cobertura**: 29 tests cubriendo 24/24 endpoints (100%)

**Ejecutar todas las pruebas unitarias:**

```bash
cd tests
uv run pytest unit/ -v
```

**Ejecutar archivo de test específico:**

```bash
cd tests
uv run pytest unit/test_rag_endpoints.py -v
```

**Ejecutar test específico:**

```bash
cd tests
uv run pytest unit/test_rag_endpoints.py::test_ask_question_returns_200 -v
```

### Categorías de Tests

**Endpoints de Health** (11 tests)

- `GET /api/health/` - Health check principal
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/qdrant` - Estado de Qdrant
- `GET /api/health/gcp` - Estado de GCP
- `GET /api/health/embeddings` - Estado del servicio de embeddings
- `GET /api/health/reranking` - Estado del servicio de reranking
- `GET /api/health/rag` - Estado del servicio RAG
- `GET /api/health/phoenix` - Estado del monitoreo Phoenix
- `GET /docs` - Documentación de la API

**Endpoints de Status** (4 tests)

- `GET /` - Endpoint raíz
- `GET /api/status` - Estado de servicios

**Endpoints de Vectorstore** (10 tests)

- `GET /api/data/collections` - Listar colecciones
- `GET /api/data/collections/{name}` - Info de colección
- `DELETE /api/data/collections/{name}` - Eliminar colección
- `POST /api/data/load-to-vectorstore-local` - Cargar datos desde local
- `POST /api/data/load-to-vectorstore-gcp` - Cargar datos desde GCP
- `GET /api/data/jobs` - Listar jobs en background

**Endpoints de RAG** (4 tests)

- `POST /api/rag/ask` - Hacer preguntas
- Validación Pydantic (longitud min/max)
- Manejo de errores

### Características

✅ **Mock de servicios externos**: No requiere Qdrant, GCP, o LLMs  
✅ **Ejecución rápida**: ~26 segundos para 29 tests  
✅ **Tests aislados**: Sin dependencias entre tests  
✅ **Completo**: Códigos de estado, estructura JSON, casos de error  
✅ **100% de cobertura**: Todos los 24 endpoints testeados  
✅ **Output limpio**: 0 warnings

## Pruebas de Integración

### `integration_test_e2e.sh` - Prueba de Integración End-to-End

Flujo completo end-to-end que prueba todos los componentes del sistema juntos.

**Qué hace:**

1. ✅ **Servicios**: Inicia Qdrant y Phoenix con `docker compose up -d`
2. ✅ **Extracción de datos**: Ejecuta `extract_law_text.py --mode local` (con tracing a Phoenix)
3. ✅ **API**: Inicia la API FastAPI con `docker compose up -d`
4. ✅ **Autenticación**: Genera token JWT
5. ✅ **Vectorización**: POST a `/api/data/load-to-vectorstore-local`
6. ✅ **Polling**: Verifica estado del job vía `GET /api/data/jobs`
7. ✅ **Consulta RAG**: POST a `/api/rag/ask` con pregunta de prueba
8. ✅ **Verificación**: 6 verificaciones automáticas en la respuesta
9. ✅ **Cleanup**: Limpieza automática de recursos (trap)

**Uso:**

```bash
# Desde la raíz del proyecto
./tests/integration/integration_test_e2e.sh

# O desde el directorio tests
cd tests
./integration/integration_test_e2e.sh
```

**Prerequisitos:**

- Docker ejecutándose
- `jq` instalado (parser JSON) - Instalar: `sudo apt-get install jq` (Ubuntu) o `brew install jq` (macOS)
- Archivo `.env` configurado
- Claves JWT (se auto-generan si faltan)
- UV instalado

**Duración:** ~3-5 minutos

**Verificaciones:**

1. Flag de success en respuesta
2. Respuesta del LLM no vacía
3. Documentos recuperados de Qdrant
4. Validación de estructura de documentos
5. Session ID para tracking
6. Keywords relevantes en respuesta

Para información detallada sobre el test de integración, revisar los comentarios del header del script o ejecutarlo con la flag `-h`.

> **⚠️ Nota Importante**: Las pruebas de integración pueden ser actualizadas y mejoradas en los próximos días. Recomendamos verificar esta carpeta regularmente para actualizaciones y mejoras en la suite de tests. Siempre revisa la última versión del script de prueba de integración antes de ejecutarlo.

## Configuración

### Configuración de Pytest

El archivo `pyproject.toml` contiene la configuración de pytest:

```toml
[tool.pytest.ini_options]
# Filtrar warnings de deprecación de librerías externas
filterwarnings = [
    "ignore::pydantic.warnings.PydanticDeprecatedSince20",
    "ignore::pydantic.warnings.PydanticDeprecatedSince212",
]

# Registrar marks personalizados de pytest
markers = [
    "integration: marca tests como de integración",
    "unit: marca tests como unitarios",
    "slow: marca tests como lentos",
]
```

### Usando Marks

```bash
# Ejecutar solo tests de integración
pytest -m integration

# Ejecutar solo tests unitarios
pytest -m unit

# Excluir tests lentos
pytest -m "not slow"
```

## Debugging

### Ver Logs de Servicios

```bash
# Qdrant
cd services/vectordb && docker compose logs -f

# Phoenix
cd services/monitoring && docker compose logs -f

# API
cd src/lus_laboris_api && docker compose logs -f
```

### Verificaciones Manuales de Servicios

```bash
# Health checks
curl http://localhost:6333          # Qdrant
curl http://localhost:6006          # Phoenix  
curl http://localhost:8000/api/health  # API

# Colecciones
curl http://localhost:6333/collections
```

## Integración CI/CD

Estos tests están diseñados para integrarse con GitHub Actions:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: |
          cd tests
          uv run pytest unit/ -v

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: ./tests/integration/integration_test_e2e.sh
        timeout-minutes: 10
```

## Contribuir

Para agregar nuevos tests:

1. Crear archivo de test en el directorio apropiado (`unit/` o `integration/`)
2. Usar fixtures de `conftest.py` para mocking
3. Seguir convención de nombres: `test_*.py`
4. Actualizar este README con información del nuevo test
