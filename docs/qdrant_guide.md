<div align="center">

**Language / Idioma:**
[🇺🇸 English](#table-of-contents) | [🇪🇸 Español](#tabla-de-contenidos)

</div>

---

# Qdrant Vector Database Guide

This guide provides comprehensive information about using Qdrant vector database in the Lus Laboris project for semantic search and retrieval of Paraguayan labor law information.

## Table of Contents

- [Overview](#overview)
- [Installation and Setup](#installation-and-setup)
- [Configuration](#configuration)
- [Basic Operations](#basic-operations)
- [Advanced Features](#advanced-features)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

Qdrant is a vector similarity search engine and vector database that enables efficient storage and retrieval of high-dimensional vectors. In the Lus Laboris project, Qdrant is used to:

- Store embeddings of Paraguayan labor law articles
- Enable semantic search for legal queries
- Support RAG (Retrieval-Augmented Generation) functionality
- Provide fast similarity search capabilities

### Key Features

- **High Performance**: Optimized for vector similarity search
- **Scalability**: Horizontal scaling capabilities
- **Filtering**: Advanced filtering options for metadata
- **Multiple Distance Metrics**: Support for cosine, dot product, and Euclidean distances
- **REST API**: Easy integration with Python applications

## Installation and Setup

### Using Docker (Recommended)

The easiest way to run Qdrant is using Docker:

```bash
# Pull the official Qdrant image
docker pull qdrant/qdrant

# Run Qdrant container
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### Using Docker Compose

The project includes a `docker-compose.yml` file in the `src/vectorstore` directory:

```bash
cd src/vectorstore
docker-compose up -d
```

### Python Client Installation

```bash
pip install qdrant-client
# or using uv
uv add qdrant-client
```

## Configuration

### Environment Variables

Set the following environment variables in your `.env` file located in the project root directory:

```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key_here  # Optional for local development
```

> **Note**: The `.env` file should be placed in the project root directory (`lus-laboris-py/.env`), not in the `docs/` directory.

### Connection Setup

```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Connect to Qdrant
client = QdrantClient(
    url="http://localhost:6333",
    api_key="your_api_key"  # Optional
)
```

## Basic Operations

### Creating a Collection

```python
from qdrant_client.http.models import Distance, VectorParams

# Create a collection for labor law articles
client.create_collection(
    collection_name="labor_law_articles",
    vectors_config=VectorParams(
        size=384,  # Dimension of your embeddings
        distance=Distance.COSINE  # Distance metric
    )
)
```

### Inserting Documents

```python
from qdrant_client.http.models import PointStruct

# Prepare documents with embeddings
points = [
    PointStruct(
        id=1,
        vector=[0.1, 0.2, 0.3, ...],  # Your embedding vector
        payload={
            "text": "Article content here",
            "article_number": 1,
            "chapter": "General Provisions",
            "metadata": {...}
        }
    )
]

# Insert points into collection
client.upsert(
    collection_name="labor_law_articles",
    points=points
)
```

### Searching Documents

```python
# Search for similar documents
search_results = client.query_points(
    collection_name="labor_law_articles",
    query=[0.1, 0.2, 0.3, ...],  # Query embedding
    limit=5,  # Number of results to return
    with_payload=True,  # Include payload in results
    with_vectors=False  # Exclude vectors from results
)

# Process results
for result in search_results.points:
    print(f"Score: {result.score}")
    print(f"Content: {result.payload['text']}")
    print(f"Article: {result.payload['article_number']}")
```

### Filtering Results

```python
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

# Search with filters
search_results = client.query_points(
    collection_name="labor_law_articles",
    query=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="chapter",
                match=MatchValue(value="General Provisions")
            )
        ]
    ),
    limit=5
)
```

## Advanced Features

### Batch Operations

```python
# Batch insert multiple documents
def batch_insert_documents(documents, embeddings, batch_size=100):
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]
        
        points = [
            PointStruct(
                id=j,
                vector=embedding,
                payload=doc
            )
            for j, (doc, embedding) in enumerate(zip(batch_docs, batch_embeddings))
        ]
        
        client.upsert(
            collection_name="labor_law_articles",
            points=points
        )
```

### Collection Management

```python
# List all collections
collections = client.get_collections()
print(collections)

# Get collection info
collection_info = client.get_collection("labor_law_articles")
print(collection_info)

# Delete collection
client.delete_collection("labor_law_articles")
```

### Updating Documents

```python
# Update document payload
client.set_payload(
    collection_name="labor_law_articles",
    payload={
        "updated_field": "new_value"
    },
    points=[1, 2, 3]  # Point IDs to update
)

# Delete specific points
client.delete(
    collection_name="labor_law_articles",
    points_selector=[1, 2, 3]
)
```

## Performance Optimization

### Index Configuration

```python
# Create collection with optimized settings
client.create_collection(
    collection_name="optimized_collection",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE,
        on_disk=True  # Store vectors on disk for large collections
    ),
    optimizers_config={
        "default_segment_number": 2,
        "max_segment_size": 20000,
        "memmap_threshold": 50000,
        "indexing_threshold": 20000
    }
)
```

### Search Optimization

```python
# Use filters to reduce search space
search_results = client.query_points(
    collection_name="labor_law_articles",
    query=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="article_type",
                match=MatchValue(value="main_article")
            )
        ]
    ),
    limit=10,
    score_threshold=0.7  # Minimum similarity score
)
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if Qdrant is running
   docker ps | grep qdrant
   
   # Check logs
   docker logs qdrant_container_name
   ```

2. **Out of Memory**
   ```python
   # Use on_disk storage for large collections
   vectors_config=VectorParams(
       size=384,
       distance=Distance.COSINE,
       on_disk=True
   )
   ```

3. **Slow Search Performance**
   - Ensure proper indexing
   - Use filters to reduce search space
   - Consider using smaller batch sizes for inserts

### Monitoring

```python
# Check collection statistics
stats = client.get_collection("labor_law_articles")
print(f"Points count: {stats.points_count}")
print(f"Indexed vectors: {stats.indexed_vectors_count}")

