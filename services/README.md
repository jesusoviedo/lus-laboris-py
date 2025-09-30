<div align="center">

**Language / Idioma:**
[🇺🇸 English](#services) | [🇪🇸 Español](#servicios)

</div>

---
# Services

This directory contains the external services required by the RAG system, each managed independently with Docker Compose for easy local development and testing.

## Contents

- `vectordb/` - Qdrant vector database service
- `monitoring/` - Phoenix observability and monitoring service
- `manage_services.sh` - Interactive script to manage all services
- `README.md` - This documentation file

## Quick Start

### Using the Management Script (Recommended)

1. Navigate to the services directory:
   ```bash
   cd services
   ```

2. Run the management script:
   ```bash
   ./manage_services.sh
   ```

3. Follow the interactive menu to start, stop, or manage services.

### Manual Service Management

#### Start Qdrant
```bash
cd vectordb
docker-compose up -d
```

#### Start Phoenix
```bash
cd monitoring
docker-compose up -d
```

## Service Details

### Qdrant (Vector Database)

**Location**: `vectordb/`
**Purpose**: Vector database for semantic search and document retrieval
**Ports**: 6333 (HTTP), 6334 (gRPC)
**UI**: http://localhost:6333/dashboard

**Features**:
- Semantic search using vector embeddings
- Metadata filtering capabilities
- REST API for integration
- Web dashboard for management

**Documentation**: [Qdrant Guide](../docs/qdrant_guide.md)

### Phoenix (Monitoring & Observability)

**Location**: `monitoring/`
**Purpose**: Real-time monitoring and evaluation for RAG system
**Ports**: 6006 (UI), 4317 (gRPC), 9090 (Prometheus)
**UI**: http://localhost:6006

**Features**:
- Real-time trace analysis
- Performance metrics tracking
- LLM monitoring (OpenAI, Gemini)
- RAG system evaluation
- Interactive dashboard

**Documentation**: [Phoenix Guide](../docs/phoenix_guide.md)

## Management Script

The `manage_services.sh` script provides an interactive interface to manage all services:

### Available Actions

- **Start Service**: Start individual services or all services
- **Stop Service**: Stop individual services or all services
- **Restart Service**: Restart individual services or all services
- **Show Logs**: View real-time logs for any service
- **Show Status**: Check the current status of all services

### Usage

```bash
# Make script executable (if not already)
chmod +x manage_services.sh

# Run the script
./manage_services.sh
```

### Script Features

- **Interactive Menu**: Easy-to-use command-line interface
- **Service Status**: Real-time status display
- **Error Handling**: Comprehensive error checking and reporting
- **Docker Validation**: Ensures Docker is running before operations
- **Colored Output**: Clear visual feedback for different operations

## Configuration

### Environment Variables

Both services use environment variables from the project root `.env` file:

```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key_here
...

# Phoenix Configuration
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
PHOENIX_GRPC_ENDPOINT=localhost:4317
...
```

### Docker Compose

Each service has its own `docker-compose.yml` file:
- **vectordb/docker-compose.yml**: Qdrant configuration
- **monitoring/docker-compose.yml**: Phoenix configuration

## Integration

### With RAG API

Both services are integrated with the main RAG API:

1. **Qdrant**: Used for document storage and semantic search
2. **Phoenix**: Used for monitoring API performance and RAG metrics

### Service Dependencies

- **RAG API** depends on **Qdrant** for document retrieval
- **Phoenix** monitors **RAG API** performance
- **Qdrant** and **Phoenix** are independent services

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker status
docker info

# Check if ports are available
netstat -tulpn | grep :6333  # Qdrant
netstat -tulpn | grep :6006  # Phoenix
```

#### Permission Issues
```bash
# Make script executable
chmod +x manage_services.sh
```

#### Service Not Responding
```bash
# Check service logs
./manage_services.sh
# Select option 'l' for logs
```

### Logs and Debugging

```bash
# View Qdrant logs
cd vectordb
docker-compose logs -f

# View Phoenix logs
cd monitoring
docker-compose logs -f
```

## Best Practices

1. **Start Services First**: Always start Qdrant before the RAG API
2. **Use Management Script**: Prefer the management script over manual commands
3. **Check Status**: Use the status option to verify services are running
4. **Monitor Logs**: Check logs if services are not working properly
5. **Clean Shutdown**: Always stop services properly using the script

---

# Servicios

Este directorio contiene los servicios externos requeridos por el sistema RAG, cada uno gestionado independientemente con Docker Compose para facilitar el desarrollo y pruebas locales.

## Contenidos

- `vectordb/` - Servicio de base de datos vectorial Qdrant
- `monitoring/` - Servicio de observabilidad y monitoreo Phoenix
- `manage_services.sh` - Script interactivo para gestionar todos los servicios
- `README.md` - Este archivo de documentación

## Inicio Rápido

### Usando el Script de Gestión (Recomendado)

1. Navegar al directorio de servicios:
   ```bash
   cd services
   ```

2. Ejecutar el script de gestión:
   ```bash
   ./manage_services.sh
   ```

3. Seguir el menú interactivo para iniciar, detener o gestionar servicios.

### Gestión Manual de Servicios

#### Iniciar Qdrant
```bash
cd vectordb
docker-compose up -d
```

#### Iniciar Phoenix
```bash
cd monitoring
docker-compose up -d
```

## Detalles de Servicios

### Qdrant (Base de Datos Vectorial)

**Ubicación**: `vectordb/`
**Propósito**: Base de datos vectorial para búsqueda semántica y recuperación de documentos
**Puertos**: 6333 (HTTP), 6334 (gRPC)
**UI**: http://localhost:6333/dashboard

**Características**:
- Búsqueda semántica usando embeddings vectoriales
- Capacidades de filtrado de metadatos
- API REST para integración
- Dashboard web para gestión

**Documentación**: [Guía de Qdrant](../docs/qdrant_guide.md)

### Phoenix (Monitoreo y Observabilidad)

**Ubicación**: `monitoring/`
**Propósito**: Monitoreo en tiempo real y evaluación para el sistema RAG
**Puertos**: 6006 (UI), 4317 (gRPC), 9090 (Prometheus)
**UI**: http://localhost:6006

**Características**:
- Análisis de trazas en tiempo real
- Seguimiento de métricas de rendimiento
- Monitoreo de LLM (OpenAI, Gemini)
- Evaluación del sistema RAG
- Dashboard interactivo

**Documentación**: [Guía de Phoenix](../docs/phoenix_guide.md)

## Script de Gestión

El script `manage_services.sh` proporciona una interfaz interactiva para gestionar todos los servicios:

### Acciones Disponibles

- **Iniciar Servicio**: Iniciar servicios individuales o todos los servicios
- **Detener Servicio**: Detener servicios individuales o todos los servicios
- **Reiniciar Servicio**: Reiniciar servicios individuales o todos los servicios
- **Mostrar Logs**: Ver logs en tiempo real de cualquier servicio
- **Mostrar Estado**: Verificar el estado actual de todos los servicios

### Uso

```bash
# Hacer el script ejecutable (si no lo está ya)
chmod +x manage_services.sh

# Ejecutar el script
./manage_services.sh
```

### Características del Script

- **Menú Interactivo**: Interfaz de línea de comandos fácil de usar
- **Estado de Servicios**: Visualización de estado en tiempo real
- **Manejo de Errores**: Verificación de errores y reportes completos
- **Validación de Docker**: Asegura que Docker esté ejecutándose antes de las operaciones
- **Salida Coloreada**: Retroalimentación visual clara para diferentes operaciones

## Configuración

### Variables de Entorno

Ambos servicios usan variables de entorno del archivo `.env` en la raíz del proyecto:

```env
# Configuración de Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=tu_clave_api_aqui
...

# Configuración de Phoenix
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006/v1/traces
PHOENIX_GRPC_ENDPOINT=localhost:4317
...
```

### Docker Compose

Cada servicio tiene su propio archivo `docker-compose.yml`:
- **vectordb/docker-compose.yml**: Configuración de Qdrant
- **monitoring/docker-compose.yml**: Configuración de Phoenix

## Integración

### Con API RAG

Ambos servicios están integrados con la API RAG principal:

1. **Qdrant**: Usado para almacenamiento de documentos y búsqueda semántica
2. **Phoenix**: Usado para monitorear el rendimiento de la API y métricas RAG

### Dependencias de Servicios

- **API RAG** depende de **Qdrant** para recuperación de documentos
- **Phoenix** monitorea el rendimiento de **API RAG**
- **Qdrant** y **Phoenix** son servicios independientes

## Solución de Problemas

### Problemas Comunes

#### Los Servicios No Inician
```bash
# Verificar estado de Docker
docker info

# Verificar si los puertos están disponibles
netstat -tulpn | grep :6333  # Qdrant
netstat -tulpn | grep :6006  # Phoenix
```

#### Problemas de Permisos
```bash
# Hacer el script ejecutable
chmod +x manage_services.sh
```

#### Servicio No Responde
```bash
# Verificar logs del servicio
./manage_services.sh
# Seleccionar opción 'l' para logs
```

### Logs y Depuración

```bash
# Ver logs de Qdrant
cd vectordb
docker-compose logs -f

# Ver logs de Phoenix
cd monitoring
docker-compose logs -f
```

## Mejores Prácticas

1. **Iniciar Servicios Primero**: Siempre iniciar Qdrant antes que la API RAG
2. **Usar Script de Gestión**: Preferir el script de gestión sobre comandos manuales
3. **Verificar Estado**: Usar la opción de estado para verificar que los servicios estén ejecutándose
4. **Monitorear Logs**: Verificar logs si los servicios no funcionan correctamente
5. **Apagado Limpio**: Siempre detener los servicios correctamente usando el script
