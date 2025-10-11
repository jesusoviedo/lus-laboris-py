<div align="center">

**Language / Idioma:**
[🇺🇸 English](#github-actions-workflows) | [🇪🇸 Español](#workflows-de-github-actions)

</div>

---

# GitHub Actions Workflows

This folder contains configuration files (`.yml`) for GitHub Actions workflows that automate project tasks.

A **workflow** is an automated process defined as code, which runs on GitHub's infrastructure in response to specific events (such as code pushes, pull requests, or manual triggers). Workflows are used for tasks like testing, building, deploying, or automating maintenance.

## Local Development Scripts

- **act_menu.sh**:
Interactive script to run GitHub Actions workflows locally using `act`.
  - Must be executed from `.github/workflows/` directory.
  - Reads environment variables from the project root `.env` file.
  - Automatically handles Docker Hub login and GCP credentials.
  - Supports all workflows with proper variable mapping and validation.
  - Provides a user-friendly menu interface in Spanish.
  - Hides sensitive values in command preview for security.
  - Includes configurable list of secret variables for better security management.

## Existing Workflows

- **code-quality.yml**:
Validates code quality, style, and security across the entire project.
  - Triggers on push/PR when Python files, configs, or documentation change.
  - Runs pre-commit hooks (ruff, bandit, mypy, trailing-whitespace, etc.).
  - Lints API, processing, and utils code separately with ruff.
  - Performs security scanning with bandit.
  - Type checks with mypy (pragmatic configuration to avoid false positives).
  - Runs API tests with pytest and generates coverage reports.
  - Provides a comprehensive quality summary with all job results.

- **docker-processing-build-publish.yml**:
Automates the build and publishing of the Docker image for the legal text processing service (`src/processing` folder).
  - Triggers manually or when key files change (`Dockerfile`, `extract_law_text.py`, `pyproject.toml`, `.python-version`).
  - Uses repository secrets for Docker Hub credentials and the image name.
  - Tags the image with both `latest` and the current date (`YYYYMMDD`).
  - Pushes both tags to Docker Hub.

- **docker-api-build-publish.yml**:
Automates the build and publishing of the Docker image for the FastAPI service (`src/lus_laboris_api` folder).
  - Triggers manually or when key files change (`Dockerfile`, `pyproject.toml`, `uv.lock`, `api/**`).
  - Uses repository secrets for Docker Hub credentials and the image name.
  - Tags the image with both `latest` and the current date (`YYYYMMDD`).
  - Pushes both tags to Docker Hub.
  - Outputs detailed information about the created images for easy usage.

- **terraform-apply-on-tf-change.yml**:
Runs Terraform automatically when any `.tf` file changes in the `terraform/` folder (or its subfolders).
  - Triggers on push events affecting any Terraform file inside `terraform/`.
  - Sets up Google Cloud authentication using a service account key stored as a secret.
  - Generates the required `.env` file and runs the menu script to create `terraform.tfvars`.
  - Executes `terraform init`, `plan`, and `apply` to update the infrastructure.
  - All required variables are passed as GitHub secrets or environment variables.

- **deploy-qdrant.yml**:
Deploys Qdrant vector database to a Compute Engine VM instance.
  - Triggers when files in `src/vectorstore/` or `terraform/modules/compute_engine/` change.
  - Can also be triggered manually via `workflow_dispatch`.
  - Gets VM details using the VM name from Terraform outputs.
  - Installs Docker and Docker Compose on the VM.
  - Copies Docker Compose files and creates environment configuration.
  - Starts Qdrant containers and verifies deployment.
  - Uses repository secrets for GCP project configuration and Qdrant API key.

## Local Testing with act

To test workflows locally before pushing changes, use the interactive script (run from the current directory):

```bash
bash act_menu.sh
```

For detailed information about act installation and usage, see:

- [docs/act_guide.md](../../docs/act_guide.md)

For a detailed explanation of how GitHub Actions work in this project, see the guide:

- [docs/github_actions_guide.md](../../docs/github_actions_guide.md)

---

# Workflows de GitHub Actions

Esta carpeta contiene los archivos de configuración (`.yml`) para los workflows de GitHub Actions que automatizan tareas del proyecto.

Un **workflow** es un proceso automatizado definido como código, que se ejecuta en la infraestructura de GitHub en respuesta a eventos específicos (como push, pull request o ejecución manual). Los workflows se utilizan para tareas como pruebas, construcción, despliegue o automatización de mantenimiento.

## Scripts de desarrollo local

- **act_menu.sh**:
Script interactivo para ejecutar workflows de GitHub Actions localmente usando `act`.
  - Debe ejecutarse desde el directorio `.github/workflows/`.
  - Lee las variables de entorno desde el archivo `.env` en la raíz del proyecto.
  - Maneja automáticamente el login a Docker Hub y las credenciales de GCP.
  - Soporta todos los workflows con mapeo correcto de variables y validación.
  - Proporciona una interfaz de menú amigable en español.
  - Oculta valores sensibles en la vista previa del comando por seguridad.
  - Incluye lista configurable de variables secretas para mejor gestión de seguridad.

## Workflows existentes

- **code-quality.yml**:
Valida la calidad de código, estilo y seguridad en todo el proyecto.
  - Se ejecuta en push/PR cuando cambian archivos Python, configuraciones o documentación.
  - Ejecuta hooks de pre-commit (ruff, bandit, mypy, trailing-whitespace, etc.).
  - Hace linting de API, processing y utils por separado con ruff.
  - Realiza escaneo de seguridad con bandit.
  - Chequeo de tipos con mypy (configuración pragmática para evitar falsos positivos).
  - Ejecuta tests de la API con pytest y genera reportes de cobertura.
  - Proporciona un resumen completo de calidad con todos los resultados de jobs.

- **docker-processing-build-publish.yml**:
Automatiza la construcción y publicación de la imagen Docker para el procesamiento de texto legal (carpeta `src/processing`).
  - Se ejecuta manualmente o cuando se modifican archivos clave (`Dockerfile`, `extract_law_text.py`, `pyproject.toml`, `.python-version`).
  - Usa secrets del repositorio para las credenciales de Docker Hub y el nombre de la imagen.
  - Etiqueta la imagen con `latest` y con la fecha (`YYYYMMDD`).
  - Sube ambas etiquetas a Docker Hub.

- **docker-api-build-publish.yml**:
Automatiza la construcción y publicación de la imagen Docker para el servicio FastAPI (carpeta `src/lus_laboris_api`).
  - Se ejecuta manualmente o cuando se modifican archivos clave (`Dockerfile`, `pyproject.toml`, `uv.lock`, `api/**`).
  - Usa secrets del repositorio para las credenciales de Docker Hub y el nombre de la imagen.
  - Etiqueta la imagen con `latest` y con la fecha (`YYYYMMDD`).
  - Sube ambas etiquetas a Docker Hub.
  - Muestra información detallada sobre las imágenes creadas para facilitar su uso.

- **terraform-apply-on-tf-change.yml**:
Ejecuta Terraform automáticamente cuando se modifica cualquier archivo `.tf` dentro de la carpeta `terraform/` (o sus subcarpetas).
  - Se activa ante un push que afecte archivos de Terraform en `terraform/`.
  - Configura la autenticación de Google Cloud usando una service account almacenada como secret.
  - Genera el archivo `.env` necesario y ejecuta el script de menú para crear `terraform.tfvars`.
  - Ejecuta `terraform init`, `plan` y `apply` para actualizar la infraestructura.
  - Todas las variables requeridas se pasan como secrets de GitHub o variables de entorno.

- **deploy-qdrant.yml**:
Despliega la base de datos vectorial Qdrant en una instancia de Compute Engine VM.
  - Se activa cuando se modifican archivos en `src/vectorstore/` o `terraform/modules/compute_engine/`.
  - También se puede activar manualmente mediante `workflow_dispatch`.
  - Obtiene detalles de la VM usando el nombre de la VM desde las salidas de Terraform.
  - Instala Docker y Docker Compose en la VM.
  - Copia archivos de Docker Compose y crea configuración de entorno.
  - Inicia contenedores de Qdrant y verifica el despliegue.
  - Usa secrets del repositorio para configuración del proyecto GCP y clave API de Qdrant.

## Pruebas locales con act

Para probar workflows localmente antes de hacer push de los cambios, usa el script interactivo (ejecutar desde el directorio actual):

```bash
bash act_menu.sh
```

Para información detallada sobre la instalación y uso de act, consulta:

- [docs/act_guide.md](../../docs/act_guide.md)

Para una explicación detallada sobre el uso de GitHub Actions en este proyecto, consulta la guía:

- [docs/github_actions_guide.md](../../docs/github_actions_guide.md)
