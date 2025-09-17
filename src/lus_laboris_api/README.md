# Lus Laboris API

API REST en FastAPI para búsqueda semántica y recuperación de información de la ley laboral paraguaya usando Qdrant como base de datos vectorial.

## 📁 Estructura del Proyecto

```
src/lus_laboris_api/
├── api/                      # Aplicación FastAPI
│   ├── main.py              # Aplicación principal FastAPI
│   ├── config.py            # Configuración centralizada
│   ├── auth/                # Módulos de autenticación
│   │   ├── jwt_handler.py   # Validación JWT con clave pública
│   │   └── security.py      # Gestión de seguridad y permisos
│   ├── endpoints/           # Endpoints de la API
│   │   ├── vectorstore.py   # Operaciones con Qdrant
│   │   └── health.py        # Health checks
│   ├── services/            # Servicios de negocio
│   │   ├── qdrant_service.py    # Operaciones con Qdrant
│   │   ├── gcp_service.py       # Operaciones con Google Cloud
│   │   └── embedding_service.py # Generación de embeddings
│   └── models/              # Modelos Pydantic
│       ├── requests.py      # Modelos de solicitudes
│       └── responses.py     # Modelos de respuestas
├── start_api_dev.sh         # Script de desarrollo
└── README.md                # Este archivo
```

## 🚀 Inicio Rápido

### Desarrollo

```bash
# Ir al directorio de la API
cd src/lus_laboris_api/

# Ejecutar script de desarrollo
./start_api_dev.sh
```

### Características del Script de Desarrollo

- ✅ **Recarga automática** cuando cambias el código
- ✅ **Logs detallados** en consola
- ✅ **Variables de entorno opcionales** (usa valores por defecto)
- ✅ **Verificaciones automáticas** de requisitos
- ✅ **Información clara** de URLs y configuración

## 🌐 URLs Disponibles

Una vez iniciada la API:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## 🔧 Configuración

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
API_EMBEDDING_DEVICE=cpu
```

### Valores por Defecto

Si no se proporciona un archivo `.env`, la API usará estos valores:

- **Host**: `0.0.0.0`
- **Puerto**: `8000`
- **Qdrant**: `http://localhost:6333`
- **Modelo de Embedding**: `sentence-transformers/all-MiniLM-L6-v2`

## 📚 Documentación de la API

### Endpoints Principales

#### 🔐 Autenticación
- **Tipo**: JWT con claves RSA pública/privada
- **Header**: `Authorization: Bearer <token>`
- **Generación**: Usar scripts en `utils/`

#### 📊 Vectorstore (Qdrant)

**POST** `/api/data/load-to-vectorstore`
- Cargar datos JSON a Qdrant
- Modos: `local` (archivos locales) o `gcp` (Google Cloud Storage)
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

#### 🏥 Health Checks

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

#### LoadToVectorstoreRequest
```json
{
  "mode": "local",
  "filename": "codigo_trabajo_articulos.json",
  "collection_name": "labor_law_articles",
  "local_data_path": "data/processed",
  "batch_size": 100,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "replace_collection": false
}
```

#### LoadToVectorstoreResponse
```json
{
  "success": true,
  "message": "Data loaded successfully to vectorstore",
  "collection_name": "labor_law_articles",
  "documents_processed": 410,
  "documents_inserted": 410,
  "processing_time_seconds": 45.2,
  "embedding_model_used": "sentence-transformers/all-MiniLM-L6-v2",
  "vector_dimensions": 384,
  "batch_size": 100
}
```

## 🔒 Seguridad

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

## 🛠️ Servicios

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

## 📋 Requisitos

### Sistema
- **Python**: 3.8+
- **uv**: Instalador de paquetes Python
- **Qdrant**: Base de datos vectorial
- **Opcional**: Google Cloud Platform

### Dependencias Python
- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `qdrant-client` - Cliente Qdrant
- `sentence-transformers` - Modelos de embeddings
- `google-cloud-storage` - Cliente GCS
- `pydantic` - Validación de datos
- `PyJWT` - Manejo de JWT
- `cryptography` - Criptografía RSA

## 🔧 Desarrollo

### Estructura de Código

- **Modular**: Separación clara de responsabilidades
- **Configuración centralizada**: `config.py` con Pydantic Settings
- **Manejo de errores**: Excepciones HTTP apropiadas
- **Logging**: Logs estructurados en todos los servicios
- **Type hints**: Tipado completo en Python

### Patrones de Diseño

- **Dependency Injection**: FastAPI dependencies
- **Service Layer**: Lógica de negocio en servicios
- **Repository Pattern**: Abstracción de datos
- **Factory Pattern**: Creación de modelos de embedding

## 🐛 Solución de Problemas

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

## 📖 Documentación Adicional

- **Utils**: `utils/README.md` - Scripts de utilidades
- **Guía Qdrant**: `docs/qdrant_guide.md` - Guía de Qdrant
- **Guía UV**: `docs/uv_guide.md` - Guía de UV

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama de feature
3. Hacer cambios
4. Ejecutar tests
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.