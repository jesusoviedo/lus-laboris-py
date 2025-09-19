<div align="center">

# 🚀 Proyecto Py Labor Law RAG (lus-laboris-py)

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![uv](https://img.shields.io/badge/uv-0A9EDC?logo=uv&logoColor=white)](https://github.com/astral-sh/uv)

[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Phoenix](https://img.shields.io/badge/Phoenix-FF7100?logo=phoenixframework&logoColor=white)](#)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?logoColor=white)](https://openai.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-FF6B35?logo=qdrant&logoColor=white)](https://qdrant.tech/)

[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/Docker--Compose-2496ED?logo=docker&logoColor=fff)](https://docs.docker.com/compose/)
[![Terraform](https://img.shields.io/badge/Terraform-844FBA?logo=terraform&logoColor=fff)](https://developer.hashicorp.com/terraform)

[![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![GCS](https://img.shields.io/badge/Google%20Cloud%20Storage-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/storage)
[![Compute Engine](https://img.shields.io/badge/Google%20Compute%20Engine-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/compute)

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](https://docs.github.com/en/actions)

[![Licencia MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)



[![Infra Provision](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-cd-terraform.yml/badge.svg)](https://github.com/jesusoviedo/spotify-dwh-insights/actions/workflows/ci-cd-terraform.yml)


[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)


**Language / Idioma:**
[🇺🇸 English](#Introduction) | [🇪🇸 Español](#Introducción)

</div>

---

## 📌 Introduction

**lus-laboris-py** is a RAG (Retrieval-Augmented Generation) application that provides intelligent access to Paraguay's Labor Code (Law Nº 213). The system enables users to query legal information through natural language using advanced AI technologies.

### Key Workflow
- **Data Processing**: Extract, clean, and structure legal text
- **Vector Storage**: Index processed data in Qdrant vector database
- **Intelligent Querying**: Use OpenAI and specialized prompts for accurate responses
- **API Access**: REST API built with FastAPI for seamless integration
- **Cloud Deployment**: Automated infrastructure management with Terraform and GitHub Actions

## 📂 Project Structure

| Directory | Purpose |
|-----------|---------|
| `data/` | Raw and processed legal data storage |
| `src/` | Core application code (API, processing, vector operations) |
| `notebooks/` | Analysis and experimentation notebooks |
| `terraform/` | Infrastructure as Code for Google Cloud Platform |
| `docs/` | Comprehensive project documentation |
| `utils/` | Utility scripts for automation and management |
| `evaluation/` | RAG system performance evaluation |
| `monitoring/` | Application observability and tracking |
| `.github/workflows/` | CI/CD automation workflows |

## ⚙️ Prerequisites

- **Python 3.13** (managed with `uv`)
- **Terraform** (for infrastructure management)
- **Google Cloud Platform** account with appropriate permissions
- **Docker** (for containerized development)

## 🚀 Getting Started

### 1. Clone and Setup
```bash
git clone https://github.com/jesusoviedo/lus-laboris-py.git
cd lus-laboris-py
```

### 2. Environment Configuration
Create a `.env` file at the project root with required variables:
```env
GCP_PROJECT_ID=your-project-id
GCP_REGION=your-region
GCP_BUCKET_NAME=your-bucket-name
# ... (see docs/setup_gcp_project.md for complete list)
```

### 3. Infrastructure Setup
```bash
# Automated GCP project setup
bash utils/setup_gcp_project.sh

# Deploy infrastructure
cd terraform/
bash tf_menu.sh
```

### 4. Local Development
```bash
# Test workflows locally
cd .github/workflows/
bash act_menu.sh

# Run notebooks
cd notebooks/
uv run jupyter notebook
```

## 📋 Key Features

- **🤖 AI-Powered Legal Search**: Advanced RAG system for legal document queries
- **☁️ Cloud-Native Architecture**: Scalable deployment on Google Cloud Platform
- **🔧 Infrastructure as Code**: Complete automation with Terraform
- **📊 Monitoring & Evaluation**: Comprehensive system performance tracking
- **🔄 CI/CD Pipeline**: Automated testing and deployment workflows
- **📚 Extensive Documentation**: Detailed guides for setup and usage

## 📚 Documentation

| Component | Documentation |
|-----------|---------------|
| **Setup** | [GCP Project Setup](docs/setup_gcp_project.md) |
| **Infrastructure** | [Terraform Guide](terraform/README.md) |
| **Automation** | [GitHub Actions](.github/workflows/README.md) |
| **Development** | [UV Package Manager](docs/uv_guide.md) |
| **Deployment** | [Docker Guide](docs/docker_guide.md) |
| **Utilities** | [Utility Scripts](utils/README.md) |

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📌 Introducción

**lus-laboris-py** es una aplicación RAG (Retrieval-Augmented Generation) que proporciona acceso inteligente al Código del Trabajo de Paraguay (Ley Nº 213). El sistema permite a los usuarios consultar información legal a través de lenguaje natural utilizando tecnologías avanzadas de IA.

### Flujo Principal
- **Procesamiento de Datos**: Extracción, limpieza y estructuración del texto legal
- **Almacenamiento Vectorial**: Indexación de datos procesados en base de datos vectorial Qdrant
- **Consultas Inteligentes**: Uso de OpenAI y prompts especializados para respuestas precisas
- **Acceso API**: API REST construida con FastAPI para integración fluida
- **Despliegue en la Nube**: Gestión automatizada de infraestructura con Terraform y GitHub Actions

## 📂 Estructura del Proyecto

| Directorio | Propósito |
|------------|-----------|
| `data/` | Almacenamiento de datos legales crudos y procesados |
| `src/` | Código principal de la aplicación (API, procesamiento, operaciones vectoriales) |
| `notebooks/` | Notebooks de análisis y experimentación |
| `terraform/` | Infraestructura como Código para Google Cloud Platform |
| `docs/` | Documentación completa del proyecto |
| `utils/` | Scripts de utilidad para automatización y gestión |
| `evaluation/` | Evaluación del rendimiento del sistema RAG |
| `monitoring/` | Observabilidad y seguimiento de la aplicación |
| `.github/workflows/` | Workflows de automatización CI/CD |

## ⚙️ Requisitos Previos

- **Python 3.13** (gestionado con `uv`)
- **Terraform** (para gestión de infraestructura)
- **Google Cloud Platform** cuenta con permisos apropiados
- **Docker** (para desarrollo containerizado)

## 🚀 Cómo Empezar

### 1. Clonar y Configurar
```bash
git clone https://github.com/jesusoviedo/lus-laboris-py.git
cd lus-laboris-py
```

### 2. Configuración del Entorno
Crear un archivo `.env` en la raíz del proyecto con las variables requeridas:
```env
GCP_PROJECT_ID=tu-proyecto-id
GCP_REGION=tu-region
GCP_BUCKET_NAME=tu-bucket-name
# ... (ver docs/setup_gcp_project.md para lista completa)
```

### 3. Configuración de Infraestructura
```bash
# Configuración automatizada del proyecto GCP
bash utils/setup_gcp_project.sh

# Desplegar infraestructura
cd terraform/
bash tf_menu.sh
```

### 4. Desarrollo Local
```bash
# Probar workflows localmente
cd .github/workflows/
bash act_menu.sh

# Ejecutar notebooks
cd notebooks/
uv run jupyter notebook
```

## 📋 Características Principales

- **🤖 Búsqueda Legal con IA**: Sistema RAG avanzado para consultas de documentos legales
- **☁️ Arquitectura Cloud-Native**: Despliegue escalable en Google Cloud Platform
- **🔧 Infraestructura como Código**: Automatización completa con Terraform
- **📊 Monitoreo y Evaluación**: Seguimiento integral del rendimiento del sistema
- **🔄 Pipeline CI/CD**: Workflows automatizados de testing y despliegue
- **📚 Documentación Extensa**: Guías detalladas para configuración y uso

## 📚 Documentación

| Componente | Documentación |
|------------|---------------|
| **Configuración** | [Configuración de Proyecto GCP](docs/setup_gcp_project.md) |
| **Infraestructura** | [Guía de Terraform](terraform/README.md) |
| **Automatización** | [GitHub Actions](.github/workflows/README.md) |
| **Desarrollo** | [Gestor de Paquetes UV](docs/uv_guide.md) |
| **Despliegue** | [Guía de Docker](docs/docker_guide.md) |
| **Utilidades** | [Scripts de Utilidad](utils/README.md) |

## 👥 Contribuciones

1. Fork del repositorio
2. Crear una rama de feature (`git checkout -b feature/caracteristica-increible`)
3. Commit de los cambios (`git commit -m 'Agregar característica increíble'`)
4. Push a la rama (`git push origin feature/caracteristica-increible`)
5. Abrir un Pull Request

## 📜 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.