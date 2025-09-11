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

Para una explicación detallada sobre el uso de GitHub Actions en este proyecto, consulta la guía:
- [docs/github_actions_guide.md](../../docs/github_actions_guide.md)
