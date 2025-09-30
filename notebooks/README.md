<div align="center">

**Language / Idioma:**
[🇺🇸 English](#notebooks) | [🇪🇸 Español](#notebooks-1)

</div>

---

## Notebooks

This folder contains Jupyter notebooks used for:

- Code experimentation and prototyping
- Data analysis and processing
- Documentation of workflows and tests
- Examples of project functionality usage

### Available Notebooks

| Notebook | Description | Purpose |
|----------|-------------|---------|
| `01_extract_law_text.ipynb` | Law Text Extraction and Processing | Download and parse Paraguay's Labor Code from official source |
| `02_vectorstore_embedding_exploration.ipynb` | Embedding Models Evaluation | Compare different embedding models for RAG system optimization |
| `03_rag_pipeline_evaluation.ipynb` | RAG Pipeline Comprehensive Evaluation | Evaluate retrieval, re-ranking, and generation components |

### Detailed Notebook Descriptions

#### 01_extract_law_text.ipynb
**Goal**: Download and process Paraguay's Labor Code text for further analysis and indexing.

**Key Features**:
- Downloads HTML content from official government website
- Extracts and cleans legal text using BeautifulSoup
- Segments text into structured articles (books, titles, chapters, articles)
- Generates structured JSON output with metadata
- Handles encoding issues and text normalization

**Output**: Structured JSON file with 410 legal articles organized by hierarchy

#### 02_vectorstore_embedding_exploration.ipynb
**Goal**: Evaluate different embedding models to determine the most suitable one for RAG queries about Paraguayan labor law.

**Key Features**:
- Tests 11 different embedding models (multilingual and Spanish-optimized)
- Compares performance metrics: loading time, embedding speed, search quality
- Evaluates search quality using cosine similarity on legal queries
- Integrates with Qdrant vector database for production testing
- Provides comprehensive analysis with visualizations and rankings

**Models Evaluated**: sentence-transformers, Jina AI, OpenAI, multilingual models
**Output**: Performance analysis, model recommendations, and integration examples

#### 03_rag_pipeline_evaluation.ipynb
**Goal**: Comprehensive evaluation of the complete RAG pipeline at multiple levels.

**Key Features**:
- **Retrieval Level**: Evaluates embedding models with metrics like Recall@k, Precision@k, nDCG@k
- **Re-ranking Level**: Tests cross-encoder models to improve document relevance
- **Generation Level**: Evaluates LLM responses using LLM-as-a-judge methodology
- Uses structured evaluation dataset with ground truth answers
- Provides objective and subjective metrics for system performance

**Evaluation Levels**: Retrieval, Re-ranking, Generation
**Technologies**: Qdrant, Sentence Transformers, Cross-encoders, OpenAI, Google Gemini

### Usage

You can run the notebooks with:
- See [UV Guide](../docs/uv_guide.md) for detailed commands
- Basic command: `uv run jupyter notebook`

### Prerequisites

- Environment variables configured in `.env` file
- Qdrant vector database running
- OpenAI API key for LLM evaluation
- Gemini API key for LLM evaluation
- Required Python packages installed via `uv sync`

Remember to keep notebooks organized and documented to facilitate collaboration and reproducibility of experiments.

---

## Notebooks

Esta carpeta contiene notebooks de Jupyter utilizados para:

- Experimentación y prototipado de código
- Análisis y procesamiento de datos
- Documentación de flujos y pruebas
- Ejemplos de uso de las funcionalidades del proyecto

### Notebooks Disponibles

| Notebook | Descripción | Propósito |
|----------|-------------|-----------|
| `01_extract_law_text.ipynb` | Extracción y Procesamiento de Texto Legal | Descargar y parsear el Código Laboral de Paraguay desde fuente oficial |
| `02_vectorstore_embedding_exploration.ipynb` | Evaluación de Modelos de Embedding | Comparar diferentes modelos de embedding para optimización del sistema RAG |
| `03_rag_pipeline_evaluation.ipynb` | Evaluación Integral del Pipeline RAG | Evaluar componentes de recuperación, re-ranking y generación |

### Descripciones Detalladas de Notebooks

#### 01_extract_law_text.ipynb
**Objetivo**: Descargar y procesar el texto del Código Laboral de Paraguay para análisis posterior e indexación.

**Características Principales**:
- Descarga contenido HTML desde el sitio oficial del gobierno
- Extrae y limpia texto legal usando BeautifulSoup
- Segmenta texto en artículos estructurados (libros, títulos, capítulos, artículos)
- Genera salida JSON estructurada con metadatos
- Maneja problemas de codificación y normalización de texto

**Salida**: Archivo JSON estructurado con 410 artículos legales organizados jerárquicamente

#### 02_vectorstore_embedding_exploration.ipynb
**Objetivo**: Evaluar diferentes modelos de embedding para determinar el más adecuado para consultas RAG sobre ley laboral paraguaya.

**Características Principales**:
- Prueba 11 modelos de embedding diferentes (multilingües y optimizados para español)
- Compara métricas de rendimiento: tiempo de carga, velocidad de embedding, calidad de búsqueda
- Evalúa calidad de búsqueda usando similitud coseno en consultas legales
- Integra con base de datos vectorial Qdrant para pruebas de producción
- Proporciona análisis integral con visualizaciones y rankings

**Modelos Evaluados**: sentence-transformers, Jina AI, OpenAI, modelos multilingües
**Salida**: Análisis de rendimiento, recomendaciones de modelos y ejemplos de integración

#### 03_rag_pipeline_evaluation.ipynb
**Objetivo**: Evaluación integral del pipeline RAG completo en múltiples niveles.

**Características Principales**:
- **Nivel de Recuperación**: Evalúa modelos de embedding con métricas como Recall@k, Precision@k, nDCG@k
- **Nivel de Re-ranking**: Prueba modelos cross-encoder para mejorar relevancia de documentos
- **Nivel de Generación**: Evalúa respuestas LLM usando metodología LLM-as-a-judge
- Utiliza dataset de evaluación estructurado con respuestas de referencia
- Proporciona métricas objetivas y subjetivas para rendimiento del sistema

**Niveles de Evaluación**: Recuperación, Re-ranking, Generación
**Tecnologías**: Qdrant, Sentence Transformers, Cross-encoders, OpenAI, Google Gemini

### Uso

Puedes ejecutar los notebooks con:
- Ver [Guía de UV](../docs/uv_guide.md) para comandos detallados
- Comando básico: `uv run jupyter notebook`

### Prerrequisitos

- Variables de entorno configuradas en archivo `.env`
- Base de datos vectorial Qdrant ejecutándose
- Clave API de OpenAI para evaluación LLM
- Clave API de Gemini para evaluación LLM
- Paquetes Python requeridos instalados via `uv sync`

Recuerda mantener los notebooks organizados y documentados para facilitar la colaboración y la reproducibilidad de los experimentos.
