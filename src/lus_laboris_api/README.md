<div align="center">

**Language / Idioma:**
[🇺🇸 English](#lus-laboris-api) | [🇪🇸 Español](#api-lus-laboris)

</div>

---

# Lus Laboris API

REST API built with FastAPI for semantic search and information retrieval from Paraguay's Labor Code using Qdrant as vector database. Features integrated Phoenix monitoring for LLM tracking, session management, and quality metrics.

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

The script reads variables from the `.env` file in the project root. You can use the provided example file:

```bash
# Copy the example file and customize it
cp .env_example .env
# Edit the .env file with your values
```

The `.env_example` file contains all required variables organized by category. Here are the key variables for the API:

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
API_JWT_AUD=lus-laboris-client  # JWT audience claim validation
API_JWT_ISS=lus-laboris-api     # JWT issuer claim validation

# Qdrant Configuration
API_QDRANT_URL=http://localhost:6333
API_QDRANT_API_KEY=your_api_key
API_QDRANT_COLLECTION_NAME=lus_laboris_articles
API_QDRANT_GRPC_PORT=6334  # gRPC port for faster connections (default: 6334)
API_QDRANT_PREFER_GRPC=true  # Use gRPC for 2-3x better performance (default: true)

# GCP Configuration
API_GCP_PROJECT_ID=your_project_id
API_GOOGLE_APPLICATION_CREDENTIALS=.gcpcredentials/service-account.json
API_GCP_USE_CREDENTIALS=true

# Embedding Configuration
API_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
API_EMBEDDING_BATCH_SIZE=100

# Reranking Configuration
API_RERANKING_MODEL=ms-marco-MiniLM-L-6-v2
API_USE_RERANKING=false

# RAG Configuration
API_RAG_TOP_K=5
API_LLM_PROVIDER=openai
API_LLM_MODEL=gpt-3.5-turbo
API_RATE_LIMIT_REQUESTS=10
API_RATE_LIMIT_WINDOW="1 minute"  # Must use quotes for values with spaces

# Debug Configuration
API_DEBUG_CONFIG=false

# LLM API Keys
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Phoenix Monitoring Configuration
API_PHOENIX_ENABLED=true
API_PHOENIX_ENDPOINT=http://localhost:6006
API_PHOENIX_API_KEY=your_phoenix_api_key_here
API_PHOENIX_PROJECT_NAME=lus-laboris-api

# Docker Configuration (optional)
API_ENV_FILE_PATH=/app/.env
```

### GCP Credentials Path Resolution

The `API_GOOGLE_APPLICATION_CREDENTIALS` variable supports both absolute and relative paths:

- **Absolute path**: `/path/to/credentials.json` - Used as-is
- **Relative path**: `.gcpcredentials/service-account.json` - Resolved from project root

**Examples:**
```env
# Relative path (recommended)
API_GOOGLE_APPLICATION_CREDENTIALS=.gcpcredentials/service-account.json

# Absolute path
API_GOOGLE_APPLICATION_CREDENTIALS=/home/user/.gcpcredentials/service-account.json
```

### JWT Public Key Path Resolution

The `API_JWT_PUBLIC_KEY_PATH` variable supports both absolute and relative paths:

- **Absolute path**: `/path/to/public_key.pem` - Used as-is
- **Relative path**: `keys/public_key.pem` - Resolved from project root

**Examples:**
```env
# Relative path (recommended)
API_JWT_PUBLIC_KEY_PATH=keys/public_key.pem

# Absolute path
API_JWT_PUBLIC_KEY_PATH=/home/user/keys/public_key.pem
```

## API Documentation

### Main Endpoints

#### Authentication
- **Type**: JWT with RSA public/private keys
- **Header**: `Authorization: Bearer <token>`
- **Generation**: Use scripts in `utils/`

#### Health Check Endpoints

**GET** `/api/health`
- Comprehensive health check of API and dependencies
- **No authentication required** - for monitoring systems
- Returns service status, dependencies (basic status only), and uptime
- **Safe for public access**: Only exposes service names and their status (connected/healthy/unhealthy)
- Does NOT expose: model names, project IDs, collection counts, or other sensitive details

**GET** `/api/health/ready`
- Readiness check for load balancers and orchestrators
- **No authentication required** - for deployment verification
- Returns simple ready/not ready status

**Service-Specific Health Checks (Optional Authentication with Info Filtering):**

**GET** `/api/health/qdrant`
- Qdrant-specific health check
- **Optional authentication**: Works with or without token
- **Without token**: Returns only `{"status": "connected"}` (basic info)
- **With JWT token**: Returns full info including `collections_count`

**GET** `/api/health/gcp`
- GCP-specific health check
- **Optional authentication**: Works with or without token
- **Without token**: Returns only `{"status": "connected"}` (basic info)
- **With JWT token**: Returns full info including `project_id`, `buckets_count` (⚠️ sensitive)

**GET** `/api/health/embeddings`
- Embedding service health check
- **Optional authentication**: Works with or without token
- **Without token**: Returns only `{"status": "healthy"}` (basic info)
- **With JWT token**: Returns full info including `loaded_models`, `device`, `model_dimensions`

**GET** `/api/health/reranking`
- Reranking service health check
- **Optional authentication**: Works with or without token
- **Without token**: Returns only `{"status": "healthy"}` (basic info)
- **With JWT token**: Returns full info including `model_name`, `device`

**GET** `/api/health/rag`
- RAG service health check
- **Optional authentication**: Works with or without token
- **Without token**: Returns only `{"status": "healthy"}` (basic info)
- **With JWT token**: Returns full info including `provider`, `model`, `embedding_model`

**GET** `/api/health/phoenix`
- Phoenix monitoring service health check
- **Optional authentication**: Works with or without token
- **Without token**: Returns only `{"status": "healthy"}` (basic info)
- **With JWT token**: Returns full info including `project_name`, `active_sessions`, `phoenix_connection` status, and performs active connection test to Phoenix collector

**GET** `/api/status`
- **Comprehensive status of ALL services** (aggregated diagnostic endpoint)
- **Optional authentication**: Works with or without token
- **Without token**: Returns only basic status for each service `{"status": "connected/healthy"}`
- **With JWT token**: Returns detailed information for all services:
  - Qdrant (with collections count)
  - GCP (with project_id and buckets count)
  - Embedding service (with loaded models and device)
  - RAG service (with provider, model, embedding model)
- **Use case**: 
  - Public monitoring tools can check service health
  - Authenticated admins get full diagnostic information
- **Security**: Smart filtering - no sensitive info exposed without authentication

#### RAG (Question Answering)

**POST** `/api/rag/ask`
- Ask questions about Paraguayan labor law using RAG
- **No authentication required** - public endpoint with rate limiting
- Rate limit: 10 requests per minute per IP address
- Uses OpenAI or Gemini LLM with context from Qdrant
- **Phoenix Evals**: Automatic asynchronous evaluation with LLM-as-a-Judge
  - Relevance scoring
  - Hallucination detection
  - Toxicity checking
  - Grounding verification

**GET** `/api/rag/evaluations/status`
- Evaluation service status and queue information
- **Requires JWT authentication** - protected endpoint
- Returns evaluation queue size and service health

**Phoenix Metrics and Monitoring**
- **Access Phoenix UI** to view detailed metrics, traces, and evaluations:
  - Local: `http://localhost:6006`
  - Cloud: Use your Phoenix cloud URL (e.g., `https://app.phoenix.arize.com`)
- Phoenix UI provides:
  - Real-time traces and spans
  - LLM call monitoring
  - Evaluation results and trends
  - Performance metrics and analytics

#### Health Check Examples

**Public endpoints (no token required):**
```bash
# General health check (basic status only)
curl -X GET "http://localhost:8000/api/health/"
# Response: {
#   "success": true,
#   "service": "lus-laboris-api",
#   "status": "healthy",
#   "dependencies": {
#     "qdrant": "connected",
#     "gcp": "connected",
#     "embedding_service": "healthy",
#     "reranking_service": "disabled",
#     "rag_service": "healthy",
#     "evaluation_service": "healthy",
#     "phoenix": "healthy"
#   },
#   "uptime_seconds": 3600.5
# }

# Readiness check
curl -X GET "http://localhost:8000/api/health/ready"
# Response: {"success": true, "ready": true, "message": "Service is ready"}

# Aggregated status (basic info without token)
curl -X GET "http://localhost:8000/api/status"
# Response: {"services": {"qdrant": {"status": "connected"}, "gcp": {"status": "connected"}, ...}}
```

**Optional authentication endpoints (basic info without token, detailed info with token):**
```bash
# Without token - Returns only basic status
curl -X GET "http://localhost:8000/api/health/gcp"
# Response: {"status": {"status": "connected"}}  ← No sensitive info

curl -X GET "http://localhost:8000/api/health/embeddings"
# Response: {"status": {"status": "healthy"}}  ← No model info

# With token - Returns detailed information
curl -X GET "http://localhost:8000/api/health/gcp" \
  -H "Authorization: Bearer your_jwt_token_here"
# Response: {"status": {"status": "connected", "project_id": "...", "buckets_count": 2}}

curl -X GET "http://localhost:8000/api/health/embeddings" \
  -H "Authorization: Bearer your_jwt_token_here"
# Response: {"status": {"status": "healthy", "loaded_models": [...], "device": "cuda"}}

# Aggregated status with token - Returns detailed info for ALL services
curl -X GET "http://localhost:8000/api/status" \
  -H "Authorization: Bearer your_jwt_token_here"
# Response: {"services": {"qdrant": {...full info...}, "gcp": {...full info...}, ...}}
```

**RAG endpoints:**
```bash
# Ask a question (public, no token required)
curl -X POST "http://localhost:8000/api/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuáles son las horas de trabajo permitidas?"}'

# Evaluation service status (requires JWT token)
curl -X GET "http://localhost:8000/api/rag/evaluations/status" \
  -H "Authorization: Bearer your_jwt_token_here"
```

#### Vectorstore (Qdrant)

**POST** `/api/data/load-to-vectorstore-local`
- **Asynchronous** loading of JSON data from local files to Qdrant
- Returns immediately with job information (HTTP 202 Accepted)
- Processing happens in background (embeddings, vector insertion)
- Requires JWT authentication
- **Response includes**: `job_id` for tracking

**POST** `/api/data/load-to-vectorstore-gcp`
- **Asynchronous** loading of JSON data from Google Cloud Storage to Qdrant
- Returns immediately with job information (HTTP 202 Accepted)
- Processing happens in background (embeddings, vector insertion)
- Requires JWT authentication
- **Response includes**: `job_id` for tracking

**GET** `/api/data/jobs`
- List all background processing jobs
- Shows job status: `queued`, `processing`, `completed`, `failed`
- Includes timestamps in ISO 8601 format
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
- Optional authentication (works with or without token)

**GET** `/api/health/gcp`
- Google Cloud status
- Optional authentication (works with or without token)

**GET** `/api/health/embeddings`
- Embedding service status
- Optional authentication (works with or without token)

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
  "message": "Data loading job initiated successfully. Job ID: 550e8400-e29b-41d4-a716-446655440000. Check status at /api/data/jobs",
  "collection_name": "lus_laboris_articles",
  "documents_processed": 0,
  "documents_inserted": 0,
  "processing_time_seconds": 0.0,
  "embedding_model_used": "sentence-transformers/all-MiniLM-L6-v2",
  "vector_dimensions": 0,
  "batch_size": 100,
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### JobsListResponse
```json
{
  "success": true,
  "message": "Found 2 job(s)",
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "operation": "load_to_vectorstore_local",
      "user": "admin",
      "filename": "codigo_trabajo_articulos.json",
      "collection_name": "lus_laboris_articles",
      "created_at": "2025-10-08T20:58:08.039417",
      "started_at": "2025-10-08T20:58:08.040129",
      "completed_at": "2025-10-08T20:58:27.090524",
      "error": null,
      "result": {
        "documents_processed": 413,
        "documents_inserted": 413,
        "processing_time_seconds": 19.05
      }
    },
    {
      "job_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "processing",
      "operation": "load_to_vectorstore_local",
      "user": "admin",
      "filename": "codigo_trabajo_articulos.json",
      "collection_name": "lus_laboris_articles",
      "created_at": "2025-10-08T21:05:15.123456",
      "started_at": "2025-10-08T21:05:15.124789",
      "completed_at": null,
      "error": null,
      "result": null
    }
  ],
  "count": 2
}
```

#### QuestionRequest
```json
{
  "question": "¿Cuáles son los derechos del trabajador en caso de despido?"
}
```

#### QuestionResponse
```json
{
  "success": true,
  "message": "Question answered successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "question": "¿Cuáles son los derechos del trabajador en caso de despido?",
  "answer": "Según el Código del Trabajo paraguayo, el trabajador tiene derecho a...",
  "processing_time_seconds": 2.345,
  "documents_retrieved": 5,
  "top_k": 5,
  "reranking_applied": true,
  "documents": [
    {
      "id": 123,
      "score": 0.8542,
      "payload": {
        "articulo_numero": 45,
        "capitulo_descripcion": "Derechos del Trabajador",
        "articulo": "El trabajador tiene derecho a..."
      }
    }
  ]
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

### Information Security in Health Checks

Health check endpoints implement **smart information filtering** based on authentication:

| Endpoint | Without Authentication | With JWT Token |
|----------|----------------------|----------------|
| `/api/health` | Basic status only per service | **Same** (always basic, safe for public) |
| `/api/status` | Basic status only per service | **Full details** for all services |
| `/api/health/gcp` | `{"status": "connected"}` | `{"status": "connected", "project_id": "...", "buckets_count": 2}` |
| `/api/health/qdrant` | `{"status": "connected"}` | `{"status": "connected", "collections_count": 5}` |
| `/api/health/embeddings` | `{"status": "healthy"}` | `{"status": "healthy", "loaded_models": [...], "device": "cuda"}` |
| `/api/health/reranking` | `{"status": "healthy"}` | `{"status": "healthy", "model_name": "...", "device": "cpu"}` |
| `/api/health/rag` | `{"status": "healthy"}` | `{"status": "healthy", "provider": "openai", "model": "gpt-4"}` |
| `/api/health/phoenix` | `{"status": "healthy"}` | `{"status": "healthy", "project_name": "...", "phoenix_connection": "verified"}` |

**Security Benefits:**
- ✅ **Prevents reconnaissance attacks**: Attackers cannot map your infrastructure
- ✅ **Protects sensitive data**: Project IDs, model names, device info hidden from public
- ✅ **Maintains monitoring capability**: External tools can still check service status
- ✅ **Flexible access**: Authenticated users get full diagnostic information

**Implementation:**
```python
# Automatic sanitization based on authentication
def _sanitize_health_response(status, is_authenticated):
    if is_authenticated:
        return status  # Full info
    else:
        return {"status": status.get("status")}  # Basic info only
```

### JWT Authentication

- **Algorithm**: RS256 (RSA with SHA-256)
- **Keys**: RSA public/private key pair
- **Generation**: Scripts in `utils/`
- **Validation**: Public key only (API doesn't generate tokens)
- **Issuer (`iss`)**: Configurable via `API_JWT_ISS` (default: `lus-laboris-api`)
- **Audience (`aud`)**: Configurable via `API_JWT_AUD` (default: `lus-laboris-client`)

### Authentication Flow

1. **Generate keys**: `utils/setup_jwt_token.sh`
2. **Generate token**: `utils/generate_jwt_token.py`
3. **Use token**: `Authorization: Bearer <token>`

### JWT Token Validation

The API validates the following claims:

| Claim | Description | Validated | Configurable |
|-------|-------------|-----------|--------------|
| **`exp`** | Expiration time | ✅ Yes | Via token generation |
| **`iat`** | Issued at time | ✅ Yes | Via token generation |
| **`iss`** | Issuer (who issued the token) | ✅ Yes | `API_JWT_ISS` |
| **`aud`** | Audience (who the token is for) | ✅ Yes | `API_JWT_AUD` |
| **`sub`** | Subject (username) | ℹ️ Informational | - |

**Configuration:**
```env
API_JWT_PUBLIC_KEY_PATH=keys/public_key.pem
API_JWT_AUD=lus-laboris-client
API_JWT_ISS=lus-laboris-api
```

**Security Benefits:**
- ✅ Prevents token reuse across different systems
- ✅ Validates token origin (issuer)
- ✅ Validates token destination (audience)
- ✅ Follows RFC 7519 best practices

### Separation of Responsibilities

- **API**: Only validates tokens with public key
- **Utils**: Generates keys and tokens with private key
- **Security**: Valid token = authorized access

## Performance Optimizations

The API implements several performance optimizations for production use:

### 1. Qdrant gRPC Connection (2-3x faster)
- **Protocol**: Prefers gRPC over HTTP for vector operations
- **Port**: 6334 (configurable via `API_QDRANT_GRPC_PORT`)
- **Fallback**: Automatic fallback to HTTP if gRPC unavailable
- **Impact**: Search latency reduced from ~200ms to ~70ms
- **Benefits**:
  - Binary protocol (more efficient than JSON)
  - HTTP/2 multiplexing
  - Better compression
  - Lower CPU usage

### 2. Health Check Caching (430x faster)
- **TTL**: 5 seconds (prevents redundant service checks)
- **Scope**: All health check endpoints
- **Impact**: Response time from ~430ms to <1ms on cache hit
- **Benefits**:
  - Reduced load on external services (Qdrant, GCP)
  - Better handling of monitoring tools polling
  - Lower CPU and network usage

### 3. Parallel Health Check Execution (2.15x faster)
- **Method**: `asyncio.gather()` for concurrent execution
- **Endpoints**: `/api/health/` main health check
- **Impact**: Latency from ~430ms to ~200ms

### 4. Async LLM Calls (1.39x faster)
- **Library**: `AsyncOpenAI` client for non-blocking LLM calls
- **Impact**: Response time from ~2.5s to ~1.8s
- **Benefit**: Better resource utilization, handles concurrent requests efficiently
- **Retry**: Uses `AsyncRetrying` from tenacity for robust error handling

### 5. Parallel Phoenix Evals (3x faster)
- **Method**: `asyncio.gather()` for concurrent evaluation execution
- **Evaluations**: Relevance, Hallucination, Toxicity run in parallel
- **Impact**: Evaluation time from ~6s to ~2s
- **Background**: Runs asynchronously without blocking main response
- **Benefits**:
  - All service checks run simultaneously
  - Fails gracefully if one service is down
  - Better resource utilization

### Configuration

```env
# Enable gRPC for Qdrant (recommended for production)
API_QDRANT_PREFER_GRPC=true
API_QDRANT_GRPC_PORT=6334

# Qdrant must be running with gRPC enabled
# Docker: qdrant/qdrant:latest (gRPC enabled by default on port 6334)
```

### Performance Metrics

| Optimization | Before | After | Improvement |
|--------------|--------|-------|-------------|
| **Qdrant Search** | ~200ms | ~70ms | **2.85x faster** |
| **Health Check (cache miss)** | ~430ms | ~200ms | **2.15x faster** |
| **Health Check (cache hit)** | ~430ms | <1ms | **430x faster** |
| **Service Calls per 10s** | 12 calls | ~2 calls | **83% reduction** |
| **LLM Response (async)** | ~2.5s | ~1.8s | **1.39x faster** |
| **Phoenix Evals (parallel)** | ~6s | ~2s | **3x faster** |

## Services

### QdrantService
- **gRPC Optimization**: Uses gRPC for 2-3x faster queries than HTTP
- **Automatic Fallback**: Falls back to HTTP if gRPC is unavailable
- **Connection Pooling**: Maintains persistent connections
- **Configurable Timeout**: 10 seconds default for all operations
- Connection and operations with Qdrant
- Collection creation/deletion
- Document insertion and search
- Health checks with connection type reporting (gRPC/HTTP)

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

### RerankingService
- Document reranking using cross-encoder models
- Improves relevance of retrieved documents
- Optional service (can be disabled via configuration)
- **Automatic device detection**: CPU/GPU based on availability
- **Centralized configuration**: Model and usage from config
- **Fallback behavior**: Returns original documents if reranking fails

### RAGService
- RAG (Retrieval-Augmented Generation) for question answering
- **Async LLM Calls**: Uses `AsyncOpenAI` for non-blocking responses (1.39x faster)
- Support for OpenAI and Google Gemini LLMs
- Semantic search using embeddings and Qdrant
- **Optional document reranking** for improved relevance
- Context construction from legal documents
- **Async Retry Logic**: Robust error handling with `AsyncRetrying` from tenacity
- Comprehensive response with metadata and reranking information

### PhoenixMonitoringService
- **LLM Monitoring**: Complete tracking of OpenAI and Gemini API calls
- **Session Management**: Groups all actions within execution sessions
- **Quality Metrics**: Automatic evaluation of response coherence, relevance, and completeness
- **Performance Tracking**: Monitors embedding generation, vectorstore searches, and reranking
- **OpenTelemetry Integration**: Full observability with distributed tracing
- **Non-intrusive**: Asynchronous tracking without affecting API performance
- **Hierarchical Spans**: Parent-child span relationships for complex operations

### EvaluationService

**NEW**: Asynchronous evaluation service using Phoenix Evals (LLM-as-a-Judge):
- **Asynchronous Processing**: Evaluations run in background without blocking user responses
- **Phoenix Evals Integration**: Uses proven evaluation templates from Arize Phoenix
- **Evaluation Metrics**:
  - **Relevance**: How relevant is the answer to the question (0.0-1.0)
  - **Hallucination**: Does the answer contain information not in the context (0.0-1.0)
  - **Toxicity**: Does the answer contain offensive content (0.0-1.0)
  - **Grounding**: Is the answer based solely on provided context (0.0-1.0)
  - **Overall Quality**: Weighted average of all metrics
- **Queue-Based Architecture**: ThreadPoolExecutor with 2 workers processes evaluations
- **GPT-4o-mini**: Uses cost-effective model for evaluations
- **Graceful Shutdown**: Ensures pending evaluations complete before shutdown
- **Zero Latency Impact**: User receives response immediately (~2s), evaluation happens in background (~5s)

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
- **Phoenix Monitoring**: Built-in LLM monitoring with session tracking and quality metrics

---

# API Lus Laboris

API REST construida con FastAPI para búsqueda semántica y recuperación de información del Código Laboral de Paraguay usando Qdrant como base de datos vectorial. Incluye monitoreo integrado con Phoenix para tracking de LLM, gestión de sesiones y métricas de calidad.

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

El script lee las variables del archivo `.env` en la raíz del proyecto. Puedes usar el archivo de ejemplo proporcionado:

```bash
# Copiar el archivo de ejemplo y personalizarlo
cp .env_example .env
# Editar el archivo .env con tus valores
```

El archivo `.env_example` contiene todas las variables requeridas organizadas por categoría. Aquí están las variables clave para la API:

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
API_JWT_AUD=lus-laboris-client  # Validación de claim audience en JWT
API_JWT_ISS=lus-laboris-api     # Validación de claim issuer en JWT

# Qdrant Configuration
API_QDRANT_URL=http://localhost:6333
API_QDRANT_API_KEY=your_api_key
API_QDRANT_COLLECTION_NAME=lus_laboris_articles
API_QDRANT_GRPC_PORT=6334  # gRPC port for faster connections (default: 6334)
API_QDRANT_PREFER_GRPC=true  # Use gRPC for 2-3x better performance (default: true)

# GCP Configuration
API_GCP_PROJECT_ID=your_project_id
API_GOOGLE_APPLICATION_CREDENTIALS=.gcpcredentials/service-account.json
API_GCP_USE_CREDENTIALS=true

# Embedding Configuration
API_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
API_EMBEDDING_BATCH_SIZE=100

# Reranking Configuration
API_RERANKING_MODEL=ms-marco-MiniLM-L-6-v2
API_USE_RERANKING=false

# RAG Configuration
API_RAG_TOP_K=5
API_LLM_PROVIDER=openai
API_LLM_MODEL=gpt-3.5-turbo
API_RATE_LIMIT_REQUESTS=10
API_RATE_LIMIT_WINDOW="1 minute"  # Must use quotes for values with spaces

# Debug Configuration
API_DEBUG_CONFIG=false

# LLM API Keys
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Configuración de Monitoreo Phoenix
API_PHOENIX_ENABLED=true
API_PHOENIX_ENDPOINT=http://localhost:6006
API_PHOENIX_API_KEY=tu_phoenix_api_key_aqui
API_PHOENIX_PROJECT_NAME=lus-laboris-api

# Docker Configuration (opcional)
API_ENV_FILE_PATH=/app/.env
```

### Resolución de Rutas de Credenciales GCP

La variable `API_GOOGLE_APPLICATION_CREDENTIALS` soporta tanto rutas absolutas como relativas:

- **Ruta absoluta**: `/ruta/a/credenciales.json` - Se usa tal como está
- **Ruta relativa**: `.gcpcredentials/service-account.json` - Se resuelve desde la raíz del proyecto

**Ejemplos:**
```env
# Ruta relativa (recomendado)
API_GOOGLE_APPLICATION_CREDENTIALS=.gcpcredentials/service-account.json

# Ruta absoluta
API_GOOGLE_APPLICATION_CREDENTIALS=/home/usuario/.gcpcredentials/service-account.json
```

### Resolución de Rutas de Clave Pública JWT

La variable `API_JWT_PUBLIC_KEY_PATH` soporta tanto rutas absolutas como relativas:

- **Ruta absoluta**: `/ruta/a/public_key.pem` - Se usa tal como está
- **Ruta relativa**: `keys/public_key.pem` - Se resuelve desde la raíz del proyecto

**Ejemplos:**
```env
# Ruta relativa (recomendado)
API_JWT_PUBLIC_KEY_PATH=keys/public_key.pem

# Ruta absoluta
API_JWT_PUBLIC_KEY_PATH=/home/usuario/keys/public_key.pem
```

## Documentación de la API

### Endpoints Principales

#### Autenticación
- **Tipo**: JWT con claves RSA pública/privada
- **Header**: `Authorization: Bearer <token>`
- **Generación**: Usar scripts en `utils/`

#### Vectorstore (Qdrant)

**POST** `/api/data/load-to-vectorstore-local`
- Carga **asíncrona** de datos JSON desde archivos locales a Qdrant
- Retorna inmediatamente con información del job (HTTP 202 Accepted)
- El procesamiento ocurre en background (embeddings, inserción vectorial)
- Requiere autenticación JWT
- **La respuesta incluye**: `job_id` para hacer seguimiento
- **Phoenix Tracking**: Tracking completo con spans jerárquicos
  - Track de operación principal con payload JWT decodificado
  - Spans por etapa: carga, embedding, creación de colección, inserción
  - Métricas detalladas de tiempo y contadores por etapa

**POST** `/api/data/load-to-vectorstore-gcp`
- Carga **asíncrona** de datos JSON desde Google Cloud Storage a Qdrant
- Retorna inmediatamente con información del job (HTTP 202 Accepted)
- El procesamiento ocurre en background (embeddings, inserción vectorial)
- Requiere autenticación JWT
- **La respuesta incluye**: `job_id` para hacer seguimiento
- **Phoenix Tracking**: Tracking completo con spans jerárquicos
  - Track de operación principal con payload JWT decodificado
  - Spans por etapa: carga desde GCS, embedding, creación de colección, inserción
  - Métricas detalladas de tiempo y contadores por etapa

**GET** `/api/data/jobs`
- Listar todos los jobs de procesamiento en background
- Muestra el estado del job: `queued`, `processing`, `completed`, `failed`
- Incluye timestamps en formato ISO 8601
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
- **Phoenix Tracking**: Tracking de operación con información del usuario

#### Health Checks

**GET** `/api/health`
- Health check completo del sistema y dependencias
- **Sin autenticación requerida** - para sistemas de monitoreo
- Retorna estado del servicio, dependencias (solo status básico) y tiempo de actividad
- **Seguro para acceso público**: Solo expone nombres de servicios y su estado (connected/healthy/unhealthy)
- NO expone: nombres de modelos, IDs de proyecto, conteo de colecciones, u otros detalles sensibles

**GET** `/api/health/ready`
- Verificación de disponibilidad para balanceadores de carga y orquestadores
- **Sin autenticación requerida** - para verificación de despliegues
- Retorna estado simple de listo/no listo

**Health Checks de Servicios Específicos (Autenticación Opcional con Filtrado de Información):**

**GET** `/api/health/qdrant`
- Health check específico de Qdrant
- **Autenticación opcional**: Funciona con o sin token
- **Sin token**: Retorna solo `{"status": "connected"}` (info básica)
- **Con token JWT**: Retorna info completa incluyendo `collections_count`

**GET** `/api/health/gcp`
- Health check específico de GCP
- **Autenticación opcional**: Funciona con o sin token
- **Sin token**: Retorna solo `{"status": "connected"}` (info básica)
- **Con token JWT**: Retorna info completa incluyendo `project_id`, `buckets_count` (⚠️ sensible)

**GET** `/api/health/embeddings`
- Health check del servicio de embeddings
- **Autenticación opcional**: Funciona con o sin token
- **Sin token**: Retorna solo `{"status": "healthy"}` (info básica)
- **Con token JWT**: Retorna info completa incluyendo `loaded_models`, `device`, `model_dimensions`

**GET** `/api/health/reranking`
- Health check del servicio de reranking
- **Autenticación opcional**: Funciona con o sin token
- **Sin token**: Retorna solo `{"status": "healthy"}` (info básica)
- **Con token JWT**: Retorna info completa incluyendo `model_name`, `device`

**GET** `/api/health/rag`
- Health check del servicio RAG
- **Autenticación opcional**: Funciona con o sin token
- **Sin token**: Retorna solo `{"status": "healthy"}` (info básica)
- **Con token JWT**: Retorna info completa incluyendo `provider`, `model`, `embedding_model`

**GET** `/api/health/phoenix`
- Health check del servicio de monitoreo Phoenix
- **Autenticación opcional**: Funciona con o sin token
- **Sin token**: Retorna solo `{"status": "healthy"}` (info básica)
- **Con token JWT**: Retorna info completa incluyendo `project_name`, `active_sessions`, estado de `phoenix_connection`, y realiza test activo de conexión al collector de Phoenix

**GET** `/api/status`
- **Estado completo de TODOS los servicios** (endpoint de diagnóstico agregado)
- **Autenticación opcional**: Funciona con o sin token
- **Sin token**: Retorna solo estado básico de cada servicio `{"status": "connected/healthy"}`
- **Con token JWT**: Retorna información detallada de todos los servicios:
  - Qdrant (con conteo de colecciones)
  - GCP (con project_id y conteo de buckets)
  - Servicio de embeddings (con modelos cargados y dispositivo)
  - Servicio RAG (con proveedor, modelo, modelo de embedding)
- **Caso de uso**: 
  - Herramientas públicas de monitoreo pueden verificar salud de servicios
  - Administradores autenticados obtienen información completa de diagnóstico
- **Seguridad**: Filtrado inteligente - no se expone info sensible sin autenticación

#### RAG (Preguntas y Respuestas)

**POST** `/api/rag/ask`
- Hacer preguntas sobre derecho laboral paraguayo usando RAG
- **Sin autenticación requerida** - endpoint público con control de límites
- Límite de velocidad: 10 solicitudes por minuto por IP
- Utiliza OpenAI o Gemini LLM con contexto de Qdrant
- **Phoenix Evals**: Evaluación automática asíncrona con LLM-as-a-Judge
  - Scoring de relevancia
  - Detección de alucinaciones
  - Verificación de toxicidad
  - Verificación de grounding

**GET** `/api/rag/evaluations/status`
- Estado del servicio de evaluación e información de la cola
- **Requiere autenticación JWT** - endpoint protegido
- Retorna tamaño de la cola de evaluaciones y salud del servicio

**Métricas y Monitoreo con Phoenix**
- **Acceder a la UI de Phoenix** para ver métricas detalladas, trazas y evaluaciones:
  - Local: `http://localhost:6006`
  - Cloud: Usar tu URL de Phoenix cloud (ej: `https://app.phoenix.arize.com`)
- La UI de Phoenix proporciona:
  - Trazas y spans en tiempo real
  - Monitoreo de llamadas LLM
  - Resultados de evaluaciones y tendencias
  - Métricas de rendimiento y analíticas

#### Ejemplos de Health Check

**Endpoints públicos (sin token requerido):**
```bash
# Health check general
curl -X GET "http://localhost:8000/api/health/"

# Verificación de disponibilidad
curl -X GET "http://localhost:8000/api/health/ready"

# Estado agregado de servicios (info básica sin token)
curl -X GET "http://localhost:8000/api/status"
# Respuesta: {"services": {"qdrant": {"status": "connected"}, "gcp": {"status": "connected"}, ...}}
```

**Endpoints con autenticación opcional (info básica sin token, info detallada con token):**
```bash
# Sin token - Retorna solo estado básico
curl -X GET "http://localhost:8000/api/health/gcp"
# Respuesta: {"status": {"status": "connected"}}  ← No info sensible

curl -X GET "http://localhost:8000/api/health/embeddings"
# Respuesta: {"status": {"status": "healthy"}}  ← No info de modelos

# Con token - Retorna información detallada
curl -X GET "http://localhost:8000/api/health/gcp" \
  -H "Authorization: Bearer tu_jwt_token_aqui"
# Respuesta: {"status": {"status": "connected", "project_id": "...", "buckets_count": 2}}

curl -X GET "http://localhost:8000/api/health/embeddings" \
  -H "Authorization: Bearer tu_jwt_token_aqui"
# Respuesta: {"status": {"status": "healthy", "loaded_models": [...], "device": "cuda"}}

# Estado agregado con token - Retorna info detallada de TODOS los servicios
curl -X GET "http://localhost:8000/api/status" \
  -H "Authorization: Bearer tu_jwt_token_aqui"
# Respuesta: {"services": {"qdrant": {...info completa...}, "gcp": {...info completa...}, ...}}
```

**Endpoints RAG:**
```bash
# Hacer una pregunta (público, sin token requerido)
curl -X POST "http://localhost:8000/api/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuáles son las horas de trabajo permitidas?"}'

# Estado de evaluaciones (requiere token JWT)
curl -X GET "http://localhost:8000/api/rag/evaluations/status" \
  -H "Authorization: Bearer tu_jwt_token_aqui"
```

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
  "message": "Data loading job initiated successfully. Job ID: 550e8400-e29b-41d4-a716-446655440000. Check status at /api/data/jobs",
  "collection_name": "lus_laboris_articles",
  "documents_processed": 0,
  "documents_inserted": 0,
  "processing_time_seconds": 0.0,
  "embedding_model_used": "sentence-transformers/all-MiniLM-L6-v2",
  "vector_dimensions": 0,
  "batch_size": 100,
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### JobsListResponse
```json
{
  "success": true,
  "message": "Found 2 job(s)",
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "operation": "load_to_vectorstore_local",
      "user": "admin",
      "filename": "codigo_trabajo_articulos.json",
      "collection_name": "lus_laboris_articles",
      "created_at": "2025-10-08T20:58:08.039417",
      "started_at": "2025-10-08T20:58:08.040129",
      "completed_at": "2025-10-08T20:58:27.090524",
      "error": null,
      "result": {
        "documents_processed": 413,
        "documents_inserted": 413,
        "processing_time_seconds": 19.05
      }
    },
    {
      "job_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "processing",
      "operation": "load_to_vectorstore_local",
      "user": "admin",
      "filename": "codigo_trabajo_articulos.json",
      "collection_name": "lus_laboris_articles",
      "created_at": "2025-10-08T21:05:15.123456",
      "started_at": "2025-10-08T21:05:15.124789",
      "completed_at": null,
      "error": null,
      "result": null
    }
  ],
  "count": 2
}
```

#### QuestionRequest
```json
{
  "question": "¿Cuáles son los derechos del trabajador en caso de despido?"
}
```

#### QuestionResponse
```json
{
  "success": true,
  "message": "Question answered successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "question": "¿Cuáles son los derechos del trabajador en caso de despido?",
  "answer": "Según el Código del Trabajo paraguayo, el trabajador tiene derecho a...",
  "processing_time_seconds": 2.345,
  "documents_retrieved": 5,
  "top_k": 5,
  "reranking_applied": true,
  "documents": [
    {
      "id": 123,
      "score": 0.8542,
      "payload": {
        "articulo_numero": 45,
        "capitulo_descripcion": "Derechos del Trabajador",
        "articulo": "El trabajador tiene derecho a..."
      }
    }
  ]
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

### Seguridad de Información en Health Checks

Los endpoints de health check implementan **filtrado inteligente de información** basado en autenticación:

| Endpoint | Sin Autenticación | Con Token JWT |
|----------|------------------|---------------|
| `/api/health` | Solo status básico por servicio | **Igual** (siempre básico, seguro para público) |
| `/api/status` | Solo status básico por servicio | **Detalles completos** de todos los servicios |
| `/api/health/gcp` | `{"status": "connected"}` | `{"status": "connected", "project_id": "...", "buckets_count": 2}` |
| `/api/health/qdrant` | `{"status": "connected"}` | `{"status": "connected", "collections_count": 5}` |
| `/api/health/embeddings` | `{"status": "healthy"}` | `{"status": "healthy", "loaded_models": [...], "device": "cuda"}` |
| `/api/health/reranking` | `{"status": "healthy"}` | `{"status": "healthy", "model_name": "...", "device": "cpu"}` |
| `/api/health/rag` | `{"status": "healthy"}` | `{"status": "healthy", "provider": "openai", "model": "gpt-4"}` |
| `/api/health/phoenix` | `{"status": "healthy"}` | `{"status": "healthy", "project_name": "...", "phoenix_connection": "verified"}` |

**Beneficios de Seguridad:**
- ✅ **Previene ataques de reconocimiento**: Los atacantes no pueden mapear tu infraestructura
- ✅ **Protege datos sensibles**: IDs de proyecto, nombres de modelos, info de hardware oculta del público
- ✅ **Mantiene capacidad de monitoreo**: Herramientas externas pueden verificar el estado del servicio
- ✅ **Acceso flexible**: Usuarios autenticados obtienen información completa de diagnóstico

**Implementación:**
```python
# Sanitización automática basada en autenticación
def _sanitize_health_response(status, is_authenticated):
    if is_authenticated:
        return status  # Info completa
    else:
        return {"status": status.get("status")}  # Solo info básica
```

### Autenticación JWT

- **Algoritmo**: RS256 (RSA con SHA-256)
- **Claves**: Par de claves pública/privada RSA
- **Generación**: Scripts en `utils/`
- **Validación**: Solo clave pública (API no genera tokens)
- **Issuer (`iss`)**: Configurable vía `API_JWT_ISS` (default: `lus-laboris-api`)
- **Audience (`aud`)**: Configurable vía `API_JWT_AUD` (default: `lus-laboris-client`)

### Flujo de Autenticación

1. **Generar claves**: `utils/setup_jwt_token.sh`
2. **Generar token**: `utils/generate_jwt_token.py`
3. **Usar token**: `Authorization: Bearer <token>`

### Validación de Claims JWT

La API valida los siguientes claims:

| Claim | Descripción | Validado | Configurable |
|-------|-------------|----------|--------------|
| **`exp`** | Tiempo de expiración | ✅ Sí | Vía generación de token |
| **`iat`** | Tiempo de emisión | ✅ Sí | Vía generación de token |
| **`iss`** | Emisor (quién emitió el token) | ✅ Sí | `API_JWT_ISS` |
| **`aud`** | Audiencia (para quién es el token) | ✅ Sí | `API_JWT_AUD` |
| **`sub`** | Sujeto (username) | ℹ️ Informativo | - |

**Configuración:**
```env
API_JWT_PUBLIC_KEY_PATH=keys/public_key.pem
API_JWT_AUD=lus-laboris-client
API_JWT_ISS=lus-laboris-api
```

**Beneficios de Seguridad:**
- ✅ Previene reutilización de tokens entre sistemas diferentes
- ✅ Valida el origen del token (issuer)
- ✅ Valida el destino del token (audience)
- ✅ Sigue las mejores prácticas de RFC 7519

### Separación de Responsabilidades

- **API**: Solo valida tokens con clave pública
- **Utils**: Genera claves y tokens con clave privada
- **Seguridad**: Token válido = acceso autorizado

## Optimizaciones de Rendimiento

La API implementa varias optimizaciones de rendimiento para uso en producción:

### 1. Conexión gRPC con Qdrant (2-3x más rápido)
- **Protocolo**: Prefiere gRPC sobre HTTP para operaciones vectoriales
- **Puerto**: 6334 (configurable vía `API_QDRANT_GRPC_PORT`)
- **Fallback**: Recurre automáticamente a HTTP si gRPC no está disponible
- **Impacto**: Latencia de búsqueda reducida de ~200ms a ~70ms
- **Beneficios**:
  - Protocolo binario (más eficiente que JSON)
  - Multiplexing HTTP/2
  - Mejor compresión
  - Menor uso de CPU

### 2. Cache de Health Checks (430x más rápido)
- **TTL**: 5 segundos (previene verificaciones redundantes de servicios)
- **Alcance**: Todos los endpoints de health check
- **Impacto**: Tiempo de respuesta de ~430ms a <1ms en cache hit
- **Beneficios**:
  - Reduce carga en servicios externos (Qdrant, GCP)
  - Mejor manejo de herramientas de monitoreo que hacen polling
  - Menor uso de CPU y red

### 3. Ejecución Paralela de Health Checks (2.15x más rápido)
- **Método**: `asyncio.gather()` para ejecución concurrente
- **Endpoints**: `/api/health/` principal
- **Impacto**: Latencia de ~430ms a ~200ms
- **Beneficios**:
  - Todas las verificaciones de servicio se ejecutan simultáneamente
  - Falla gracefully si un servicio está caído
  - Mejor utilización de recursos

### 4. Llamadas Asíncronas a LLM (1.39x más rápido)
- **Librería**: Cliente `AsyncOpenAI` para llamadas no bloqueantes
- **Impacto**: Tiempo de respuesta de ~2.5s a ~1.8s
- **Beneficio**: Mejor utilización de recursos, maneja peticiones concurrentes eficientemente
- **Retry**: Usa `AsyncRetrying` de tenacity para manejo robusto de errores

### 5. Evaluaciones Phoenix en Paralelo (3x más rápido)
- **Método**: `asyncio.gather()` para ejecución concurrente de evaluaciones
- **Evaluaciones**: Relevancia, Alucinación, Toxicidad se ejecutan en paralelo
- **Impacto**: Tiempo de evaluación de ~6s a ~2s
- **Background**: Se ejecuta asíncronamente sin bloquear la respuesta principal

### Configuración

```env
# Habilitar gRPC para Qdrant (recomendado para producción)
API_QDRANT_PREFER_GRPC=true
API_QDRANT_GRPC_PORT=6334

# Qdrant debe estar ejecutándose con gRPC habilitado
# Docker: qdrant/qdrant:latest (gRPC habilitado por defecto en puerto 6334)
```

### Métricas de Rendimiento

| Optimización | Antes | Después | Mejora |
|--------------|-------|---------|--------|
| **Búsqueda en Qdrant** | ~200ms | ~70ms | **2.85x más rápido** |
| **Health Check (cache miss)** | ~430ms | ~200ms | **2.15x más rápido** |
| **Health Check (cache hit)** | ~430ms | <1ms | **430x más rápido** |
| **Llamadas a servicios por 10s** | 12 llamadas | ~2 llamadas | **83% reducción** |
| **Respuesta LLM (async)** | ~2.5s | ~1.8s | **1.39x más rápido** |
| **Phoenix Evals (paralelo)** | ~6s | ~2s | **3x más rápido** |

## Servicios

### QdrantService
- **Optimización gRPC**: Usa gRPC para consultas 2-3x más rápidas que HTTP
- **Fallback Automático**: Recurre a HTTP si gRPC no está disponible
- **Connection Pooling**: Mantiene conexiones persistentes
- **Timeout Configurable**: 10 segundos por defecto para todas las operaciones
- Conexión y operaciones con Qdrant
- Creación/eliminación de colecciones
- Inserción y búsqueda de documentos
- Health checks con reporte de tipo de conexión (gRPC/HTTP)

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
- **Detección automática de dispositivo**: CPU/GPU según disponibilidad
- **Configuración centralizada**: Modelo y tamaño de lote desde config

### RerankingService
- Reranking de documentos usando modelos cross-encoder
- Mejora la relevancia de los documentos recuperados
- Servicio opcional (puede deshabilitarse vía configuración)
- **Detección automática de dispositivo**: CPU/GPU según disponibilidad
- **Configuración centralizada**: Modelo y uso desde config
- **Comportamiento de respaldo**: Retorna documentos originales si el reranking falla

### RAGService
- RAG (Retrieval-Augmented Generation) para preguntas y respuestas
- **Llamadas Async a LLM**: Usa `AsyncOpenAI` para respuestas no bloqueantes (1.39x más rápido)
- Soporte para LLMs de OpenAI y Google Gemini
- Búsqueda semántica usando embeddings y Qdrant
- **Reranking opcional de documentos** para mejorar relevancia
- Construcción de contexto desde documentos legales
- **Lógica de Retry Async**: Manejo robusto de errores con `AsyncRetrying` de tenacity
- Respuesta comprensiva con metadatos e información de reranking

### PhoenixMonitoringService
- **Monitoreo de LLM**: Tracking completo de llamadas a APIs de OpenAI y Gemini
- **Gestión de Sesiones**: Agrupa todas las acciones dentro de sesiones de ejecución
- **Métricas de Calidad**: Evaluación automática de coherencia, relevancia y completitud de respuestas
- **Tracking de Rendimiento**: Monitorea generación de embeddings, búsquedas en vectorstore y reranking
- **Integración OpenTelemetry**: Observabilidad completa con trazabilidad distribuida
- **No intrusivo**: Tracking asíncrono sin afectar el rendimiento de la API
- **Spans Jerárquicos**: Relaciones padre-hijo para operaciones complejas

### EvaluationService

**NUEVO**: Servicio de evaluación asíncrona usando Phoenix Evals (LLM-as-a-Judge):
- **Procesamiento Asíncrono**: Las evaluaciones se ejecutan en background sin bloquear las respuestas al usuario
- **Integración Phoenix Evals**: Usa templates de evaluación probados de Arize Phoenix
- **Evaluaciones en Paralelo (3x más rápido)**: Las 3 evaluaciones (Relevancia, Alucinación, Toxicidad) se ejecutan simultáneamente usando `asyncio.gather()`, reduciendo el tiempo de ~6s a ~2s
- **Métricas de Evaluación**:
  - **Relevancia**: Qué tan relevante es la respuesta a la pregunta (0.0-1.0)
  - **Alucinación**: La respuesta contiene información no presente en el contexto (0.0-1.0)
  - **Toxicidad**: La respuesta contiene contenido ofensivo (0.0-1.0)
  - **Grounding**: La respuesta se basa únicamente en el contexto proporcionado (0.0-1.0)
  - **Calidad General**: Promedio ponderado de todas las métricas
- **Arquitectura Basada en Cola**: ThreadPoolExecutor con 2 workers procesa evaluaciones
- **GPT-4o-mini**: Usa modelo cost-effective para evaluaciones
- **Shutdown Graceful**: Asegura que las evaluaciones pendientes se completen antes del cierre
- **Sin Impacto en Latencia**: Usuario recibe respuesta inmediatamente (~1.8s con async), evaluación ocurre en background (~2s con paralelo)

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

## Phoenix Evals - Evaluación Automática de Calidad

### ¿Qué es Phoenix Evals?

Phoenix Evals es un sistema de evaluación de calidad para sistemas RAG que usa **LLM-as-a-Judge** (un LLM para evaluar las respuestas de otro LLM).

### Arquitectura de Evaluación

```
Usuario hace pregunta
    ↓
RAG genera respuesta (2-3s)
    ↓
✅ Usuario recibe respuesta (sin bloqueo)
    ↓
📊 Evaluación encolada
    ↓
🔄 Worker evalúa en background (2-5s)
    - Relevancia
    - Alucinaciones
    - Toxicidad
    - Grounding
    ↓
💾 Métricas guardadas en Phoenix
```

### Métricas Evaluadas

| Métrica | Descripción | Rango | Peso |
|---------|-------------|-------|------|
| **Relevance** | ¿La respuesta es relevante a la pregunta? | 0.0-1.0 | 50% |
| **Hallucination** | ¿Inventa información no presente en el contexto? | 0.0-1.0 | - |
| **Grounding** | ¿Se basa únicamente en el contexto? (1.0 - hallucination) | 0.0-1.0 | 40% |
| **Toxicity** | ¿Contiene contenido ofensivo? | 0.0-1.0 | 10% |
| **Overall Quality** | Promedio ponderado de todas las métricas | 0.0-1.0 | 100% |

### Ver Evaluaciones en Phoenix

1. Abrir Phoenix UI: `http://localhost:6006`
2. Seleccionar proyecto: `lus-laboris-api`
3. Filtrar por `operation_type: llm_evaluation`
4. Ver métricas en los atributos del span

### Costos de Evaluación

- **Modelo usado**: GPT-4o-mini (~$0.150 / 1M tokens input, ~$0.600 / 1M tokens output)
- **Tokens por evaluación**: ~500-1000 tokens
- **Costo estimado**: ~$0.0005-0.001 por evaluación
- **Para 1000 evaluaciones/día**: ~$0.50-1.00/día

### Deshabilitar Evaluaciones

Si no quieres usar evaluaciones (para reducir costos):

```env
# En .env
API_PHOENIX_ENABLED=false
```

## Documentación Adicional

- **Utils**: `utils/README.md` - Scripts de utilidades
- **Docker Guide**: `docs/docker_guide.md` - Guía completa de Docker
- **Qdrant Guide**: `docs/qdrant_guide.md` - Guía de Qdrant
- **FastAPI Guide**: `docs/fastapi_guide.md` - Guía de FastAPI
- **Phoenix Evals**: `api/services/evaluation_service.py` - Implementación de evaluaciones
- **UV Guide**: `docs/uv_guide.md` - Guía de UV
- **GCP Setup**: `docs/setup_gcp_project.md` - Configuración de GCP
- **Monitoreo Phoenix**: Monitoreo integrado de LLM con tracking de sesiones y métricas de calidad