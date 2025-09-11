<div align="center">

**Language / Idioma:**
[🇺🇸 English](#github-actions-workflows) | [🇪🇸 Español](#workflows-de-github-actions)

</div>

---

# GitHub Actions Workflows

This folder contains configuration files (`.yml`) for GitHub Actions workflows that automate project tasks.

A **workflow** is an automated process defined as code, which runs on GitHub's infrastructure in response to specific events (such as code pushes, pull requests, or manual triggers). Workflows are used for tasks like testing, building, deploying, or automating maintenance.

## Existing Workflows

- **docker-processing-build-publish.yml**: 
Automates the build and publishing of the Docker image for the legal text processing service (`src/processing` folder).
  - Triggers manually or when key files change (`Dockerfile`, `extract_law_text.py`, `pyproject.toml`, `.python-version`).
  - Uses repository secrets for Docker Hub credentials and the image name.
  - Tags the image with both `latest` and the current date (`YYYYMMDD`).
  - Pushes both tags to Docker Hub.

- **terraform-apply-on-tf-change.yml**:
Runs Terraform automatically when any `.tf` file changes in the `terraform/` folder (or its subfolders).
  - Triggers on push events affecting any Terraform file inside `terraform/`.
  - Sets up Google Cloud authentication using a service account key stored as a secret.
  - Generates the required `.env` file and runs the menu script to create `terraform.tfvars`.
  - Executes `terraform init`, `plan`, and `apply` to update the infrastructure.
  - All required variables are passed as GitHub secrets or environment variables.

For a detailed explanation of how GitHub Actions work in this project, see the guide:
- [docs/github_actions_guide.md](../../docs/github_actions_guide.md)

---

# Workflows de GitHub Actions

Esta carpeta contiene los archivos de configuración (`.yml`) para los workflows de GitHub Actions que automatizan tareas del proyecto.

Un **workflow** es un proceso automatizado definido como código, que se ejecuta en la infraestructura de GitHub en respuesta a eventos específicos (como push, pull request o ejecución manual). Los workflows se utilizan para tareas como pruebas, construcción, despliegue o automatización de mantenimiento.

## Workflows existentes

- **docker-processing-build-publish.yml**: 
Automatiza la construcción y publicación de la imagen Docker para el procesamiento de texto legal (carpeta `src/processing`).
  - Se ejecuta manualmente o cuando se modifican archivos clave (`Dockerfile`, `extract_law_text.py`, `pyproject.toml`, `.python-version`).
  - Usa secrets del repositorio para las credenciales de Docker Hub y el nombre de la imagen.
  - Etiqueta la imagen con `latest` y con la fecha (`YYYYMMDD`).
  - Sube ambas etiquetas a Docker Hub.

- **terraform-apply-on-tf-change.yml**:
Ejecuta Terraform automáticamente cuando se modifica cualquier archivo `.tf` dentro de la carpeta `terraform/` (o sus subcarpetas).
  - Se activa ante un push que afecte archivos de Terraform en `terraform/`.
  - Configura la autenticación de Google Cloud usando una service account almacenada como secret.
  - Genera el archivo `.env` necesario y ejecuta el script de menú para crear `terraform.tfvars`.
  - Ejecuta `terraform init`, `plan` y `apply` para actualizar la infraestructura.
  - Todas las variables requeridas se pasan como secrets de GitHub o variables de entorno.

Para una explicación detallada sobre el uso de GitHub Actions en este proyecto, consulta la guía:
- [docs/github_actions_guide.md](../../docs/github_actions_guide.md)