# Check cluster status
cluster_info = client.get_cluster_info()
print(cluster_info)
```

## Best Practices

### 1. Collection Design

- Use descriptive collection names
- Choose appropriate distance metrics (cosine for text embeddings)
- Set proper vector dimensions based on your embedding model

### 2. Data Management

- Use batch operations for large datasets
- Implement proper error handling
- Monitor collection size and performance

### 3. Search Optimization

- Use filters to narrow down search space
- Set appropriate score thresholds
- Consider using different collections for different document types

### 4. Security

- Use API keys in production
- Implement proper access controls
- Monitor usage and performance

### 5. Backup and Recovery

```bash
# Backup collection data
docker exec qdrant_container qdrant-cli snapshot create \
    --collection-name labor_law_articles \
    --output-dir /qdrant/snapshots

# Restore from snapshot
docker exec qdrant_container qdrant-cli snapshot restore \
    --collection-name labor_law_articles \
    --input-file /qdrant/snapshots/snapshot.snapshot
```

---

# Guía de Base de Datos Vectorial Qdrant

Esta guía proporciona información integral sobre el uso de la base de datos vectorial Qdrant en el proyecto Lus Laboris para búsqueda semántica y recuperación de información de la ley laboral paraguaya.

## Tabla de Contenidos

- [Resumen](#resumen)
- [Instalación y Configuración](#instalación-y-configuración)
- [Configuración](#configuración-1)
- [Operaciones Básicas](#operaciones-básicas)
- [Características Avanzadas](#características-avanzadas)
- [Optimización de Rendimiento](#optimización-de-rendimiento)
- [Solución de Problemas](#solución-de-problemas)
- [Mejores Prácticas](#mejores-prácticas)

## Resumen

Qdrant es un motor de búsqueda de similitud vectorial y base de datos vectorial que permite el almacenamiento y recuperación eficiente de vectores de alta dimensión. En el proyecto Lus Laboris, Qdrant se utiliza para:

- Almacenar embeddings de artículos de la ley laboral paraguaya
- Habilitar búsqueda semántica para consultas legales
- Soportar funcionalidad RAG (Generación Aumentada por Recuperación)
- Proporcionar capacidades de búsqueda de similitud rápida

### Características Clave

- **Alto Rendimiento**: Optimizado para búsqueda de similitud vectorial
- **Escalabilidad**: Capacidades de escalado horizontal
- **Filtrado**: Opciones de filtrado avanzadas para metadatos
- **Múltiples Métricas de Distancia**: Soporte para distancias coseno, producto punto y euclidiana
- **API REST**: Integración fácil con aplicaciones Python

## Instalación y Configuración

### Usando Docker (Recomendado)

La forma más fácil de ejecutar Qdrant es usando Docker:

```bash
# Descargar la imagen oficial de Qdrant
docker pull qdrant/qdrant

