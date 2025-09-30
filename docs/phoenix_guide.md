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
