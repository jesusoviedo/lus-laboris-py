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
- [Production Deployment](#production-deployment)
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

## Production Deployment

### Option 1: Qdrant Cloud (Recommended)

For production environments, Qdrant Cloud provides a fully managed vector database service with high availability, automatic scaling, and enterprise features.

#### Getting Started with Qdrant Cloud

1. **Sign up** at [Qdrant Cloud](https://cloud.qdrant.io/)
2. **Create a cluster** in your preferred region
3. **Get API key** from your cluster dashboard
4. **Update environment variables**:

```env
# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster-id.eu-central.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_api_key_here
```

#### Cloud Features

- **High Availability**: 99.9% uptime SLA
- **Automatic Scaling**: Scale up/down based on demand
- **Global Distribution**: Deploy in multiple regions
- **Enterprise Security**: VPC, encryption, access controls
- **Monitoring**: Built-in metrics and alerting
- **Backup & Recovery**: Automated backups and point-in-time recovery

#### Cloud Configuration

```python
# Connect to Qdrant Cloud
client = QdrantClient(
    url="https://your-cluster-id.eu-central.aws.cloud.qdrant.io:6333",
    api_key="your_api_key_here",
    timeout=60,  # Increased timeout for cloud
    prefer_grpc=True  # Use gRPC for better performance
)
```

### Option 2: Self-Hosted Deployment

For organizations requiring full control over their infrastructure, Qdrant can be self-hosted on various platforms.

#### Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant-prod
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
      - ./qdrant_config:/qdrant/config
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__SERVICE__ENABLE_CORS=true
    command: ./qdrant --config-path /qdrant/config/production.yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

volumes:
  qdrant_data:
    driver: local
```

#### Kubernetes Deployment

```yaml
# qdrant-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:latest
        ports:
        - containerPort: 6333
        - containerPort: 6334
        env:
        - name: QDRANT__SERVICE__HTTP_PORT
          value: "6333"
        - name: QDRANT__SERVICE__GRPC_PORT
          value: "6334"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
      volumes:
      - name: qdrant-storage
        persistentVolumeClaim:
          claimName: qdrant-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: qdrant-service
spec:
  selector:
    app: qdrant
  ports:
  - port: 6333
    targetPort: 6333
    name: http
  - port: 6334
    targetPort: 6334
    name: grpc
  type: LoadBalancer
```

#### Production Configuration

```yaml
# production.yaml
service:
  host: 0.0.0.0
  http_port: 6333
  grpc_port: 6334
  enable_cors: true
  max_request_size_mb: 32
  max_workers: 0  # Auto-detect

storage:
  # Use disk storage for production
  storage_path: /qdrant/storage
  snapshots_path: /qdrant/snapshots
  on_disk_payload: true
  on_disk_vectors: true

cluster:
  enabled: true
  p2p:
    port: 6335
  consensus:
    tick_period_ms: 100
    bootstrap_timeout_sec: 5

log_level: INFO
```

### Option 3: Hybrid Approach

Combine Qdrant Cloud for production with local development:

```python
import os
from qdrant_client import QdrantClient

def get_qdrant_client():
    """Get Qdrant client based on environment"""
    if os.getenv("ENVIRONMENT") == "production":
        # Use Qdrant Cloud
        return QdrantClient(
            url=os.getenv("QDRANT_CLOUD_URL"),
            api_key=os.getenv("QDRANT_CLOUD_API_KEY"),
            timeout=60,
            prefer_grpc=True
        )
    else:
        # Use local Qdrant
        return QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=30
        )
```

### Migration from Local to Cloud

1. **Export data** from local Qdrant:
   ```bash
   # Create snapshot
   docker exec qdrant_container qdrant-cli snapshot create \
       --collection-name labor_law_articles \
       --output-dir /qdrant/snapshots
   ```

2. **Import to Qdrant Cloud**:
   ```python
   # Upload to cloud
   client.upload_collection(
       collection_name="labor_law_articles",
       vectors=vectors,
       payload=payloads,
       ids=ids
   )
   ```

3. **Update configuration**:
   ```env
   # Switch to cloud configuration
   QDRANT_URL=https://your-cluster-id.eu-central.aws.cloud.qdrant.io:6333
   QDRANT_API_KEY=your_cloud_api_key
   ```

### Cost Considerations

#### Qdrant Cloud Pricing
- **Free Tier**: 1GB storage, 1M vectors
- **Pay-as-you-go**: Based on storage and compute usage
- **Enterprise**: Custom pricing for large deployments

#### Self-Hosted Costs
- **Infrastructure**: Server costs, storage, networking
- **Maintenance**: DevOps time, monitoring, backups
- **Scaling**: Manual scaling vs automatic

### Security Considerations

#### Qdrant Cloud Security
- **Encryption**: Data encrypted in transit and at rest
- **Access Control**: API key-based authentication
- **Network Security**: VPC and private endpoints
- **Compliance**: SOC 2, GDPR compliant

#### Self-Hosted Security
- **Network Security**: Firewall rules, VPN access
- **Authentication**: API keys, RBAC
- **Encryption**: TLS for data in transit
- **Access Control**: Network-level restrictions

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
- [Despliegue en Producción](#despliegue-en-producción)
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

## Despliegue en Producción

### Opción 1: Qdrant Cloud (Recomendado)

Para entornos de producción, Qdrant Cloud proporciona un servicio de base de datos vectorial completamente gestionado con alta disponibilidad, escalado automático y características empresariales.

#### Comenzando con Qdrant Cloud

1. **Regístrate** en [Qdrant Cloud](https://cloud.qdrant.io/)
2. **Crea un cluster** en tu región preferida
3. **Obtén la clave API** desde tu dashboard del cluster
4. **Actualiza las variables de entorno**:

```env
# Configuración de Qdrant Cloud
QDRANT_URL=https://your-cluster-id.eu-central.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=tu_clave_api_aqui
```

#### Características de la Nube

- **Alta Disponibilidad**: SLA de 99.9% de tiempo de actividad
- **Escalado Automático**: Escalar hacia arriba/abajo según la demanda
- **Distribución Global**: Desplegar en múltiples regiones
- **Seguridad Empresarial**: VPC, encriptación, controles de acceso
- **Monitoreo**: Métricas integradas y alertas
- **Respaldo y Recuperación**: Respaldos automatizados y recuperación punto en el tiempo

#### Configuración de la Nube

```python
# Conectar a Qdrant Cloud
client = QdrantClient(
    url="https://your-cluster-id.eu-central.aws.cloud.qdrant.io:6333",
    api_key="tu_clave_api_aqui",
    timeout=60,  # Timeout aumentado para la nube
    prefer_grpc=True  # Usar gRPC para mejor rendimiento
)
```

### Opción 2: Despliegue Auto-hospedado

Para organizaciones que requieren control total sobre su infraestructura, Qdrant puede ser auto-hospedado en varias plataformas.

#### Docker Compose para Producción

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant-prod
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
      - ./qdrant_config:/qdrant/config
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__SERVICE__ENABLE_CORS=true
    command: ./qdrant --config-path /qdrant/config/production.yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

volumes:
  qdrant_data:
    driver: local
```

#### Despliegue en Kubernetes

```yaml
# qdrant-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:latest
        ports:
        - containerPort: 6333
        - containerPort: 6334
        env:
        - name: QDRANT__SERVICE__HTTP_PORT
          value: "6333"
        - name: QDRANT__SERVICE__GRPC_PORT
          value: "6334"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
      volumes:
      - name: qdrant-storage
        persistentVolumeClaim:
          claimName: qdrant-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: qdrant-service
spec:
  selector:
    app: qdrant
  ports:
  - port: 6333
    targetPort: 6333
    name: http
  - port: 6334
    targetPort: 6334
    name: grpc
  type: LoadBalancer
```

#### Configuración de Producción

```yaml
# production.yaml
service:
  host: 0.0.0.0
  http_port: 6333
  grpc_port: 6334
  enable_cors: true
  max_request_size_mb: 32
  max_workers: 0  # Auto-detectar

storage:
  # Usar almacenamiento en disco para producción
  storage_path: /qdrant/storage
  snapshots_path: /qdrant/snapshots
  on_disk_payload: true
  on_disk_vectors: true

cluster:
  enabled: true
  p2p:
    port: 6335
  consensus:
    tick_period_ms: 100
    bootstrap_timeout_sec: 5

log_level: INFO
```

### Opción 3: Enfoque Híbrido

Combina Qdrant Cloud para producción con desarrollo local:

```python
import os
from qdrant_client import QdrantClient

def get_qdrant_client():
    """Obtener cliente Qdrant basado en el entorno"""
    if os.getenv("ENVIRONMENT") == "production":
        # Usar Qdrant Cloud
        return QdrantClient(
            url=os.getenv("QDRANT_CLOUD_URL"),
            api_key=os.getenv("QDRANT_CLOUD_API_KEY"),
            timeout=60,
            prefer_grpc=True
        )
    else:
        # Usar Qdrant local
        return QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=30
        )
```

### Migración de Local a Nube

1. **Exportar datos** desde Qdrant local:
   ```bash
   # Crear snapshot
   docker exec qdrant_container qdrant-cli snapshot create \
       --collection-name labor_law_articles \
       --output-dir /qdrant/snapshots
   ```

2. **Importar a Qdrant Cloud**:
   ```python
   # Subir a la nube
   client.upload_collection(
       collection_name="labor_law_articles",
       vectors=vectors,
       payload=payloads,
       ids=ids
   )
   ```

3. **Actualizar configuración**:
   ```env
   # Cambiar a configuración de nube
   QDRANT_URL=https://your-cluster-id.eu-central.aws.cloud.qdrant.io:6333
   QDRANT_API_KEY=tu_clave_api_de_nube
   ```

### Consideraciones de Costo

#### Precios de Qdrant Cloud
- **Nivel Gratuito**: 1GB de almacenamiento, 1M vectores
- **Pago por uso**: Basado en almacenamiento y uso de cómputo
- **Empresarial**: Precios personalizados para despliegues grandes

#### Costos Auto-hospedados
- **Infraestructura**: Costos de servidor, almacenamiento, red
- **Mantenimiento**: Tiempo de DevOps, monitoreo, respaldos
- **Escalado**: Escalado manual vs automático

### Consideraciones de Seguridad

#### Seguridad de Qdrant Cloud
- **Encriptación**: Datos encriptados en tránsito y en reposo
- **Control de Acceso**: Autenticación basada en clave API
- **Seguridad de Red**: VPC y endpoints privados
- **Cumplimiento**: Compatible con SOC 2, GDPR

#### Seguridad Auto-hospedada
- **Seguridad de Red**: Reglas de firewall, acceso VPN
- **Autenticación**: Claves API, RBAC
- **Encriptación**: TLS para datos en tránsito
- **Control de Acceso**: Restricciones a nivel de red

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