# Ejecutar contenedor de Qdrant
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### Usando Docker Compose

El proyecto incluye un archivo `docker-compose.yml` en el directorio `src/vectorstore`:

```bash
cd src/vectorstore
docker-compose up -d
```

### Instalación del Cliente Python

```bash
pip install qdrant-client
# o usando uv
uv add qdrant-client
```

## Configuración

### Variables de Entorno

Configura las siguientes variables de entorno en tu archivo `.env` ubicado en el directorio raíz del proyecto:

```env
# Configuración de Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=tu_clave_api_aqui  # Opcional para desarrollo local
```

> **Nota**: El archivo `.env` debe colocarse en el directorio raíz del proyecto (`lus-laboris-py/.env`), no en el directorio `docs/`.

### Configuración de Conexión

```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Conectar a Qdrant
client = QdrantClient(
    url="http://localhost:6333",
    api_key="tu_clave_api"  # Opcional
)
```

## Operaciones Básicas

### Crear una Colección

```python
from qdrant_client.http.models import Distance, VectorParams

# Crear una colección para artículos de ley laboral
client.create_collection(
    collection_name="labor_law_articles",
    vectors_config=VectorParams(
        size=384,  # Dimensión de tus embeddings
        distance=Distance.COSINE  # Métrica de distancia
    )
)
```

### Insertar Documentos

```python
from qdrant_client.http.models import PointStruct

# Preparar documentos con embeddings
points = [
    PointStruct(
        id=1,
        vector=[0.1, 0.2, 0.3, ...],  # Tu vector de embedding
        payload={
            "text": "Contenido del artículo aquí",
            "article_number": 1,
            "chapter": "Disposiciones Generales",
            "metadata": {...}
        }
    )
]

# Insertar puntos en la colección
client.upsert(
    collection_name="labor_law_articles",
    points=points
)
```

### Buscar Documentos

```python
# Buscar documentos similares
search_results = client.query_points(
    collection_name="labor_law_articles",
    query=[0.1, 0.2, 0.3, ...],  # Embedding de consulta
    limit=5,  # Número de resultados a devolver
    with_payload=True,  # Incluir payload en resultados
    with_vectors=False  # Excluir vectores de resultados
)

# Procesar resultados
for result in search_results.points:
    print(f"Puntuación: {result.score}")
    print(f"Contenido: {result.payload['text']}")
    print(f"Artículo: {result.payload['article_number']}")
```

### Filtrar Resultados

```python
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

# Buscar con filtros
search_results = client.query_points(
    collection_name="labor_law_articles",
    query=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="chapter",
                match=MatchValue(value="Disposiciones Generales")
            )
        ]
    ),
    limit=5
)
```

## Características Avanzadas

### Operaciones por Lotes

