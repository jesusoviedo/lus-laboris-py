# Phoenix Guide

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#phoenix-guide) | [🇪🇸 Español](#guía-de-phoenix)

</div>

---

# Phoenix Guide

This guide provides comprehensive instructions for setting up and using Phoenix for real-time observability and evaluation of the RAG system. Phoenix is an open-source observability platform designed specifically for LLM applications.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Configuration](#configuration)
- [Integration with RAG API](#integration-with-rag-api)
- [Advanced Tracing Features](#advanced-tracing-features)
- [Session Management](#session-management)
- [Span Kinds and Categorization](#span-kinds-and-categorization)
- [Monitoring Features](#monitoring-features)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Overview

Phoenix provides real-time observability for LLM applications, offering:

- **Trace Analysis**: Detailed tracing of requests through the RAG pipeline
- **Performance Metrics**: Response times, token usage, and accuracy tracking
- **LLM Monitoring**: OpenAI and Gemini API usage and performance
- **Evaluation Metrics**: Retrieval and generation quality metrics
- **Real-time Dashboard**: Interactive UI for monitoring and analysis

## Prerequisites

- Docker and Docker Compose installed
- Python 3.13+ environment
- Access to the project's `.env` file
- Basic understanding of observability concepts

## Local Setup

### 1. Navigate to Phoenix Directory

```bash
cd services/monitoring
```

### 2. Start Phoenix with Docker Compose

```bash
# Start Phoenix in detached mode
docker-compose up -d

# Check if Phoenix is running
docker-compose ps

# View logs
docker-compose logs -f phoenix
```

### 3. Verify Installation

```bash
# Check Phoenix health
curl http://localhost:6006/health

# Access the Phoenix UI
open http://localhost:6006
```

## Configuration

### Environment Variables

Add the following variables to your `.env` file in the project root:

```env
# Phoenix Configuration
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
PHOENIX_GRPC_ENDPOINT=localhost:4317

# Instrumentation Settings
INSTRUMENT_OPENAI=true
INSTRUMENT_GEMINI=true
INSTRUMENT_LLAMA_INDEX=true

# Optional: Prometheus metrics
PHOENIX_PROMETHEUS_ENABLED=true
PHOENIX_PROMETHEUS_PORT=9090
```

### Docker Compose Configuration

The `docker-compose.yml` file includes:

```yaml
services:
  phoenix:
    image: arizephoenix/phoenix:latest
    ports:
      - "6006:6006"  # UI and OTLP HTTP collector
      - "4317:4317"  # OTLP gRPC collector
      - "9090:9090"  # Prometheus metrics (optional)
    environment:
      - PHOENIX_WORKING_DIR=/mnt/data
    volumes:
      - phoenix_data:/mnt/data
    env_file:
      - ../../.env
```

## Integration with RAG API

### 1. Install Phoenix Python Package

```bash
# Add to your pyproject.toml
phoenix = "^4.0.0"
```

### 2. Basic Instrumentation

```python
# In your RAG service
import phoenix as px
from phoenix.trace import trace

class RAGService:
    @trace
    def answer_question(self, question: str):
        # Your existing RAG code
        # Phoenix will automatically capture metrics
        pass
```

### 3. Advanced Instrumentation

```python
# Custom tracing for specific operations
from phoenix.trace import trace, set_attributes

@trace
def retrieve_documents(self, query: str):
    with trace("embedding_generation"):
        embedding = self.embedding_service.generate_embedding(query)

    with trace("vector_search"):
        results = self.qdrant_service.search(embedding)

    set_attributes({
        "query_length": len(query),
        "results_count": len(results),
        "search_time": time.time() - start_time
    })

    return results
```

## Advanced Tracing Features

The law processing system includes advanced Phoenix tracing features for comprehensive observability:

### Context Managers vs Decorators

The system uses **context managers** instead of decorators for better control and granular tracing:

```python
from opentelemetry.trace import SpanKind

# Using context manager for custom spans
with phoenix_span("operation_name", SpanKind.INTERNAL, {"param": "value"}):
    # Your operation code here
    pass
```

### Automatic Session Grouping

All spans from a single execution are automatically grouped under a session with unique identifiers.

## Session Management

The system implements automatic session management to group all spans from a single execution:

### Session Features

- **Unique Session ID**: Each execution gets a UUID for identification
- **Automatic Grouping**: All spans are grouped under a root session span
- **Session Attributes**: Each span includes session information
- **Duration Tracking**: Total execution time is tracked at session level

### Session Structure

```text
execution_session (SERVER) 🔵 [ROOT SESSION]
├── session.id: "550e8400-e29b-41d4-a716-446655440000"
├── session.start_time: "2024-01-15T10:30:00.123456"
├── session.type: "law_processing"
├── session.version: "1.0"
│
└── main_process (SERVER) 🔵 [CHILD OF SESSION]
    ├── session.id: "550e8400-e29b-41d4-a716-446655440000"
    ├── execution.timestamp: "2024-01-15T10:30:00.234567"
    │
    └── All operation spans with session.id attribute
```

### Session Benefits

1. **Visual Grouping**: All spans from one execution appear grouped in Phoenix
2. **Easy Filtering**: Filter by `session.id` to see specific executions
3. **Performance Analysis**: Compare different executions easily
4. **Complete Traceability**: Track the full lifecycle of each execution

### Using Sessions in Phoenix

**Filter by Session:**

```text
session.id = "550e8400-e29b-41d4-a716-446655440000"
```

**View Session Duration:**

- The root `execution_session` span shows total execution time
- Compare durations across different executions

## Span Kinds and Categorization

The system uses OpenTelemetry Span Kinds for better visualization and categorization:

### Span Kind Types

#### 🔵 **SpanKind.SERVER**

**Purpose**: Main operations that coordinate other operations

- `main_process` - Main application process
- `process_law_local` - Complete local processing
- `process_law_gcs` - Complete GCS processing

#### 🟢 **SpanKind.CLIENT**

**Purpose**: Operations that make external calls

- `download_law_page` - Download from external URL

#### 🟡 **SpanKind.PRODUCER**

**Purpose**: Operations that send data to external systems

- `save_parsed_json_gcs` - Save to Google Cloud Storage
- `upload_file_to_gcs` - Upload files to GCS

#### ⚪ **SpanKind.INTERNAL**

**Purpose**: Internal data processing operations

- `extract_metadata` - Extract law metadata
- `extract_articles` - Segment articles
- `parse_law_text` - Process complete text
- `extract_text_from_html` - Extract clean text from HTML
- `save_parsed_json_local` - Save files locally

### Benefits of Span Kinds

1. **Better Visualization**: Different icons and colors for each operation type
2. **Clear Categorization**: Easy identification of operation types
3. **Performance Analysis**: Identify where resources are spent by type
4. **Improved Debugging**: Easier problem identification
5. **Type-specific Metrics**: Generate metrics by operation type

### Span Hierarchy

```text
main_process (SERVER) 🔵
├── process_law_local/process_law_gcs (SERVER) 🔵
    ├── download_law_page (CLIENT) 🟢
    ├── extract_text_from_html (INTERNAL) ⚪
    ├── parse_law_text (INTERNAL) ⚪
    │   ├── extract_metadata (INTERNAL) ⚪
    │   └── extract_articles (INTERNAL) ⚪
    ├── save_parsed_json_local (INTERNAL) ⚪ [local mode]
    ├── upload_file_to_gcs (PRODUCER) 🟡 [GCS mode]
    └── save_parsed_json_gcs (PRODUCER) 🟡 [GCS mode]
```

### Attributes by Span Type

**CLIENT Spans:**

- `url` - External call URL
- `output_path` - Local output path

**PRODUCER Spans:**

- `bucket_name` - GCS bucket name
- `filename` - File name
- `articles_count` - Number of processed articles

**INTERNAL Spans:**

- `lines_count` - Number of processed lines
- `text_length` - Text length
- `html_path` - HTML file path
- `articles_count` - Number of extracted articles

**SERVER Spans:**

- `mode` - Operation mode (local/gcs)
- `url` - Law URL
- `bucket_name` - Bucket name (GCS mode only)
- `raw_filename` - HTML filename
- `processed_filename` - JSON filename
- `output_root` - Output root directory (local mode only)
- `use_local_credentials` - Use local credentials (GCS mode only)

## Monitoring Features

### 1. Trace Analysis

Phoenix provides detailed traces showing:

- Request flow through the RAG pipeline
- Time spent in each component
- Token usage and costs
- Error rates and exceptions

### 2. Performance Metrics

Track key performance indicators:

- **Response Time**: End-to-end request processing time
- **Token Usage**: Tokens consumed per request
- **Throughput**: Requests per minute
- **Error Rate**: Percentage of failed requests

### 3. LLM Monitoring

Monitor LLM providers:

- **OpenAI**: API calls, token usage, costs
- **Google Gemini**: API calls, token usage, costs
- **Model Performance**: Response quality and consistency

### 4. Evaluation Metrics

Track RAG system quality:

- **Retrieval Accuracy**: Relevance of retrieved documents
- **Generation Quality**: Response accuracy and coherence
- **Reranking Effectiveness**: Impact of reranking on results

## Production Deployment

### Option 1: Phoenix Cloud (Recommended)

For production, use Phoenix Cloud to avoid infrastructure overhead:

1. **Sign up** at [Phoenix Cloud](https://arize.com/phoenix)
2. **Get API key** from your dashboard
3. **Update environment variables**:

```env
PHOENIX_COLLECTOR_ENDPOINT=https://your-instance.phoenix.arize.com/v1/traces
PHOENIX_API_KEY=your_api_key_here
```

### Option 2: Self-Hosted

For self-hosted deployment, see the [Phoenix documentation](https://arize.com/docs/phoenix/self-hosting/).

## Troubleshooting

### Common Issues

#### Phoenix Won't Start

```bash
# Check Docker status
docker info

# Check port availability
netstat -tulpn | grep :6006

# Restart Phoenix
docker-compose down
docker-compose up -d
```

#### No Traces Appearing

1. **Check environment variables**:

   ```bash
   echo $PHOENIX_COLLECTOR_ENDPOINT
   ```

2. **Verify instrumentation**:

   ```python
   import phoenix as px
   print(px.get_tracer())
   ```

3. **Check network connectivity**:

   ```bash
   curl http://localhost:6006/health
   ```

#### High Memory Usage

```bash
# Monitor resource usage
docker stats phoenix

# Adjust memory limits in docker-compose.yml
services:
  phoenix:
    mem_limit: 2g
```

### Logs and Debugging

```bash
# View Phoenix logs
docker-compose logs phoenix

# Follow logs in real-time
docker-compose logs -f phoenix

# Check specific service logs
docker-compose logs phoenix | grep ERROR
```

## Best Practices

1. **Start with Local Development**: Use local Phoenix for development and testing
2. **Use Phoenix Cloud for Production**: Avoid infrastructure overhead
3. **Instrument Key Operations**: Focus on critical paths in your RAG pipeline
4. **Monitor Resource Usage**: Keep an eye on memory and CPU usage
5. **Set Up Alerts**: Configure alerts for critical metrics
6. **Regular Cleanup**: Clean up old traces to manage storage

---

# Guía de Phoenix

Esta guía proporciona instrucciones completas para configurar y usar Phoenix para observabilidad en tiempo real y evaluación del sistema RAG. Phoenix es una plataforma de observabilidad de código abierto diseñada específicamente para aplicaciones LLM.

## Tabla de Contenidos

- [Resumen](#resumen)
- [Prerrequisitos](#prerrequisitos)
- [Configuración Local](#configuración-local)
- [Configuración](#configuración)
- [Integración con API RAG](#integración-con-api-rag)
- [Características Avanzadas de Tracing](#características-avanzadas-de-tracing)
- [Gestión de Sesiones](#gestión-de-sesiones)
- [Tipos de Spans y Categorización](#tipos-de-spans-y-categorización)
- [Características de Monitoreo](#características-de-monitoreo)
- [Despliegue en Producción](#despliegue-en-producción)
- [Solución de Problemas](#solución-de-problemas)

## Resumen

Phoenix proporciona observabilidad en tiempo real para aplicaciones LLM, ofreciendo:

- **Análisis de Trazas**: Trazado detallado de solicitudes a través del pipeline RAG
- **Métricas de Rendimiento**: Tiempos de respuesta, uso de tokens y seguimiento de precisión
- **Monitoreo de LLM**: Uso y rendimiento de APIs de OpenAI y Gemini
- **Métricas de Evaluación**: Métricas de calidad de recuperación y generación
- **Dashboard en Tiempo Real**: UI interactiva para monitoreo y análisis

## Prerrequisitos

- Docker y Docker Compose instalados
- Entorno Python 3.13+
- Acceso al archivo `.env` del proyecto
- Comprensión básica de conceptos de observabilidad

## Configuración Local

### 1. Navegar al Directorio de Phoenix

```bash
cd services/monitoring
```

### 2. Iniciar Phoenix con Docker Compose

```bash
# Iniciar Phoenix en modo detached
docker-compose up -d

# Verificar si Phoenix está ejecutándose
docker-compose ps

# Ver logs
docker-compose logs -f phoenix
```

### 3. Verificar la Instalación

```bash
# Verificar salud de Phoenix
curl http://localhost:6006/health

# Acceder a la UI de Phoenix
open http://localhost:6006
```

## Configuración

### Variables de Entorno

Agrega las siguientes variables a tu archivo `.env` en la raíz del proyecto:

```env
# Configuración de Phoenix
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
PHOENIX_GRPC_ENDPOINT=localhost:4317

# Configuraciones de Instrumentación
INSTRUMENT_OPENAI=true
INSTRUMENT_GEMINI=true
INSTRUMENT_LLAMA_INDEX=true

# Opcional: métricas de Prometheus
PHOENIX_PROMETHEUS_ENABLED=true
PHOENIX_PROMETHEUS_PORT=9090
```

### Configuración de Docker Compose

El archivo `docker-compose.yml` incluye:

```yaml
services:
  phoenix:
    image: arizephoenix/phoenix:latest
    ports:
      - "6006:6006"  # UI y colector OTLP HTTP
      - "4317:4317"  # Colector OTLP gRPC
      - "9090:9090"  # Métricas de Prometheus (opcional)
    environment:
      - PHOENIX_WORKING_DIR=/mnt/data
    volumes:
      - phoenix_data:/mnt/data
    env_file:
      - ../../.env
```

## Integración con API RAG

### 1. Instalar Paquete Python de Phoenix

```bash
# Agregar a tu pyproject.toml
phoenix = "^4.0.0"
```

### 2. Instrumentación Básica

```python
# En tu servicio RAG
import phoenix as px
from phoenix.trace import trace

class RAGService:
    @trace
    def answer_question(self, question: str):
        # Tu código RAG existente
        # Phoenix capturará automáticamente las métricas
        pass
```

### 3. Instrumentación Avanzada

```python
# Trazado personalizado para operaciones específicas
from phoenix.trace import trace, set_attributes

@trace
def retrieve_documents(self, query: str):
    with trace("embedding_generation"):
        embedding = self.embedding_service.generate_embedding(query)

    with trace("vector_search"):
        results = self.qdrant_service.search(embedding)

    set_attributes({
        "query_length": len(query),
        "results_count": len(results),
        "search_time": time.time() - start_time
    })

    return results
```

## Características Avanzadas de Tracing

El sistema de procesamiento de leyes incluye características avanzadas de tracing en Phoenix para observabilidad integral:

### Context Managers vs Decoradores

El sistema usa **context managers** en lugar de decoradores para mejor control y tracing granular:

```python
from opentelemetry.trace import SpanKind

# Usando context manager para spans personalizados
with phoenix_span("nombre_operacion", SpanKind.INTERNAL, {"param": "valor"}):
    # Tu código de operación aquí
    pass
```

### Agrupación Automática de Sesiones

Todos los spans de una sola ejecución se agrupan automáticamente bajo una sesión con identificadores únicos.

## Gestión de Sesiones

El sistema implementa gestión automática de sesiones para agrupar todos los spans de una sola ejecución:

### Características de Sesión

- **ID de Sesión Único**: Cada ejecución obtiene un UUID para identificación
- **Agrupación Automática**: Todos los spans se agrupan bajo un span de sesión raíz
- **Atributos de Sesión**: Cada span incluye información de sesión
- **Seguimiento de Duración**: El tiempo total de ejecución se rastrea a nivel de sesión

### Estructura de Sesión

```text
execution_session (SERVER) 🔵 [SESIÓN RAÍZ]
├── session.id: "550e8400-e29b-41d4-a716-446655440000"
├── session.start_time: "2024-01-15T10:30:00.123456"
├── session.type: "law_processing"
├── session.version: "1.0"
│
└── main_process (SERVER) 🔵 [HIJO DE SESIÓN]
    ├── session.id: "550e8400-e29b-41d4-a716-446655440000"
    ├── execution.timestamp: "2024-01-15T10:30:00.234567"
    │
    └── Todos los spans de operación con atributo session.id
```

### Beneficios de Sesión

1. **Agrupación Visual**: Todos los spans de una ejecución aparecen agrupados en Phoenix
2. **Filtrado Fácil**: Filtrar por `session.id` para ver ejecuciones específicas
3. **Análisis de Rendimiento**: Comparar diferentes ejecuciones fácilmente
4. **Trazabilidad Completa**: Rastrear el ciclo de vida completo de cada ejecución

### Usando Sesiones en Phoenix

**Filtrar por Sesión:**

```text
session.id = "550e8400-e29b-41d4-a716-446655440000"
```

**Ver Duración de Sesión:**

- El span raíz `execution_session` muestra el tiempo total de ejecución
- Comparar duraciones entre diferentes ejecuciones

## Tipos de Spans y Categorización

El sistema usa Span Kinds de OpenTelemetry para mejor visualización y categorización:

### Tipos de Span Kind

#### 🔵 **SpanKind.SERVER**

**Propósito**: Operaciones principales que coordinan otras operaciones

- `main_process` - Proceso principal de la aplicación
- `process_law_local` - Procesamiento local completo
- `process_law_gcs` - Procesamiento GCS completo

#### 🟢 **SpanKind.CLIENT**

**Propósito**: Operaciones que realizan llamadas externas

- `download_law_page` - Descarga desde URL externa

#### 🟡 **SpanKind.PRODUCER**

**Propósito**: Operaciones que envían datos a sistemas externos

- `save_parsed_json_gcs` - Guardar en Google Cloud Storage
- `upload_file_to_gcs` - Subir archivos a GCS

#### ⚪ **SpanKind.INTERNAL**

**Propósito**: Operaciones de procesamiento interno de datos

- `extract_metadata` - Extraer metadatos de la ley
- `extract_articles` - Segmentar artículos
- `parse_law_text` - Procesar texto completo
- `extract_text_from_html` - Extraer texto limpio del HTML
- `save_parsed_json_local` - Guardar archivos localmente

### Beneficios de Span Kinds

1. **Mejor Visualización**: Diferentes iconos y colores para cada tipo de operación
2. **Categorización Clara**: Identificación fácil de tipos de operación
3. **Análisis de Rendimiento**: Identificar dónde se gastan recursos por tipo
4. **Debugging Mejorado**: Identificación más fácil de problemas
5. **Métricas Específicas por Tipo**: Generar métricas por tipo de operación

### Jerarquía de Spans

```text
main_process (SERVER) 🔵
├── process_law_local/process_law_gcs (SERVER) 🔵
    ├── download_law_page (CLIENT) 🟢
    ├── extract_text_from_html (INTERNAL) ⚪
    ├── parse_law_text (INTERNAL) ⚪
    │   ├── extract_metadata (INTERNAL) ⚪
    │   └── extract_articles (INTERNAL) ⚪
    ├── save_parsed_json_local (INTERNAL) ⚪ [modo local]
    ├── upload_file_to_gcs (PRODUCER) 🟡 [modo GCS]
    └── save_parsed_json_gcs (PRODUCER) 🟡 [modo GCS]
```

### Atributos por Tipo de Span

**Spans CLIENT:**

- `url` - URL de llamada externa
- `output_path` - Ruta de salida local

**Spans PRODUCER:**

- `bucket_name` - Nombre del bucket de GCS
- `filename` - Nombre del archivo
- `articles_count` - Número de artículos procesados

**Spans INTERNAL:**

- `lines_count` - Número de líneas procesadas
- `text_length` - Longitud del texto
- `html_path` - Ruta del archivo HTML
- `articles_count` - Número de artículos extraídos

**Spans SERVER:**

- `mode` - Modo de operación (local/gcs)
- `url` - URL de la ley
- `bucket_name` - Nombre del bucket (solo modo GCS)
- `raw_filename` - Nombre del archivo HTML
- `processed_filename` - Nombre del archivo JSON
- `output_root` - Directorio raíz de salida (solo modo local)
- `use_local_credentials` - Usar credenciales locales (solo modo GCS)

## Características de Monitoreo

### 1. Análisis de Trazas

Phoenix proporciona trazas detalladas mostrando:

- Flujo de solicitudes a través del pipeline RAG
- Tiempo gastado en cada componente
- Uso de tokens y costos
- Tasas de error y excepciones

### 2. Métricas de Rendimiento

Rastrea indicadores clave de rendimiento:

- **Tiempo de Respuesta**: Tiempo de procesamiento de solicitudes de extremo a extremo
- **Uso de Tokens**: Tokens consumidos por solicitud
- **Throughput**: Solicitudes por minuto
- **Tasa de Error**: Porcentaje de solicitudes fallidas

### 3. Monitoreo de LLM

Monitorea proveedores de LLM:

- **OpenAI**: Llamadas API, uso de tokens, costos
- **Google Gemini**: Llamadas API, uso de tokens, costos
- **Rendimiento del Modelo**: Calidad y consistencia de respuestas

### 4. Métricas de Evaluación

Rastrea la calidad del sistema RAG:

- **Precisión de Recuperación**: Relevancia de documentos recuperados
- **Calidad de Generación**: Precisión y coherencia de respuestas
- **Efectividad de Reranking**: Impacto del reranking en resultados

## Despliegue en Producción

### Opción 1: Phoenix Cloud (Recomendado)

Para producción, usa Phoenix Cloud para evitar sobrecarga de infraestructura:

1. **Regístrate** en [Phoenix Cloud](https://arize.com/phoenix)
2. **Obtén clave API** de tu dashboard
3. **Actualiza variables de entorno**:

```env
PHOENIX_COLLECTOR_ENDPOINT=https://your-instance.phoenix.arize.com/v1/traces
PHOENIX_API_KEY=tu_clave_api_aqui
```

### Opción 2: Auto-hospedado

Para despliegue auto-hospedado, consulta la [documentación de Phoenix](https://arize.com/docs/phoenix/self-hosting/).

## Solución de Problemas

### Problemas Comunes

#### Phoenix No Inicia

```bash
# Verificar estado de Docker
docker info

# Verificar disponibilidad de puertos
netstat -tulpn | grep :6006

# Reiniciar Phoenix
docker-compose down
docker-compose up -d
```

#### No Aparecen Trazas

1. **Verificar variables de entorno**:

   ```bash
   echo $PHOENIX_COLLECTOR_ENDPOINT
   ```

2. **Verificar instrumentación**:

   ```python
   import phoenix as px
   print(px.get_tracer())
   ```

3. **Verificar conectividad de red**:

   ```bash
   curl http://localhost:6006/health
   ```

#### Alto Uso de Memoria

```bash
# Monitorear uso de recursos
docker stats phoenix

# Ajustar límites de memoria en docker-compose.yml
services:
  phoenix:
    mem_limit: 2g
```

### Logs y Depuración

```bash
# Ver logs de Phoenix
docker-compose logs phoenix

# Seguir logs en tiempo real
docker-compose logs -f phoenix

# Verificar logs específicos del servicio
docker-compose logs phoenix | grep ERROR
```

## Mejores Prácticas

1. **Comenzar con Desarrollo Local**: Usa Phoenix local para desarrollo y pruebas
2. **Usar Phoenix Cloud para Producción**: Evita sobrecarga de infraestructura
3. **Instrumentar Operaciones Clave**: Enfócate en rutas críticas en tu pipeline RAG
4. **Monitorear Uso de Recursos**: Mantén un ojo en el uso de memoria y CPU
5. **Configurar Alertas**: Configura alertas para métricas críticas
6. **Limpieza Regular**: Limpia trazas antiguas para gestionar almacenamiento
