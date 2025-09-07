# lus-laboris-py

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-FF6B6B?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![DLT](https://img.shields.io/badge/DLT-FF6B35?style=for-the-badge&logo=data&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-FF6B35?style=for-the-badge&logo=qdrant&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Phoenix](https://img.shields.io/badge/Phoenix-FF7100?style=for-the-badge&logo=phoenixframework&logoColor=white)
![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

</div>

## Descripción

Este proyecto implementa una aplicación RAG (Retrieval-Augmented Generation) sobre la Ley Nº 213 que Establece el Código del Trabajo del Paraguay. El flujo principal consiste en:

- **Extracción**: Descarga y almacenamiento de la ley original.
- **Procesamiento**: Uso de dlt y Python para limpiar, segmentar y enriquecer el texto legal.
- **Almacenamiento**: Guardado del archivo procesado en un bucket de Google Cloud Storage (GGS).
- **Indexado**: Carga de los datos procesados en una base vectorial Qdrant, aplicando modelos de indexado según idioma y área, y agregando metadatos para filtrado eficiente.
- **Recuperación y respuesta**: Uso de OpenAI como LLM y un prompt especializado para responder preguntas de usuarios sobre la ley, a través de una API REST construida con FastAPI y Pydantic.
- **Evaluación**: Evaluación integral de la aplicación RAG, incluyendo los prompts, los modelos de indexado y el sistema RAG en general.
- **Monitoreo**: Monitoreo de la aplicación y sus respuestas usando Phoenix.
- **Despliegue en la nube**: Google Cloud Run se utiliza tanto para ejecutar el proceso batch que carga la base Qdrant como para desplegar la API FastAPI que extrae información de la base vectorial.
- **Automatización**: GitHub Actions se utiliza para automatizar procesos clave del proyecto, como pruebas, despliegues y tareas de integración continua.

## Estructura del Proyecto

```
lus-laboris-py/
├── data/                   # Directorio de datos
│   ├── raw/               # Datos originales sin procesar
│   └── processed/         # Datos limpios y procesados
├── deploy/                # Archivos de despliegue y configuración
├── evaluation/            # Scripts de evaluación de la aplicación RAG
├── monitoring/            # Scripts de monitoreo y observabilidad
├── notebooks/             # Jupyter notebooks para análisis
│   ├── 01_data_extraction.ipynb
│   ├── pyproject.toml
│   ├── README.md
│   └── uv.lock
├── src/                   # Código fuente principal
│   ├── api/               # Implementación de API REST con FastAPI
│   ├── core/              # Funcionalidades principales y lógica de negocio
│   ├── processing/        # Scripts de extracción y procesamiento de datos
│   └── vectorstore/       # Scripts para la base de datos vectorial Qdrant
├── tests/                 # Pruebas unitarias y de integración
├── .github/workflows/     # Workflows de GitHub Actions
├── LICENSE                # Licencia del proyecto
├── README.md              # Este archivo
└── README_ES.md           # Versión en español de este archivo
```

## Descripción de Directorios

- **`data/`**: Almacena todos los datos del proyecto, con subdirectorios para archivos crudos y procesados.
- **`deploy/`**: Contiene guías de despliegue, Dockerfiles y archivos de configuración para Google Cloud.
- **`evaluation/`**: Scripts y notebooks para evaluar el rendimiento de la aplicación RAG.
- **`monitoring/`**: Scripts y configuración para monitoreo y observabilidad de la aplicación.
- **`notebooks/`**: Jupyter notebooks para experimentación, análisis y documentación.
- **`src/api/`**: Implementación de API REST con FastAPI para exponer las funcionalidades del proyecto.
- **`src/core/`**: Funcionalidades principales y lógica de negocio del proyecto.
- **`src/processing/`**: Scripts para extracción, limpieza y procesamiento de datos.
- **`src/vectorstore/`**: Scripts para carga, gestión y consulta de la base de datos vectorial Qdrant.
- **`tests/`**: Pruebas unitarias y de integración para asegurar la calidad y corrección del código.

## Características

- **Extracción de Datos**: Herramientas para extraer información de fuentes web
- **Análisis de Datos**: Notebooks de Jupyter para análisis interactivo
- **API**: Módulos para crear servicios web con FastAPI
- **Procesamiento**: Funcionalidades core para el procesamiento de datos

## Requisitos

- Python 3.13
- uv (gestor de dependencias)
- FastAPI
- Dependencias principales:
  - beautifulsoup4 >= 4.13.5
  - notebook >= 7.4.5

## Instalación

1. Instala uv si no lo tienes:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clona el repositorio:
```bash
git clone https://github.com/jesusoviedo/lus-laboris-py.git
cd lus-laboris-py
```

3. Instala las dependencias con uv:
```bash
uv sync
```

## Uso

### Ejecutar Notebooks

Para ejecutar los notebooks de análisis:

```bash
cd notebooks
uv run jupyter notebook
```

### Usar la API

```python
from src.api import tu_modulo
# Tu código aquí
```

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
