# lus-laboris-py

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-FF6B6B?style=for-the-badge&logo=python&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![DLT](https://img.shields.io/badge/DLT-FF6B35?style=for-the-badge&logo=data&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-FF6B35?style=for-the-badge&logo=qdrant&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Phoenix](https://img.shields.io/badge/Phoenix-FF7100?style=for-the-badge&logo=phoenixframework&logoColor=white)
![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

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
- **Automation**: GitHub Actions is used to automate key project processes such as testing, deployment, and CI tasks.

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
│   └── vectorstore/       # Qdrant vector database scripts
├── tests/                 # Unit and integration tests
├── terraform/             # Infrastructure as Code
│   ├── modules/           # Reusable Terraform modules
│   │   └── gcs/           # Google Cloud Storage module
│   ├── main.tf            # Main configuration
│   ├── variables.tf       # Input variables
│   ├── providers.tf       # Provider configuration
│   ├── terraform.tfvars   # Variable values
│   └── README.md          # Terraform documentation
├── utils/                 # Utility scripts and tools
│   ├── gcp_utils.py       # GCP utilities for bucket management
│   ├── pyproject.toml     # Dependencies for utils
│   └── README.md          # Utils documentation
├── docs/                  # Project documentation
│   ├── setup_gcp_project.md  # GCP setup guide
│   ├── uv_guide.md        # UV package manager guide
│   ├── docker_guide.md    # Docker guide
│   ├── docker_compose_guide.md  # Docker Compose guide
│   ├── docker_hub_guide.md     # Docker Hub guide
│   ├── github_actions_guide.md  # GitHub Actions guide
│   └── README.md          # Documentation index
├── .github/workflows/     # GitHub Actions workflows
├── LICENSE                # Project license
└── README.md              # This file
```

## Directory Overview

- **`data/`**: Stores all project data, with subdirectories for raw and processed files.
- **`deploy/`**: Contains deployment guides, Dockerfiles, and configuration files for Google Cloud.
- **`docs/`**: Complete project documentation, including setup and configuration guides.
- **`evaluation/`**: Scripts and notebooks for evaluating the RAG application's performance.
- **`monitoring/`**: Scripts and configuration for application monitoring and observability.
- **`notebooks/`**: Jupyter notebooks for experimentation, analysis, and documentation.
- **`src/api/`**: FastAPI REST API implementation for exposing project functionalities.
- **`src/core/`**: Core functionalities and business logic of the project.
- **`src/processing/`**: Scripts for data extraction, cleaning, and processing.
- **`src/vectorstore/`**: Scripts for loading, managing, and querying the Qdrant vector database.
- **`terraform/`**: Infrastructure as Code for managing Google Cloud Platform resources.
- **`tests/`**: Unit and integration tests to ensure code quality and correctness.
- **`utils/`**: Utility scripts and tools for project management, including GCP bucket management for Terraform state.

## Features

- **Data Extraction**: Tools for extracting information from web sources
- **Data Analysis**: Jupyter notebooks for interactive analysis
- **REST API**: Web services with FastAPI for labor law queries
- **Processing**: Core functionalities for legal data processing
- **Vector Database**: Semantic storage and search with Qdrant
- **Infrastructure as Code**: Infrastructure management with Terraform
- **Monitoring**: Observability and tracking with Phoenix
- **Evaluation**: Metrics and performance analysis of the RAG system

## Requirements

- Python 3.13
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
   - See [UV Guide](docs/uv_guide.md) for Python package management
   - See [Terraform Guide](terraform/README.md) for infrastructure setup

## Usage

### Initial Setup

1. **Configure Google Cloud Platform**:
   - Follow the guide in `docs/setup_gcp_project.md`
   - Set up service account credentials

2. **Configure Infrastructure with Terraform**:
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

## Contact

Jesus Oviedo Riquelme - j92riquelme@gmail.com - [LinkedIn](https://www.linkedin.com/in/jesusoviedoriquelme)

Project Link: [https://github.com/jesusoviedo/lus-laboris-py](https://github.com/jesusoviedo/lus-laboris-py)

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
- **Automatización**: GitHub Actions se utiliza para automatizar procesos clave del proyecto, como pruebas, despliegues y tareas de integración continua.

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
│   ├── docker_guide.md    # Guía de Docker
│   ├── docker_compose_guide.md  # Guía de Docker Compose
│   ├── docker_hub_guide.md     # Guía de Docker Hub
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
│   └── vectorstore/       # Scripts para la base de datos vectorial Qdrant
├── tests/                 # Pruebas unitarias y de integración
├── terraform/             # Infraestructura como código
│   ├── modules/           # Módulos reutilizables de Terraform
│   │   └── gcs/           # Módulo para Google Cloud Storage
│   ├── main.tf            # Configuración principal
│   ├── variables.tf       # Variables de entrada
│   ├── providers.tf       # Configuración de proveedores
│   ├── terraform.tfvars   # Valores de variables
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
- **`docs/`**: Documentación completa del proyecto, incluyendo guías de configuración y setup.
- **`evaluation/`**: Scripts y notebooks para evaluar el rendimiento de la aplicación RAG.
- **`monitoring/`**: Scripts y configuración para monitoreo y observabilidad de la aplicación.
- **`notebooks/`**: Jupyter notebooks para experimentación, análisis y documentación.
- **`src/api/`**: Implementación de API REST con FastAPI para exponer las funcionalidades del proyecto.
- **`src/core/`**: Funcionalidades principales y lógica de negocio del proyecto.
- **`src/processing/`**: Scripts para extracción, limpieza y procesamiento de datos.
- **`src/vectorstore/`**: Scripts para carga, gestión y consulta de la base de datos vectorial Qdrant.
- **`terraform/`**: Infraestructura como código para gestionar recursos de Google Cloud Platform.
- **`tests/`**: Pruebas unitarias y de integración para asegurar la calidad y corrección del código.
- **`utils/`**: Utilidades y scripts auxiliares para el proyecto.

## Características

- **Extracción de Datos**: Herramientas para extraer información de fuentes web
- **Análisis de Datos**: Notebooks de Jupyter para análisis interactivo
- **API REST**: Servicios web con FastAPI para consultas sobre la ley laboral
- **Procesamiento**: Funcionalidades core para el procesamiento de datos legales
- **Base de Datos Vectorial**: Almacenamiento y búsqueda semántica con Qdrant
- **Infraestructura como Código**: Gestión de infraestructura con Terraform
- **Monitoreo**: Observabilidad y seguimiento con Phoenix
- **Evaluación**: Métricas y análisis de rendimiento del sistema RAG

## Requisitos

- Python 3.13
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
   - Ver [Guía de UV](docs/uv_guide.md) para gestión de paquetes Python
   - Ver [Guía de Terraform](terraform/README.md) para configuración de infraestructura

## Uso

### Configuración Inicial

1. **Configurar Google Cloud Platform**:
   - Sigue la guía en `docs/setup_gcp_project.md`
   - Configura las credenciales de servicio

2. **Configurar Infraestructura con Terraform**:
   - Ver [Guía de Terraform](terraform/README.md) para comandos detallados
   - Comandos básicos: `terraform init`, `terraform plan`, `terraform apply`

### Ejecutar Notebooks

Para ejecutar los notebooks de análisis:
- Ver [Guía de UV](docs/uv_guide.md) para comandos detallados
- Comando básico: `uv run jupyter notebook`

### Gestión de Infraestructura
- Ver [Guía de Terraform](terraform/README.md) para comandos detallados
- Comandos básicos: `terraform show`, `terraform destroy`

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

Jesus Oviedo Riquelme - j92riquelme@gmail.com - [LinkedIn](https://www.linkedin.com/in/jesusoviedoriquelme)

Link del Proyecto: [https://github.com/jesusoviedo/lus-laboris-py](https://github.com/jesusoviedo/lus-laboris-py)
