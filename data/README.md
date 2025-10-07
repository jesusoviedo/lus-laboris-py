# Data

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#data) | [🇪🇸 Español](#datos)

</div>

---

## Data

This folder contains all data used in the project, organized into three main subdirectories:

## Structure

- **`raw/`**: Stores the original, unprocessed data as downloaded from external sources
  - Contains the HTML file of Paraguay's Labor Code (Ley Nº 213) downloaded from the official government website
  - Files are stored in their original format for reproducibility

- **`processed/`**: Stores cleaned and processed data ready for indexing, analysis, or use by the application
  - Contains structured JSON files with parsed legal articles
  - Data is normalized and ready for downstream processing

- **`evaluation/`**: Contains datasets used for evaluating the RAG pipeline performance
  - Test datasets with curated questions and answers
  - Ground truth data for measuring accuracy and relevance
  - Evaluation metrics and benchmark results

## Data Processing

### Manual Process
For a detailed step-by-step guide on how the data is downloaded and processed, see:
- **[Notebook: Extract Law Text](../notebooks/01_extract_law_text.ipynb)** - Interactive notebook showing the complete data extraction and processing pipeline

### Automated Process
For automated data processing, use the provided Python script:
- **[Script: extract_law_text.py](../src/processing/extract_law_text.py)** - Automated script that downloads and processes the law text

### Usage
```bash
# Run the automated processing script
python src/processing/extract_law_text.py
```

## Data Organization

Keep data organized for reproducibility and collaboration. The processing pipeline ensures:
- Raw data preservation for audit trails
- Consistent data structure across processed files
- Clear separation between source and processed data

---

## Datos

Esta carpeta contiene todos los datos utilizados en el proyecto, organizados en tres subdirectorios principales:

## Estructura

- **`raw/`**: Almacena los datos originales sin procesar tal como fueron descargados de fuentes externas
  - Contiene el archivo HTML del Código Laboral de Paraguay (Ley Nº 213) descargado del sitio oficial del gobierno
  - Los archivos se almacenan en su formato original para reproducibilidad

- **`processed/`**: Almacena los datos limpios y procesados, listos para indexar, analizar o usar por la aplicación
  - Contiene archivos JSON estructurados con artículos legales parseados
  - Los datos están normalizados y listos para procesamiento posterior

- **`evaluation/`**: Contiene datasets utilizados para evaluar el rendimiento del pipeline RAG
  - Datasets de prueba con preguntas y respuestas curadas
  - Datos de referencia para medir precisión y relevancia
  - Métricas de evaluación y resultados de benchmarks

## Procesamiento de Datos

### Proceso Manual
Para una guía detallada paso a paso sobre cómo se descargan y procesan los datos, consulta:
- **[Notebook: Extract Law Text](../notebooks/01_extract_law_text.ipynb)** - Notebook interactivo que muestra el pipeline completo de extracción y procesamiento de datos

### Proceso Automatizado
Para el procesamiento automatizado de datos, usa el script de Python proporcionado:
- **[Script: extract_law_text.py](../src/processing/extract_law_text.py)** - Script automatizado que descarga y procesa el texto de la ley

### Uso
```bash
# Ejecutar el script de procesamiento automatizado
python src/processing/extract_law_text.py
```

## Organización de Datos

Mantén los datos organizados para facilitar la reproducibilidad y la colaboración. El pipeline de procesamiento asegura:
- Preservación de datos crudos para auditorías
- Estructura de datos consistente en archivos procesados
- Separación clara entre datos fuente y procesados