```python
# Insertar múltiples documentos por lotes
def batch_insert_documents(documents, embeddings, batch_size=100):
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]
        
        points = [
            PointStruct(
                id=j,
                vector=embedding,
                payload=doc
            )
            for j, (doc, embedding) in enumerate(zip(batch_docs, batch_embeddings))
        ]
        
        client.upsert(
            collection_name="labor_law_articles",
            points=points
        )
```

### Gestión de Colecciones

```python
# Listar todas las colecciones
collections = client.get_collections()
print(collections)

# Obtener información de colección
collection_info = client.get_collection("labor_law_articles")
print(collection_info)

# Eliminar colección
client.delete_collection("labor_law_articles")
```

### Actualizar Documentos

```python
# Actualizar payload de documento
client.set_payload(
    collection_name="labor_law_articles",
    payload={
        "updated_field": "nuevo_valor"
    },
    points=[1, 2, 3]  # IDs de puntos a actualizar
)

# Eliminar puntos específicos
client.delete(
    collection_name="labor_law_articles",
    points_selector=[1, 2, 3]
)
```

## Optimización de Rendimiento

### Configuración de Índices

```python
# Crear colección con configuraciones optimizadas
client.create_collection(
    collection_name="optimized_collection",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE,
        on_disk=True  # Almacenar vectores en disco para colecciones grandes
    ),
    optimizers_config={
        "default_segment_number": 2,
        "max_segment_size": 20000,
        "memmap_threshold": 50000,
        "indexing_threshold": 20000
    }
)
```

### Optimización de Búsqueda

```python
# Usar filtros para reducir espacio de búsqueda
search_results = client.query_points(
    collection_name="labor_law_articles",
    query=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="article_type",
                match=MatchValue(value="main_article")
            )
        ]
    ),
    limit=10,
    score_threshold=0.7  # Puntuación mínima de similitud
)
```

## Solución de Problemas

### Problemas Comunes

1. **Conexión Rechazada**
   ```bash
   # Verificar si Qdrant está ejecutándose
   docker ps | grep qdrant
   
   # Verificar logs
   docker logs nombre_contenedor_qdrant
   ```

2. **Memoria Insuficiente**
   ```python
   # Usar almacenamiento en disco para colecciones grandes
   vectors_config=VectorParams(
       size=384,
       distance=Distance.COSINE,
       on_disk=True
   )
   ```

3. **Rendimiento Lento de Búsqueda**
   - Asegurar indexación adecuada
   - Usar filtros para reducir espacio de búsqueda
   - Considerar usar tamaños de lote más pequeños para inserciones

### Monitoreo

```python
# Verificar estadísticas de colección
stats = client.get_collection("labor_law_articles")
print(f"Conteo de puntos: {stats.points_count}")
print(f"Vectores indexados: {stats.indexed_vectors_count}")

# Verificar estado del cluster
cluster_info = client.get_cluster_info()
print(cluster_info)
```

## Mejores Prácticas

### 1. Diseño de Colecciones

- Usar nombres descriptivos para colecciones
- Elegir métricas de distancia apropiadas (coseno para embeddings de texto)
- Establecer dimensiones de vector apropiadas basadas en tu modelo de embedding

### 2. Gestión de Datos

- Usar operaciones por lotes para conjuntos de datos grandes
- Implementar manejo adecuado de errores
- Monitorear tamaño y rendimiento de colecciones

### 3. Optimización de Búsqueda

- Usar filtros para reducir espacio de búsqueda
- Establecer umbrales de puntuación apropiados
- Considerar usar diferentes colecciones para diferentes tipos de documentos

### 4. Seguridad

- Usar claves API en producción
- Implementar controles de acceso adecuados
- Monitorear uso y rendimiento

### 5. Respaldo y Recuperación

```bash
# Respaldar datos de colección
docker exec qdrant_container qdrant-cli snapshot create \
    --collection-name labor_law_articles \
    --output-dir /qdrant/snapshots

# Restaurar desde snapshot
docker exec qdrant_container qdrant-cli snapshot restore \
    --collection-name labor_law_articles \
    --input-file /qdrant/snapshots/snapshot.snapshot
```
