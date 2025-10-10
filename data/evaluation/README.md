<div align="center">

**Language / Idioma:**
[🇺🇸 English](#evaluation-data) | [🇪🇸 Español](#datos-de-evaluación)

</div>

---

## Evaluation Data

This folder contains datasets used for evaluating the RAG pipeline performance, including test queries, ground truth answers, and evaluation metrics.

### Contents

- **Test Datasets**: Curated sets of questions and answers for RAG evaluation
- **Ground Truth**: Reference answers for measuring accuracy and relevance
- **Evaluation Metrics**: Performance measurements and analysis results
- **Benchmark Data**: Standardized datasets for comparing different configurations

### Usage

These datasets are used by the evaluation notebooks in the `notebooks/` directory, specifically:

- `03_rag_pipeline_evaluation.ipynb` - Main evaluation notebook
- Other evaluation-related notebooks

### Data Sources

The evaluation datasets are created from:

- Manual curation of relevant legal questions
- Expert-validated answers from Paraguay's Labor Code
- Synthetic test cases for edge scenarios
- Performance benchmarks from similar RAG systems

---

## Datos de Evaluación

Esta carpeta contiene datasets utilizados para evaluar el rendimiento del pipeline RAG, incluyendo consultas de prueba, respuestas de referencia y métricas de evaluación.

### Contenidos

- **Datasets de Prueba**: Conjuntos curados de preguntas y respuestas para evaluación RAG
- **Respuestas de Referencia**: Respuestas de referencia para medir precisión y relevancia
- **Métricas de Evaluación**: Mediciones de rendimiento y resultados de análisis
- **Datos de Benchmark**: Datasets estandarizados para comparar diferentes configuraciones

### Uso

Estos datasets son utilizados por los notebooks de evaluación en el directorio `notebooks/`, específicamente:

- `03_rag_pipeline_evaluation.ipynb` - Notebook principal de evaluación
- Otros notebooks relacionados con evaluación

### Fuentes de Datos

Los datasets de evaluación se crean a partir de:

- Curación manual de preguntas legales relevantes
- Respuestas validadas por expertos del Código del Trabajo de Paraguay
- Casos de prueba sintéticos para escenarios límite
- Benchmarks de rendimiento de sistemas RAG similares
