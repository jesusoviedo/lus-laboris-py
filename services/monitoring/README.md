<div align="center">

**Language / Idioma:**
[🇺🇸 English](#contents) | [🇪🇸 Español](#contenidos)

</div>

---

# Monitoring

This folder contains the configuration and setup for Phoenix monitoring service, which provides real-time observability and evaluation capabilities for the RAG system.

## Contents

- `docker-compose.yml` - Docker Compose configuration for running Phoenix locally
- `README.md` - This documentation file

## Quick Start

### Using Docker Compose

1. Navigate to this directory:

   ```bash
   cd services/monitoring
   ```

2. Start Phoenix:

   ```bash
   docker-compose up -d
   ```

3. Verify Phoenix is running:

   ```bash
   curl http://localhost:6006/health
   ```

4. Access the Phoenix UI:
   - Open your browser and go to: <http://localhost:6006>

### Configuration

Phoenix runs locally without requiring additional configuration. The service uses default ports and settings suitable for local development.

**Ports Used**:

- `6006`: Phoenix UI and HTTP collector
- `4317`: gRPC collector
- `9090`: Prometheus metrics (if enabled)

> **Note**: For API integration with Phoenix, see the API configuration section in `src/lus_laboris_api/README.md` which uses `API_PHOENIX_*` environment variables.

## Documentation

For comprehensive monitoring and observability documentation, see:

- [Phoenix Guide](../../docs/phoenix_guide.md) - Complete guide for setting up and using Phoenix
- [Phoenix Documentation](https://arize.com/docs/phoenix/) - Official Phoenix documentation

## Production Deployment

**Personal Projects**: Use [Phoenix Cloud](https://arize.com/phoenix) (recommended)

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

- **Real-time Observability**: Monitor RAG system performance in real-time
- **Trace Analysis**: Detailed tracing of requests through the RAG pipeline
- **Performance Metrics**: Track response times, token usage, and accuracy
- **LLM Monitoring**: Monitor OpenAI and Gemini API usage and performance
- **Evaluation Metrics**: Track retrieval and generation quality metrics

## Integration

The monitoring service is integrated with:

- **RAG API**: Real-time instrumentation of question-answering endpoints
- **LLM Providers**: OpenAI and Google Gemini usage tracking
- **Vector Database**: Qdrant search performance monitoring
- **Embedding Service**: Sentence transformers performance tracking

## Ports

- **6006**: Phoenix UI and OTLP HTTP collector
- **4317**: OTLP gRPC collector
- **9090**: Prometheus metrics (optional)

---

# Monitoring

Esta carpeta contiene la configuración y setup del servicio de monitoreo Phoenix, que proporciona capacidades de observabilidad y evaluación en tiempo real para el sistema RAG.

## Contenidos

- `docker-compose.yml` - Configuración de Docker Compose para ejecutar Phoenix localmente
- `README.md` - Este archivo de documentación

## Inicio Rápido

### Usando Docker Compose

1. Navegar a este directorio:

   ```bash
   cd services/monitoring
   ```

2. Iniciar Phoenix:

   ```bash
   docker-compose up -d
   ```

3. Verificar que Phoenix esté ejecutándose:

   ```bash
   curl http://localhost:6006/health
   ```

4. Acceder a la UI de Phoenix:
   - Abrir el navegador y ir a: <http://localhost:6006>

### Configuración

Phoenix se ejecuta localmente sin requerir configuración adicional. El servicio usa puertos y configuraciones predeterminadas adecuadas para desarrollo local.

**Puertos Utilizados**:

- `6006`: UI de Phoenix y colector HTTP
- `4317`: Colector gRPC
- `9090`: Métricas de Prometheus (si está habilitado)

> **Nota**: Para integración con la API de Phoenix, consulta la sección de configuración de la API en `src/lus_laboris_api/README.md` que usa variables de entorno `API_PHOENIX_*`.

## Documentación

Para documentación completa de monitoreo y observabilidad, consulta:

- [Guía de Phoenix](../../docs/phoenix_guide.md) - Guía completa para configurar y usar Phoenix
- [Documentación de Phoenix](https://arize.com/docs/phoenix/) - Documentación oficial de Phoenix

## Despliegue en Producción

**Proyectos Personales**: Usa [Phoenix Cloud](https://arize.com/phoenix) (recomendado)

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

- **Observabilidad en Tiempo Real**: Monitorear el rendimiento del sistema RAG en tiempo real
- **Análisis de Trazas**: Trazado detallado de solicitudes a través del pipeline RAG
- **Métricas de Rendimiento**: Rastrear tiempos de respuesta, uso de tokens y precisión
- **Monitoreo de LLM**: Monitorear el uso y rendimiento de las APIs de OpenAI y Gemini
- **Métricas de Evaluación**: Rastrear métricas de calidad de recuperación y generación

## Integración

El servicio de monitoreo está integrado con:

- **API RAG**: Instrumentación en tiempo real de endpoints de preguntas y respuestas
- **Proveedores de LLM**: Seguimiento del uso de OpenAI y Google Gemini
- **Base de Datos Vectorial**: Monitoreo del rendimiento de búsqueda de Qdrant
- **Servicio de Embeddings**: Seguimiento del rendimiento de sentence transformers

## Puertos

- **6006**: UI de Phoenix y colector OTLP HTTP
- **4317**: Colector OTLP gRPC
- **9090**: Métricas de Prometheus (opcional)
