<div align="center">

**Language / Idioma:**
[🇺🇸 English](#lus-laboris-api) | [🇪🇸 Español](#api-lus-laboris)

</div>

---

# Lus Laboris API

REST API built with FastAPI for semantic search and information retrieval from Paraguay's Labor Code using Qdrant as vector database.

## Quick Start

### Development

```bash
# Navigate to API directory
cd src/lus_laboris_api/

# Run development script
./start_api_dev.sh
```

### Docker

#### Build and Push Image

```bash
# Navigate to API directory
cd src/lus_laboris_api/

# Run build and push script
./docker_build_push.sh
```

#### Run with Docker

```bash
# Basic command with volumes
docker run -it --rm \
  --name legal-rag-api \
  -p 8000:8000 \
  -v /path/to/your/keys/public_key.pem:/app/api/keys/public_key.pem \
  -v /path/to/your/.env:/app/.env \
  -e API_ENV_FILE_PATH=/app/.env \
  your_username/legal-rag-api:latest
```

#### Command Parameters

- **`-it --rm`**: Interactive mode and remove container on exit
- **`--name legal-rag-api`**: Container name
- **`-p 8000:8000`**: Maps host port 8000 to container port 8000
- **`-v /path/to/your/keys/public_key.pem:/app/api/keys/public_key.pem`**: Mounts JWT public key file
- **`-v /path/to/your/.env:/app/.env`**: Mounts configuration file
- **`-e API_ENV_FILE_PATH=/app/.env`**: Defines .env file path inside container

#### Verify it Works

```bash
# Health check
curl http://localhost:8000/api/health/

# View logs
docker logs legal-rag-api

# Access Swagger UI
open http://localhost:8000/docs
```

## Available URLs

Once the API is started:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## 🔧 Configuration

### Environment Variables

The script reads variables from the `.env` file in the project root:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
API_LOG_LEVEL=info

# Security
API_ALLOWED_ORIGINS='["*"]'
API_ALLOWED_HOSTS='["*"]'
API_JWT_PUBLIC_KEY_PATH=keys/public_key.pem

# Qdrant Configuration
API_QDRANT_URL=http://localhost:6333
API_QDRANT_API_KEY=your_api_key
API_QDRANT_COLLECTION_NAME=lus_laboris_articles

# GCP Configuration
API_GCP_PROJECT_ID=your_project_id
API_GOOGLE_APPLICATION_CREDENTIALS=.gcpcredentials
API_GCP_USE_CREDENTIALS=true

# Embedding Configuration
API_DEFAULT_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
API_EMBEDDING_BATCH_SIZE=100

# Docker Configuration (optional)
API_ENV_FILE_PATH=/app/.env
```

## API Documentation

### Main Endpoints

#### Authentication
- **Type**: JWT with RSA public/private keys
- **Header**: `Authorization: Bearer <token>`
- **Generation**: Use scripts in `utils/`

#### Vectorstore (Qdrant)

**POST** `/api/data/load-to-vectorstore-local`
- Load JSON data from local files to Qdrant
- Requires JWT authentication

**POST** `/api/data/load-to-vectorstore-gcp`
- Load JSON data from Google Cloud Storage to Qdrant
- Requires JWT authentication

**GET** `/api/data/collections`
- List all collections
- Requires JWT authentication

**GET** `/api/data/collections/{collection_name}`
- Detailed information about a collection
- Requires JWT authentication

**DELETE** `/api/data/collections/{collection_name}`
- Delete a collection
- Requires JWT authentication

#### Health Checks

**GET** `/api/health/`
- Complete system health check
- No authentication required

**GET** `/api/health/qdrant`
- Qdrant status
- No authentication required

**GET** `/api/health/gcp`
- Google Cloud status
- No authentication required

**GET** `/api/health/embeddings`
- Embedding service status
- No authentication required

### Data Models

#### LoadToVectorstoreLocalRequest
```json
{
  "filename": "codigo_trabajo_articulos.json",
  "local_data_path": "data/processed",
  "replace_collection": false
}
```

#### LoadToVectorstoreGCPRequest
```json
{
  "filename": "codigo_trabajo_articulos.json",
  "folder": "processed",
  "bucket_name": "your-bucket-name",
  "replace_collection": false
}
```

#### LoadToVectorstoreResponse
```json
{
  "success": true,
  "message": "Data loaded successfully to vectorstore",
  "collection_name": "lus_laboris_articles",
  "documents_processed": 410,
  "documents_inserted": 410,
  "processing_time_seconds": 45.2,
  "embedding_model_used": "sentence-transformers/all-MiniLM-L6-v2",
  "vector_dimensions": 384,
  "batch_size": 100
}
```

### JSON Data Structure

The API processes JSON files with the following structure:

```json
{
  "meta": {
    "numero_ley": "213",
    "fecha_promulgacion": "29-06-1993",
    "fecha_publicacion": "29-10-1993"
  },
  "articulos": [
    {
      "articulo_numero": 1,
      "libro": "libro primero",
      "libro_numero": 1,
      "titulo": "titulo primero",
      "capitulo": "capitulo i",
      "capitulo_numero": 1,
      "capitulo_descripcion": "del objeto y aplicación del código",
      "articulo": "este código tiene por objeto establecer normas..."
    }
  ]
}
```

### Qdrant Payload

Each article is stored in Qdrant with the following payload:

```json
{
  "libro": "libro primero",
  "libro_numero": 1,
  "titulo": "titulo primero",
  "capitulo": "capitulo i",
  "capitulo_numero": 1,
  "capitulo_descripcion": "del objeto y aplicación del código",
  "articulo": "este código tiene por objeto establecer normas...",
  "articulo_numero": 1,
  "articulo_len": 192,
  "source": "codigo_trabajo_paraguay_ley213"
}
```

### Text for Embedding

The text used to generate embeddings combines:
- **Format**: `{capitulo_descripcion}: {articulo}`
- **Example**: `"del objeto y aplicación del código: este código tiene por objeto establecer normas..."`

## Security

### JWT Authentication

- **Algorithm**: RS256 (RSA with SHA-256)
- **Keys**: RSA public/private key pair
- **Generation**: Scripts in `utils/`
- **Validation**: Public key only (API doesn't generate tokens)

### Authentication Flow

1. **Generate keys**: `utils/setup_jwt_token.sh`
2. **Generate token**: `utils/generate_jwt_token.py`
3. **Use token**: `Authorization: Bearer <token>`

### Separation of Responsibilities

- **API**: Only validates tokens with public key
- **Utils**: Generates keys and tokens with private key
- **Security**: Valid token = authorized access

## Services

### QdrantService
- Connection and operations with Qdrant
- Collection creation/deletion
- Document insertion and search
- Health checks

### GCPService
- Google Cloud Storage operations
- JSON file loading from GCS
- Automatic authentication (Cloud Run) or with credentials
- Health checks

### EmbeddingService
- Embedding generation with Sentence Transformers
- Multiple supported models
- Batch processing
- Model loading cache
- **Automatic device detection**: CPU/GPU based on availability
- **Centralized configuration**: Model and batch size from config

## Troubleshooting

### Error: "uv is not installed"
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### Error: "api/main.py not found"
```bash
# Make sure you run from src/lus_laboris_api/
cd src/lus_laboris_api/
pwd
# Should show: /path/to/lus-laboris-py/src/lus_laboris_api
```

### Error: "Qdrant connection failed"
- Verify Qdrant is running
- Check URL and API key in configuration
- Review logs for specific details

### Error: "JWT public key not found"
- Generate keys with `utils/setup_jwt_token.sh`
- Verify path in `JWT_PUBLIC_KEY_PATH`
- Ensure file exists

### Docker Common Issues

#### Error: "Qdrant connection failed" in Docker
```bash
# Configuration depends on how Qdrant is running:

# 1. If Qdrant is running in Docker Compose (same network)
# Use the service name as hostname
API_QDRANT_URL=http://qdrant:6333

# 2. If Qdrant is running on host machine:
# Windows (Docker Desktop): use host.docker.internal
API_QDRANT_URL=http://host.docker.internal:6333

# Linux: use host IP or host.docker.internal
API_QDRANT_URL=http://host.docker.internal:6333
# OR
API_QDRANT_URL=http://172.17.0.1:6333

# 3. If Qdrant is running in another container:
# Use container name or IP
API_QDRANT_URL=http://qdrant-container:6333
```

#### Error: "JWT public key not found" in Docker
```bash
# Verify the key file is mounted correctly
docker exec -it legal-rag-api ls -la /app/api/keys/

# Check the environment variable
docker exec -it legal-rag-api env | grep JWT

# Ensure correct path in .env file
API_JWT_PUBLIC_KEY_PATH=keys/public_key.pem
```

#### Error: "IsADirectoryError: [Errno 21] Is a directory: '/app/keys'"
```bash
# Problem: Mounting directory instead of file
# Wrong:
-v /path/to/keys:/app/keys

# Correct:
-v /path/to/keys/public_key.pem:/app/api/keys/public_key.pem
```

#### Error: "ModuleNotFoundError: No module named 'api'"
```bash
# Problem: Incorrect ENTRYPOINT in Dockerfile
# Check Dockerfile has correct WORKDIR and ENTRYPOINT
WORKDIR /app
ENTRYPOINT ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Error: "Container exits immediately"
```bash
# Check container logs
docker logs legal-rag-api

# Run interactively to debug
docker run -it --rm \
  --name legal-rag-api-debug \
  -p 8000:8000 \
  -v /path/to/keys/public_key.pem:/app/api/keys/public_key.pem \
  -v /path/to/.env:/app/.env \
  -e API_ENV_FILE_PATH=/app/.env \
  your_username/legal-rag-api:latest /bin/bash
```

## Additional Documentation

- **Utils**: `utils/README.md` - Utility scripts
- **Docker Guide**: `docs/docker_guide.md` - Complete Docker guide
- **Qdrant Guide**: `docs/qdrant_guide.md` - Qdrant guide
- **FastAPI Guide**: `docs/fastapi_guide.md` - FastAPI guide
- **UV Guide**: `docs/uv_guide.md` - UV guide
- **GCP Setup**: `docs/setup_gcp_project.md` - GCP configuration

---

# API Lus Laboris

API REST construida con FastAPI para búsqueda semántica y recuperación de información del Código Laboral de Paraguay usando Qdrant como base de datos vectorial.

## Inicio Rápido

### Desarrollo

```bash
# Ir al directorio de la API
cd src/lus_laboris_api/

# Ejecutar script de desarrollo
./start_api_dev.sh
```

### Docker

#### Construir y Subir Imagen

```bash
# Ir al directorio de la API
cd src/lus_laboris_api/

# Ejecutar script de build y push
./docker_build_push.sh
```

#### Ejecutar con Docker

```bash
# Comando básico con volúmenes
docker run -it --rm \
  --name legal-rag-api \
  -p 8000:8000 \
  -v /ruta/a/tus/keys/public_key.pem:/app/api/keys/public_key.pem \
  -v /ruta/a/tu/.env:/app/.env \
  -e API_ENV_FILE_PATH=/app/.env \
  tu_usuario/legal-rag-api:latest
```

#### Parámetros del Comando

- **`-it --rm`**: Modo interactivo y eliminar contenedor al salir
- **`--name legal-rag-api`**: Nombre del contenedor
- **`-p 8000:8000`**: Mapea el puerto 8000 del host al puerto 8000 del contenedor
- **`-v /ruta/a/tus/keys/public_key.pem:/app/api/keys/public_key.pem`**: Monta el archivo de clave pública JWT
- **`-v /ruta/a/tu/.env:/app/.env`**: Monta el archivo de configuración
- **`-e API_ENV_FILE_PATH=/app/.env`**: Define la ruta del archivo .env dentro del contenedor

#### Verificar que Funciona

```bash
# Health check
curl http://localhost:8000/api/health/

# Ver logs
docker logs legal-rag-api

# Acceder a Swagger UI
open http://localhost:8000/docs
```

## URLs Disponibles

Una vez iniciada la API:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## Configuración

### Variables de Entorno

El script lee las variables del archivo `.env` en la raíz del proyecto:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
API_LOG_LEVEL=info

# Security
API_ALLOWED_ORIGINS='["*"]'
API_ALLOWED_HOSTS='["*"]'
API_JWT_PUBLIC_KEY_PATH=keys/public_key.pem

# Qdrant Configuration
API_QDRANT_URL=http://localhost:6333
API_QDRANT_API_KEY=your_api_key
API_QDRANT_COLLECTION_NAME=lus_laboris_articles

# GCP Configuration
API_GCP_PROJECT_ID=your_project_id
API_GOOGLE_APPLICATION_CREDENTIALS=.gcpcredentials
API_GCP_USE_CREDENTIALS=true

# Embedding Configuration
API_DEFAULT_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
API_EMBEDDING_BATCH_SIZE=100

# Docker Configuration (opcional)
API_ENV_FILE_PATH=/app/.env
```

## Documentación de la API

### Endpoints Principales

#### Autenticación
- **Tipo**: JWT con claves RSA pública/privada
- **Header**: `Authorization: Bearer <token>`
- **Generación**: Usar scripts en `utils/`

#### Vectorstore (Qdrant)

**POST** `/api/data/load-to-vectorstore-local`
- Cargar datos JSON desde archivos locales a Qdrant
- Requiere autenticación JWT

**POST** `/api/data/load-to-vectorstore-gcp`
- Cargar datos JSON desde Google Cloud Storage a Qdrant
- Requiere autenticación JWT

**GET** `/api/data/collections`
- Listar todas las colecciones
- Requiere autenticación JWT

**GET** `/api/data/collections/{collection_name}`
- Información detallada de una colección
- Requiere autenticación JWT

**DELETE** `/api/data/collections/{collection_name}`
- Eliminar una colección
- Requiere autenticación JWT

#### Health Checks

**GET** `/api/health/`
- Health check completo del sistema
- Sin autenticación requerida

**GET** `/api/health/qdrant`
- Estado de Qdrant
- Sin autenticación requerida

**GET** `/api/health/gcp`
- Estado de Google Cloud
- Sin autenticación requerida

**GET** `/api/health/embeddings`
- Estado del servicio de embeddings
- Sin autenticación requerida

### Modelos de Datos

#### LoadToVectorstoreLocalRequest
```json
{
  "filename": "codigo_trabajo_articulos.json",
  "local_data_path": "data/processed",
  "replace_collection": false
}
```

#### LoadToVectorstoreGCPRequest
```json
{
  "filename": "codigo_trabajo_articulos.json",
  "folder": "processed",
  "bucket_name": "your-bucket-name",
  "replace_collection": false
}
```

#### LoadToVectorstoreResponse
```json
{
  "success": true,
  "message": "Data loaded successfully to vectorstore",
  "collection_name": "lus_laboris_articles",
  "documents_processed": 410,
  "documents_inserted": 410,
  "processing_time_seconds": 45.2,
  "embedding_model_used": "sentence-transformers/all-MiniLM-L6-v2",
  "vector_dimensions": 384,
  "batch_size": 100
}
```

### Estructura de Datos JSON

La API procesa archivos JSON con la siguiente estructura:

```json
{
  "meta": {
    "numero_ley": "213",
    "fecha_promulgacion": "29-06-1993",
    "fecha_publicacion": "29-10-1993"
  },
  "articulos": [
    {
      "articulo_numero": 1,
      "libro": "libro primero",
      "libro_numero": 1,
      "titulo": "titulo primero",
      "capitulo": "capitulo i",
      "capitulo_numero": 1,
      "capitulo_descripcion": "del objeto y aplicación del código",
      "articulo": "este código tiene por objeto establecer normas..."
    }
  ]
}
```

### Payload de Qdrant

Cada artículo se almacena en Qdrant con el siguiente payload:

```json
{
  "libro": "libro primero",
  "libro_numero": 1,
  "titulo": "titulo primero",
  "capitulo": "capitulo i",
  "capitulo_numero": 1,
  "capitulo_descripcion": "del objeto y aplicación del código",
  "articulo": "este código tiene por objeto establecer normas...",
  "articulo_numero": 1,
  "articulo_len": 192,
  "source": "codigo_trabajo_paraguay_ley213"
}
```

### Texto para Embedding

El texto que se usa para generar embeddings combina:
- **Formato**: `{capitulo_descripcion}: {articulo}`
- **Ejemplo**: `"del objeto y aplicación del código: este código tiene por objeto establecer normas..."`

## Seguridad

### Autenticación JWT

- **Algoritmo**: RS256 (RSA con SHA-256)
- **Claves**: Par de claves pública/privada RSA
- **Generación**: Scripts en `utils/`
- **Validación**: Solo clave pública (API no genera tokens)

### Flujo de Autenticación

1. **Generar claves**: `utils/setup_jwt_token.sh`
2. **Generar token**: `utils/generate_jwt_token.py`
3. **Usar token**: `Authorization: Bearer <token>`

### Separación de Responsabilidades

- **API**: Solo valida tokens con clave pública
- **Utils**: Genera claves y tokens con clave privada
- **Seguridad**: Token válido = acceso autorizado

## Servicios

### QdrantService
- Conexión y operaciones con Qdrant
- Creación/eliminación de colecciones
- Inserción y búsqueda de documentos
- Health checks

### GCPService
- Operaciones con Google Cloud Storage
- Carga de archivos JSON desde GCS
- Autenticación automática (Cloud Run) o con credenciales
- Health checks

### EmbeddingService
- Generación de embeddings con Sentence Transformers
- Múltiples modelos soportados
- Procesamiento por lotes
- Caché de modelos cargados



## Solución de Problemas

### Error: "uv no está instalado"
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### Error: "No se encontró api/main.py"
```bash
# Asegúrate de ejecutar desde src/lus_laboris_api/
cd src/lus_laboris_api/
pwd
# Debe mostrar: /path/to/lus-laboris-py/src/lus_laboris_api
```

### Error: "Qdrant connection failed"
- Verificar que Qdrant esté ejecutándose
- Verificar URL y API key en configuración
- Revisar logs para detalles específicos

### Error: "JWT public key not found"
- Generar claves con `utils/setup_jwt_token.sh`
- Verificar ruta en `JWT_PUBLIC_KEY_PATH`
- Asegurar que el archivo existe

### Problemas Comunes de Docker

#### Error: "Qdrant connection failed" en Docker
```bash
# La configuración depende de cómo esté ejecutándose Qdrant:

# 1. Si Qdrant está ejecutándose en Docker Compose (misma red)
# Usa el nombre del servicio como hostname
API_QDRANT_URL=http://qdrant:6333

# 2. Si Qdrant está ejecutándose en la máquina host:
# Windows (Docker Desktop): usa host.docker.internal
API_QDRANT_URL=http://host.docker.internal:6333

# Linux: usa la IP del host o host.docker.internal
API_QDRANT_URL=http://host.docker.internal:6333
# O
API_QDRANT_URL=http://172.17.0.1:6333

# 3. Si Qdrant está ejecutándose en otro contenedor:
# Usa el nombre del contenedor o IP
API_QDRANT_URL=http://qdrant-container:6333
```

#### Error: "JWT public key not found" en Docker
```bash
# Verificar que el archivo de clave esté montado correctamente
docker exec -it legal-rag-api ls -la /app/api/keys/

# Verificar la variable de entorno
docker exec -it legal-rag-api env | grep JWT

# Asegurar ruta correcta en archivo .env
API_JWT_PUBLIC_KEY_PATH=keys/public_key.pem
```

#### Error: "IsADirectoryError: [Errno 21] Is a directory: '/app/keys'"
```bash
# Problema: Montando directorio en lugar de archivo
# Incorrecto:
-v /ruta/a/keys:/app/keys

# Correcto:
-v /ruta/a/keys/public_key.pem:/app/api/keys/public_key.pem
```

#### Error: "ModuleNotFoundError: No module named 'api'"
```bash
# Problema: ENTRYPOINT incorrecto en Dockerfile
# Verificar que Dockerfile tenga WORKDIR y ENTRYPOINT correctos
WORKDIR /app
ENTRYPOINT ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Error: "Container exits immediately"
```bash
# Verificar logs del contenedor
docker logs legal-rag-api

# Ejecutar interactivamente para debuggear
docker run -it --rm \
  --name legal-rag-api-debug \
  -p 8000:8000 \
  -v /ruta/a/keys/public_key.pem:/app/api/keys/public_key.pem \
  -v /ruta/a/.env:/app/.env \
  -e API_ENV_FILE_PATH=/app/.env \
  tu_usuario/legal-rag-api:latest /bin/bash
```

## Documentación Adicional

- **Utils**: `utils/README.md` - Scripts de utilidades
- **Docker Guide**: `docs/docker_guide.md` - Guía completa de Docker
- **Qdrant Guide**: `docs/qdrant_guide.md` - Guía de Qdrant
- **FastAPI Guide**: `docs/fastapi_guide.md` - Guía de FastAPI
- **UV Guide**: `docs/uv_guide.md` - Guía de UV
- **GCP Setup**: `docs/setup_gcp_project.md` - Configuración de GCP