
<div align="center">

**Language / Idioma:**
[🇺🇸 English](#contents) | [🇪🇸 Español](#contenidos)

</div>

---
# Vectorstore

This folder contains scripts for loading, managing, and querying the Qdrant vector database used for semantic search and retrieval of Paraguayan labor law information.

## Contents

- `docker-compose.yml` - Docker Compose configuration for running Qdrant locally
- `README.md` - This documentation file

## Quick Start

### Using Docker Compose

1. Navigate to this directory:
   ```bash
   cd services/vectordb
   ```

2. Start Qdrant:
   ```bash
   docker-compose up -d
   ```

3. Verify Qdrant is running:
   ```bash
   curl http://localhost:6333/collections
   ```

### Configuration

Set the following environment variables in your `.env` file located in the project root directory:

```env
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key_here  # Optional for local development
```

> **Note**: The `.env` file should be placed in the project root directory (`lus-laboris-py/.env`), not in the `src/vectorstore/` directory.

## Documentation

For comprehensive Qdrant usage documentation, see:
- [Qdrant Guide](../../docs/qdrant_guide.md) - Complete guide for using Qdrant in this project

## Production Deployment

**Personal Projects**: Use [Qdrant Cloud](https://cloud.qdrant.io/) (recommended)
- No infrastructure overhead
- Cost-effective for personal use
- Easy setup and management
- Automatic scaling and updates

**Enterprise**: Use self-hosted deployment
- Full control over infrastructure
- Enhanced security compliance
- Custom configurations
- On-premises data control

## Features

- **Semantic Search**: Store and search labor law articles using vector embeddings
- **Metadata Filtering**: Filter results by article metadata (chapter, book, etc.)
- **Scalable**: Horizontal scaling capabilities for large document collections
- **REST API**: Easy integration with Python applications

## Integration

The vectorstore is integrated with:
- **Embedding Models**: Various sentence-transformers models for generating embeddings
- **RAG System**: Retrieval-Augmented Generation for answering legal queries
- **API Layer**: FastAPI endpoints for search functionality

---



# Vectorstore

Esta carpeta contiene scripts para la carga, gestión y consulta de la base de datos vectorial Qdrant utilizada para búsqueda semántica y recuperación de información de la ley laboral paraguaya.

## Contenidos

- `docker-compose.yml` - Configuración de Docker Compose para ejecutar Qdrant localmente
- `README.md` - Este archivo de documentación

## Inicio Rápido

### Usando Docker Compose

1. Navegar a este directorio:
   ```bash
   cd services/vectordb
   ```

2. Iniciar Qdrant:
   ```bash
   docker-compose up -d
   ```

3. Verificar que Qdrant esté ejecutándose:
   ```bash
   curl http://localhost:6333/collections
   ```

### Configuración

Configura las siguientes variables de entorno en tu archivo `.env` ubicado en el directorio raíz del proyecto:

```env
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=tu_clave_api_aqui  # Opcional para desarrollo local
```

> **Nota**: El archivo `.env` debe colocarse en el directorio raíz del proyecto (`lus-laboris-py/.env`), no en el directorio `src/vectorstore/`.

## Documentación

Para documentación completa del uso de Qdrant, consulta:
- [Guía de Qdrant](../../docs/qdrant_guide.md) - Guía completa para usar Qdrant en este proyecto

## Despliegue en Producción

**Proyectos Personales**: Usa [Qdrant Cloud](https://cloud.qdrant.io/) (recomendado)
- Sin sobrecarga de infraestructura
- Costo-efectivo para uso personal
- Configuración y gestión fáciles
- Escalado y actualizaciones automáticas

**Empresarial**: Usa despliegue auto-hospedado
- Control total sobre la infraestructura
- Cumplimiento de seguridad mejorado
- Configuraciones personalizadas
- Control de datos en las instalaciones

## Características

- **Búsqueda Semántica**: Almacenar y buscar artículos de ley laboral usando embeddings vectoriales
- **Filtrado de Metadatos**: Filtrar resultados por metadatos de artículos (capítulo, libro, etc.)
- **Escalable**: Capacidades de escalado horizontal para grandes colecciones de documentos
- **API REST**: Integración fácil con aplicaciones Python

## Integración

El vectorstore está integrado con:
- **Modelos de Embedding**: Varios modelos de sentence-transformers para generar embeddings
- **Sistema RAG**: Generación Aumentada por Recuperación para responder consultas legales
- **Capa de API**: Endpoints de FastAPI para funcionalidad de búsqueda
