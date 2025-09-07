# Workflows de GitHub Actions

Esta carpeta contiene los archivos de configuración (`.yml`) para los workflows de GitHub Actions.

## ¿Qué es un workflow?
Un workflow es un proceso automatizado que se ejecuta en GitHub Actions para tareas como:
- Pruebas automáticas
- Despliegue continuo (CD)
- Integración continua (CI)
- Automatización de tareas de mantenimiento

## ¿Cómo funciona?
Cada archivo YAML en esta carpeta define un workflow. GitHub ejecuta estos workflows automáticamente según los eventos configurados (por ejemplo, push, pull request, release, etc).

## Ejemplo de uso
Puedes agregar un archivo como `ci.yml` para ejecutar pruebas automáticamente en cada push:

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest
```
