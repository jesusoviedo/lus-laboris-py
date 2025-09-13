# lus-laboris-py

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![Terraform](https://img.shields.io/badge/Terraform-844FBA?logo=terraform&logoColor=fff)](https://developer.hashicorp.com/terraform)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker--Compose-2496ED?logo=docker&logoColor=fff)](https://docs.docker.com/compose/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](https://docs.github.com/en/actions)

![DLT](https://img.shields.io/badge/DLT-FF6B35?style=for-the-badge&logo=data&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-FF6B35?style=for-the-badge&logo=qdrant&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
![Phoenix](https://img.shields.io/badge/Phoenix-FF7100?style=for-the-badge&logo=phoenixframework&logoColor=white)
![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)

[![Licencia MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)


[![Infra Provision](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-cd-terraform.yml/badge.svg)](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-cd-terraform.yml)


[![Build & Deploy Docker](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-cd-build-deploy-docker-image.yml/badge.svg)](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-cd-build-deploy-docker-image.yml)

[![Secrets Scan](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-sec-secrets-scan.yml/badge.svg)](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-sec-secrets-scan.yml)

[![Code Style & Quality](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-qa-pre-commit.yml/badge.svg)](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-qa-pre-commit.yml)


[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
 [![Database](https://img.shields.io/badge/Database-BigQuery-yellow?logo=googlecloud)](https://cloud.google.com/bigquery) [![Orchestration](https://img.shields.io/badge/Orchestration-Kestra-blueviolet?logo=apacheairflow)](https://kestra.io/) [![Transformation](https://img.shields.io/badge/Transformation-dbt-FF694B?logo=dbt)](https://www.getdbt.com/) [![Data Loading](https://img.shields.io/badge/Data%20Loader-dlt-32CD32)](https://github.com/duckdblabs/dlt) 







</div>

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#description) | [🇪🇸 Español](#descripción)

</div>

---

## Description

This project implements a RAG (Retrieval-Augmented Generation) application over Law Nº 213 that Establishes the Labor Code of Paraguay. The main workflow is:

- **Extraction**: Download and store the original law text.
- **Processing**: Use dlt and Python to clean, segment, and enrich the legal text.
- **Storage**: Save the processed file in a Google Cloud Storage (GGS) bucket.
- **Indexing**: Load the processed data into a Qdrant vector database, applying indexing models by language and area, and adding metadata for efficient filtering.
- **Retrieval & Response**: Use OpenAI as the LLM and a specialized prompt to answer user questions about the law, via a REST API built with FastAPI and Pydantic.
- **Evaluation**: Comprehensive evaluation of the RAG application, including prompts, indexing models, and the RAG system itself.
- **Monitoring**: Application and response monitoring using Phoenix.
- **Cloud Deployment**: Google Cloud Run is used both to run the batch process that loads Qdrant and to deploy the FastAPI API that extracts information from the vector database.
- **Automation**: GitHub Actions is used to automate key project processes such as testing, deployment, and CI tasks. See [Workflows README](.github/workflows/README.md) for details on automation.

The project is organized in folders such as:
- `data/raw/` — Original downloaded law
- `data/processed/` — Processed law ready for indexing
- `src/processing/` — Extraction and processing scripts
- `src/api/` — REST API with FastAPI
- `src/vectorstore/` — Scripts for loading and managing Qdrant
- `notebooks/` — Documentation and experiments
- `evaluation/` — Scripts and notebooks for RAG application evaluation
- `monitoring/` — Scripts and configuration for monitoring with Phoenix
- `deploy/` — Deployment and configuration files for Google Cloud Run
- `utils/` — Utility scripts for project management and automation
- `.github/workflows/` — GitHub Actions workflows for automation

## Project Structure

```
lus-laboris-py/
├── data/                   # Data directory
│   ├── raw/               # Original, unprocessed data
│   └── processed/         # Cleaned and processed data
├── deploy/                # Deployment and configuration files
├── evaluation/            # RAG application evaluation scripts
├── monitoring/            # Monitoring and observability scripts
├── notebooks/             # Jupyter notebooks for analysis
│   ├── 01_data_extraction.ipynb
│   ├── pyproject.toml
│   ├── README.md
│   └── uv.lock
├── src/                   # Main source code
│   ├── api/               # FastAPI REST API implementation
│   ├── core/              # Core functionalities and business logic
│   ├── processing/        # Data extraction and processing scripts
│   │   └── README.md      # Processing module documentation
│   └── vectorstore/       # Qdrant vector database scripts
├── tests/                 # Unit and integration tests
├── terraform/             # Infrastructure as Code
│   ├── modules/           # Reusable Terraform modules
│   │   ├── gcs/           # Google Cloud Storage module
│   │   │   └── README.md  # GCS module documentation
│   │   └── cloud_run_job/ # Cloud Run Job (batch) module
│   │       └── README.md  # Cloud Run Job module documentation
│   ├── main.tf            # Main configuration
│   ├── variables.tf       # Input variables
│   ├── providers.tf       # Provider configuration
│   ├── terraform.tfvars   # Variable values
│   ├── tf_menu.sh         # Interactive menu script
│   └── README.md          # Terraform documentation
├── utils/                 # Utility scripts and tools
│   ├── gcp_utils.py       # GCP utilities for bucket management
│   ├── pyproject.toml     # Dependencies for utils
│   └── README.md          # Utils documentation
├── docs/                  # Project documentation
│   ├── setup_gcp_project.md  # GCP setup guide
│   ├── uv_guide.md        # UV package manager guide
│   ├── docker_guide.md    # Docker guide (includes Docker, Compose, and Hub)
│   ├── github_actions_guide.md  # GitHub Actions guide
│   └── README.md          # Documentation index
├── .github/workflows/     # GitHub Actions workflows
│   └── act_menu.sh        # Interactive script for local workflow testing
├── LICENSE                # Project license
└── README.md              # This file
```

## Directory Overview

- **`data/`**: Stores all project data, with subdirectories for raw and processed files.
- **`deploy/`**: Contains deployment guides, Dockerfiles, and configuration files for Google Cloud.
- **`docs/`**: Complete project documentation, including setup and configuration guides. See especially [setup_gcp_project.md](docs/setup_gcp_project.md) and [terraform/README.md](terraform/README.md).
- **`evaluation/`**: Scripts and notebooks for evaluating the RAG application's performance.
- **`monitoring/`**: Scripts and configuration for application monitoring and observability.
- **`notebooks/`**: Jupyter notebooks for experimentation, analysis, and documentation.
- **`src/api/`**: FastAPI REST API implementation for exposing project functionalities. See [src/processing/README.md](src/processing/README.md) for processing details.
- **`src/core/`**: Core functionalities and business logic of the project.
- **`src/processing/`**: Scripts for data extraction, cleaning, and processing.
- **`src/vectorstore/`**: Scripts for loading, managing, and querying the Qdrant vector database.
- **`terraform/`**: Infrastructure as Code for managing Google Cloud Platform resources. See [terraform/README.md](terraform/README.md) for details.
- **`tests/`**: Unit and integration tests to ensure code quality and correctness.
- **`utils/`**: Utility scripts and tools for project management, including GCP bucket management for Terraform state.
- **`.github/workflows/`**: GitHub Actions workflows for automation, including `act_menu.sh` for local workflow testing.

## Features

- **Data Extraction**: Tools for extracting information from web sources
- **Data Analysis**: Jupyter notebooks for interactive analysis
- **REST API**: Web services with FastAPI for labor law queries
- **Processing**: Core functionalities for legal data processing
- **Vector Database**: Semantic storage and search with Qdrant
- **Infrastructure as Code**: Infrastructure management with Terraform
- **Monitoring**: Observability and tracking with Phoenix
- **Evaluation**: Metrics and performance analysis of the RAG system
- **Automation**: CI/CD and infrastructure workflows with GitHub Actions ([see workflows](.github/workflows/README.md))

## Requirements

- Python 3.13 (managed with [uv](docs/uv_guide.md); each submodule may have its own dependencies)
- Terraform (for infrastructure management)
- Google Cloud Platform (account and credentials)
- See [UV Guide](docs/uv_guide.md) for Python package management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jesusoviedo/lus-laboris-py.git
cd lus-laboris-py
```

2. Set up development environment:
   - See [UV Guide](docs/uv_guide.md) for Python package management (each submodule may have its own `pyproject.toml`)
   - See [Terraform Guide](terraform/README.md) for infrastructure setup

## Usage

### Local Development

#### Testing Workflows Locally

Use the interactive script to test GitHub Actions workflows locally:

```bash
cd .github/workflows/
bash act_menu.sh
```

For detailed act usage, see [act_guide.md](docs/act_guide.md).

#### Infrastructure Management

Use the interactive Terraform menu:

```bash
cd terraform/
bash tf_menu.sh
```

#### Docker Development

Build and test Docker images locally:

```bash
cd src/processing/
bash docker_build_push.sh
```

### Initial Setup

1. **Configure Google Cloud Platform**:
   - Follow the guide in [docs/setup_gcp_project.md](docs/setup_gcp_project.md)
   - Set up service account credentials

2. **Create the .env file at the project root**:
   - The following variables are required for Terraform and automation scripts:
     - `GCP_PROJECT_ID`
     - `GCP_REGION`
     - `GCP_BUCKET_NAME`
     - `GCP_CLOUD_RUN_BATCH_JOB_NAME`
     - `GCP_CLOUD_RUN_BATCH_SCHEDULE`
     - `GCP_CLOUD_RUN_BATCH_IMAGE`
     - `GCP_CLOUD_RUN_BATCH_ARGS`
     - `GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL`
     - `DOCKER_HUB_USERNAME`
     - `DOCKER_HUB_PASSWORD`
     - `DOCKER_IMAGE_NAME_PROCESSING`
   - Example:
     ```env
     GCP_PROJECT_ID=your-gcp-project-id
     GCP_REGION=your-region
     GCP_BUCKET_NAME=your-bucket-name
     GCP_CLOUD_RUN_BATCH_JOB_NAME=my-cloud-run-batch-job
     GCP_CLOUD_RUN_BATCH_SCHEDULE="0 22 * * *"
     GCP_CLOUD_RUN_BATCH_IMAGE=docker.io/usuario/mi-imagen:20240911
     GCP_CLOUD_RUN_BATCH_ARGS="--param1 valor1"
     GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL=micorreo@ejemplo.com
     DOCKER_HUB_USERNAME=your-dockerhub-username
     DOCKER_HUB_PASSWORD=your-dockerhub-password
     DOCKER_IMAGE_NAME_PROCESSING=your-image-name
     ```

3. **Configure Infrastructure with Terraform**:
   - See [Terraform Guide](terraform/README.md) for detailed commands
   - Basic commands: `terraform init`, `terraform plan`, `terraform apply`

### Running Notebooks

To run the analysis notebooks:
- See [UV Guide](docs/uv_guide.md) for detailed commands
- Basic command: `uv run jupyter notebook`

### Infrastructure Management
- See [Terraform Guide](terraform/README.md) for detailed commands
- Basic commands: `terraform show`, `terraform destroy`

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Documentation

- [Processing Module README](src/processing/README.md)
- [Terraform README](terraform/README.md)
- [Workflows README](.github/workflows/README.md)
- [GCP Setup Guide](docs/setup_gcp_project.md)
- [UV Guide](docs/uv_guide.md)
- [Docker Guide](docs/docker_guide.md)
- [GitHub Actions Guide](docs/github_actions_guide.md)
- [act Guide](docs/act_guide.md)

---

## Descripción

Este proyecto implementa una aplicación RAG (Retrieval-Augmented Generation) sobre la Ley Nº 213 que Establece el Código del Trabajo del Paraguay. El flujo principal consiste en:

- **Extracción**: Descarga y almacenamiento de la ley original.
- **Procesamiento**: Uso de dlt y Python para limpiar, segmentar y enriquecer el texto legal.
- **Almacenamiento**: Guardado del archivo procesado en un bucket de Google Cloud Storage (GGS).
- **Indexado**: Carga de los datos procesados en una base vectorial Qdrant, aplicando modelos de indexado según idioma y área, y agregando metadatos para filtrado eficiente.
- **Recuperación y respuesta**: Uso de OpenAI como LLM y un prompt especializado para responder preguntas de usuarios sobre la ley, a través de una API REST construida con FastAPI y Pydantic.
- **Evaluación**: Evaluación integral de la aplicación RAG, incluyendo los prompts, los modelos de indexado y el sistema RAG en general.
- **Monitoreo**: Monitoreo de la aplicación y sus respuestas usando Phoenix.
- **Infraestructura como código**: Terraform se utiliza para gestionar la infraestructura de Google Cloud Platform, incluyendo la creación de buckets de Storage y la configuración de servicios necesarios.
- **Despliegue en la nube**: Google Cloud Run se utiliza tanto para ejecutar el proceso batch que carga la base Qdrant como para desplegar la API FastAPI que extrae información de la base vectorial.
- **Automatización**: GitHub Actions se utiliza para automatizar procesos clave del proyecto, como pruebas, despliegues y tareas de integración continua. Consulta el [README de workflows](.github/workflows/README.md) para detalles de automatización.

El proyecto está organizado en carpetas como:
- `data/raw/` — Ley original descargada
- `data/processed/` — Ley procesada lista para indexar
- `src/processing/` — Scripts de extracción y procesamiento
- `src/api/` — API REST con FastAPI
- `src/vectorstore/` — Scripts para cargar y gestionar Qdrant
- `notebooks/` — Documentación y experimentos
- `evaluation/` — Scripts y notebooks para evaluación de la aplicación RAG
- `monitoring/` — Scripts y configuración para monitoreo con Phoenix
- `deploy/` — Archivos de despliegue y configuración para Google Cloud Run
- `utils/` — Scripts de utilidad para gestión y automatización del proyecto
- `.github/workflows/` — Workflows de GitHub Actions para automatización

## Estructura del Proyecto

```
lus-laboris-py/
├── data/                   # Directorio de datos
│   ├── raw/               # Datos originales sin procesar
│   └── processed/         # Datos limpios y procesados
├── deploy/                # Archivos de despliegue y configuración
├── docs/                  # Documentación del proyecto
│   ├── setup_gcp_project.md  # Guía de configuración de GCP
│   ├── uv_guide.md        # Guía del gestor de paquetes UV
│   ├── docker_guide.md    # Guía de Docker (incluye Docker, Compose y Hub)
│   ├── github_actions_guide.md  # Guía de GitHub Actions
│   └── README.md          # Índice de documentación
├── evaluation/            # Scripts de evaluación de la aplicación RAG
├── monitoring/            # Scripts de monitoreo y observabilidad
├── notebooks/             # Jupyter notebooks para análisis
│   ├── pyproject.toml
│   ├── README.md
│   └── uv.lock
├── src/                   # Código fuente principal
│   ├── api/               # Implementación de API REST con FastAPI
│   ├── core/              # Funcionalidades principales y lógica de negocio
│   ├── processing/        # Scripts de extracción y procesamiento de datos
│   │   └── README.md      # Documentación del módulo de procesamiento
│   └── vectorstore/       # Scripts para la base de datos vectorial Qdrant
├── tests/                 # Pruebas unitarias y de integración
├── terraform/             # Infraestructura como código
│   ├── modules/           # Módulos reutilizables de Terraform
│   │   ├── gcs/           # Módulo para Google Cloud Storage
│   │   │   └── README.md  # Documentación del módulo GCS
│   │   └── cloud_run_job/ # Módulo para Cloud Run Job (batch)
│   │       └── README.md  # Documentación del módulo Cloud Run Job
│   ├── main.tf            # Configuración principal
│   ├── variables.tf       # Variables de entrada
│   ├── providers.tf       # Configuración de proveedores
│   ├── terraform.tfvars   # Valores de variables
│   ├── tf_menu.sh         # Script de menú interactivo
│   └── README.md          # Documentación de Terraform
├── utils/                 # Scripts de utilidad y herramientas
│   ├── gcp_utils.py       # Utilidades GCP para gestión de buckets
│   ├── pyproject.toml     # Dependencias para utils
│   └── README.md          # Documentación de utils
├── .github/workflows/     # Workflows de GitHub Actions
├── LICENSE                # Licencia del proyecto
└── README.md              # Este archivo
```

## Descripción de Directorios

- **`data/`**: Almacena todos los datos del proyecto, con subdirectorios para archivos crudos y procesados.
- **`deploy/`**: Contiene guías de despliegue, Dockerfiles y archivos de configuración para Google Cloud.
- **`docs/`**: Documentación completa del proyecto, incluyendo guías de configuración y setup. Consulta especialmente [setup_gcp_project.md](docs/setup_gcp_project.md) y [terraform/README.md](terraform/README.md).
- **`evaluation/`**: Scripts y notebooks para evaluar el rendimiento de la aplicación RAG.
- **`monitoring/`**: Scripts y configuración para monitoreo y observabilidad de la aplicación.
- **`notebooks/`**: Jupyter notebooks para experimentación, análisis y documentación.
- **`src/api/`**: Implementación de API REST con FastAPI para exponer funcionalidades del proyecto. Consulta [src/processing/README.md](src/processing/README.md) para detalles de procesamiento.
- **`src/core/`**: Funcionalidades principales y lógica de negocio del proyecto.
- **`src/processing/`**: Scripts para extracción, limpieza y procesamiento de datos.
- **`src/vectorstore/`**: Scripts para carga, gestión y consulta de la base de datos vectorial Qdrant.
- **`terraform/`**: Infraestructura como código para gestionar recursos de Google Cloud Platform. Consulta [terraform/README.md](terraform/README.md) para detalles.
- **`tests/`**: Pruebas unitarias y de integración para asegurar la calidad y corrección del código.
- **`utils/`**: Utilidades y scripts auxiliares para el proyecto, incluyendo gestión de buckets GCP para el estado de Terraform.

## Características

- **Extracción de Datos**: Herramientas para extraer información de fuentes web
- **Análisis de Datos**: Notebooks de Jupyter para análisis interactivo
- **API REST**: Servicios web con FastAPI para consultas sobre la ley laboral
- **Procesamiento**: Funcionalidades core para el procesamiento de datos legales
- **Base de Datos Vectorial**: Almacenamiento y búsqueda semántica con Qdrant
- **Infraestructura como Código**: Gestión de infraestructura con Terraform
- **Monitoreo**: Observabilidad y seguimiento con Phoenix
- **Evaluación**: Métricas y análisis de rendimiento del sistema RAG
- **Automatización**: Workflows de CI/CD e infraestructura con GitHub Actions ([ver workflows](.github/workflows/README.md))

## Requisitos

- Python 3.13 (gestionado con [uv](docs/uv_guide.md); cada submódulo puede tener sus propias dependencias)
- Terraform (para gestión de infraestructura)
- Google Cloud Platform (cuenta y credenciales)
- Ver [Guía de UV](docs/uv_guide.md) para gestión de paquetes Python

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/jesusoviedo/lus-laboris-py.git
cd lus-laboris-py
```

2. Configura el entorno de desarrollo:
   - Ver [Guía de UV](docs/uv_guide.md) para gestión de paquetes Python (cada submódulo puede tener su propio `pyproject.toml`)
   - Ver [Guía de Terraform](terraform/README.md) para configuración de infraestructura

## Uso

### Desarrollo Local

#### Pruebas de Workflows Localmente

Usa el script interactivo para probar workflows de GitHub Actions localmente:

```bash
cd .github/workflows/
bash act_menu.sh
```

Para uso detallado de act, ver [act_guide.md](docs/act_guide.md).

#### Gestión de Infraestructura

Usa el menú interactivo de Terraform:

```bash
cd terraform/
bash tf_menu.sh
```

#### Desarrollo con Docker

Construye y prueba imágenes Docker localmente:

```bash
cd src/processing/
bash docker_build_push.sh
```

### Configuración Inicial

1. **Configurar Google Cloud Platform**:
   - Sigue la guía en [docs/setup_gcp_project.md](docs/setup_gcp_project.md)
   - Configura las credenciales de servicio

2. **Crea el archivo .env en la raíz del proyecto**:
   - Las siguientes variables son obligatorias para Terraform y los scripts de automatización:
     - `GCP_PROJECT_ID`
     - `GCP_REGION`
     - `GCP_BUCKET_NAME`
     - `GCP_CLOUD_RUN_BATCH_JOB_NAME`
     - `GCP_CLOUD_RUN_BATCH_SCHEDULE`
     - `GCP_CLOUD_RUN_BATCH_IMAGE`
     - `GCP_CLOUD_RUN_BATCH_ARGS`
     - `GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL`
     - `DOCKER_HUB_USERNAME`
     - `DOCKER_HUB_PASSWORD`
     - `DOCKER_IMAGE_NAME_PROCESSING`
   - Ejemplo:
     ```env
     GCP_PROJECT_ID=tu-proyecto-gcp
     GCP_REGION=tu-region
     GCP_BUCKET_NAME=nombre-de-tu-bucket
     GCP_CLOUD_RUN_BATCH_JOB_NAME=mi-cloud-run-batch-job
     GCP_CLOUD_RUN_BATCH_SCHEDULE=0 22 * * *"
     GCP_CLOUD_RUN_BATCH_IMAGE=docker.io/usuario/mi-imagen:20240911
     GCP_CLOUD_RUN_BATCH_ARGS="--param1 valor1"
     GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL=micorreo@ejemplo.com
     DOCKER_HUB_USERNAME=tu-usuario-dockerhub
     DOCKER_HUB_PASSWORD=tu-contraseña-dockerhub
     DOCKER_IMAGE_NAME_PROCESSING=nombre-de-tu-imagen
     ```

3. **Configura la infraestructura con Terraform**:
   - Ver [Guía de Terraform](terraform/README.md) para comandos detallados
   - Comandos básicos: `terraform init`, `terraform plan`, `terraform apply`

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Documentación

- [README del módulo de procesamiento](src/processing/README.md)
- [README de Terraform](terraform/README.md)
- [README de Workflows](.github/workflows/README.md)
- [Guía de configuración de GCP](docs/setup_gcp_project.md)
- [Guía de UV](docs/uv_guide.md)
- [Guía de Docker](docs/docker_guide.md)
- [Guía de GitHub Actions](docs/github_actions_guide.md)
- [Guía de act](docs/act_guide.md)
