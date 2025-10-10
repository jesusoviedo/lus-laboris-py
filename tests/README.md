<div align="center">

**Language / Idioma:**
[🇺🇸 English](#tests) | [🇪🇸 Español](#pruebas)

</div>

---

# Tests

This folder contains unit and integration tests for the project.

## Structure

```text
tests/
├── conftest.py              # Pytest fixtures and configuration
├── unit/                    # Unit tests (fast, isolated)
│   └── test_health_endpoints.py
└── integration/             # Integration tests (with dependencies)
    └── (to be added)
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_health_endpoints.py

# Run by marker
uv run pytest -m unit
uv run pytest -m integration
```

## Writing Tests

See [Code Quality Guide](../docs/code_quality_guide.md) for detailed testing guidelines.

### Example

```python
def test_example(api_client):
    response = api_client.get("/api/health")
    assert response.status_code == 200
```

## Test Markers

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests requiring external services
- `@pytest.mark.slow` - Slow-running tests

---

# Pruebas

Esta carpeta contiene pruebas unitarias y de integración para el proyecto.

## Estructura

```text
tests/
├── conftest.py              # Fixtures y configuración de pytest
├── unit/                    # Pruebas unitarias (rápidas, aisladas)
│   └── test_health_endpoints.py
└── integration/             # Pruebas de integración (con dependencias)
    └── (por agregar)
```

## Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
uv run pytest

# Ejecutar con cobertura
uv run pytest --cov=. --cov-report=html

# Ejecutar archivo de prueba específico
uv run pytest tests/unit/test_health_endpoints.py

# Ejecutar por marcador
uv run pytest -m unit
uv run pytest -m integration
```

## Escribir Pruebas

Ver [Guía de Calidad de Código](../docs/code_quality_guide.md) para guías detalladas de testing.

### Ejemplo

```python
def test_ejemplo(api_client):
    response = api_client.get("/api/health")
    assert response.status_code == 200
```

## Marcadores de Pruebas

- `@pytest.mark.unit` - Pruebas unitarias rápidas y aisladas
- `@pytest.mark.integration` - Pruebas que requieren servicios externos
- `@pytest.mark.slow` - Pruebas de ejecución lenta
