<div align="center">

**Language / Idioma:**
[🇺🇸 English](#google-cloud-platform-resources-guide) | [🇪🇸 Español](#guía-de-recursos-de-google-cloud-platform)

</div>

---

# Google Cloud Platform Resources Guide

This guide provides basic knowledge about the Google Cloud Platform resources used in this project. Understanding these resources will help you work with the Terraform infrastructure and the overall system architecture.

## What is Google Cloud Platform (GCP)?

Google Cloud Platform is a suite of cloud computing services that provides infrastructure, platform, and software services for building, deploying, and scaling applications.

## Resources Used in This Project

### Google Cloud Storage (GCS)

**What it is:**
A scalable object storage service for storing and retrieving any amount of data at any time.

**How we use it:**

- Stores raw and processed legal documents
- Stores extracted JSON data from legal text processing
- Provides a centralized data repository accessible by all services

**When you'll encounter it:**

- In `terraform/modules/gcs/` - Terraform module that creates the bucket
- In `src/processing/` - Scripts that upload/download data
- In data pipeline workflows

**Basic concepts:**

- **Bucket**: Container for storing objects (like a folder)
- **Object**: Individual file stored in a bucket
- **Uniform bucket-level access**: Security setting that uses IAM for all permissions

### Cloud Run (Service)

**What it is:**
A fully managed platform for running containerized applications that automatically scales based on incoming requests.

**How we use it:**

- Hosts the FastAPI application
- Provides the public REST API for legal queries
- Automatically scales from 0 to multiple instances based on traffic

**When you'll encounter it:**

- In `terraform/modules/cloud_run_service/` - Terraform module
- In `src/lus_laboris_api/` - The application code
- In API deployment workflows

**Basic concepts:**

- **Service**: Long-running application that responds to HTTP requests
- **Revision**: Immutable snapshot of a service configuration
- **Traffic splitting**: Route percentage of traffic to different revisions
- **Autoscaling**: Automatic adjustment of instance count based on load

### Cloud Run (Job/Batch)

**What it is:**
A managed service for running containerized tasks that run to completion and then stop.

**How we use it:**

- Scheduled extraction of legal text from official sources
- Runs on a cron schedule (e.g., daily at 23:00)
- Processes data and uploads results to Cloud Storage

**When you'll encounter it:**

- In `terraform/modules/cloud_run_job/` - Terraform module
- In `src/processing/` - The batch processing code
- In scheduled job workflows

**Basic concepts:**

- **Job**: Task that runs to completion (vs service that runs continuously)
- **Execution**: Single run of a job
- **Schedule**: Cron expression defining when job runs
- **Cloud Scheduler**: Service that triggers jobs on schedule

### Compute Engine

**What it is:**
Virtual machines (VMs) running on Google's infrastructure, providing full control over the computing environment.

**How we use it:**

- Hosts the Qdrant vector database
- Provides persistent storage and compute for the vector store
- Configured as a SPOT instance for cost optimization

**When you'll encounter it:**

- In `terraform/modules/compute_engine/` - Terraform module
- In deployment scripts for Qdrant
- In VM management operations

**Basic concepts:**

- **Instance**: A virtual machine
- **Machine type**: CPU and memory configuration (e.g., e2-micro)
- **Zone**: Physical location where the VM runs
- **SPOT instance**: Preemptible VM at lower cost
- **Firewall rules**: Network security rules controlling access

### Secret Manager

**What it is:**
A secure service for storing, managing, and accessing sensitive information like API keys, passwords, and configuration files.

**How we use it:**

- Stores the complete `.env` configuration file
- Stores JWT public key for authentication
- Provides secrets to Cloud Run service at runtime
- Secrets are updated via GitHub Actions workflows

**When you'll encounter it:**

- In `terraform/modules/secret_manager/` - Terraform module
- In deployment workflows that update secrets
- In Cloud Run configuration (mounted as volumes)

**Basic concepts:**

- **Secret**: Named container for sensitive data
- **Version**: Immutable snapshot of secret content
- **IAM binding**: Permission that grants access to a secret
- **Secret accessor role**: Permission to read secret values
- **Automatic rotation**: Ability to update secrets without redeployment

### Cloud Scheduler

**What it is:**
A fully managed cron job service for scheduling virtually any job, including batch jobs, big data jobs, and cloud infrastructure operations.

**How we use it:**

- Triggers Cloud Run Job on a schedule
- Configured to run daily at 23:00 (Paraguay time)
- Sends notifications on job completion (success/failure)

**When you'll encounter it:**

- In `terraform/modules/cloud_run_job/` - Created alongside the job
- In job monitoring and logs
- In schedule configuration

**Basic concepts:**

- **Schedule**: Cron expression (e.g., "0 23 ** *" = daily at 23:00)
- **Time zone**: Timezone for schedule interpretation
- **HTTP target**: Endpoint to call when schedule triggers
- **OAuth token**: Authentication for calling Cloud Run

### Cloud Monitoring & Logging

**What it is:**
Services for collecting, analyzing, and visualizing metrics and logs from GCP resources.

**How we use it:**

- Alert policies for job success/failure
- Email notifications when jobs complete
- Log collection from all services
- Performance monitoring

**When you'll encounter it:**

- In `terraform/modules/cloud_run_job/` - Alert configurations
- In application logs
- When troubleshooting issues

**Basic concepts:**

- **Log**: Record of events from an application or service
- **Metric**: Numerical measurement of system behavior
- **Alert policy**: Rule that triggers notification when conditions are met
- **Notification channel**: Destination for alerts (e.g., email)

## How These Resources Work Together

```text
┌─────────────────────────────────────────────────────────┐
│              Cloud Scheduler (Cron)                      │
│  Triggers daily at 23:00                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Cloud Run Job (Batch Processing)                │
│  Extracts legal text, processes data                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Cloud Storage (GCS Bucket)                     │
│  Stores processed legal documents                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│      Compute Engine VM (Qdrant Vector DB)              │
│  Indexes documents for semantic search                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Cloud Run Service (FastAPI API)                 │
│  ├── Reads config from Secret Manager                  │
│  ├── Queries Qdrant for semantic search                │
│  └── Returns AI-powered legal answers                  │
└─────────────────────────────────────────────────────────┘
```

## Cost Optimization

The infrastructure is configured for cost efficiency:

- **Cloud Run Service**: Scales to 0 when not in use (pay only for requests)
- **Cloud Run Job**: Only runs when scheduled (not continuously)
- **Compute Engine**: SPOT instance (up to 91% cheaper than regular VMs)
- **Cloud Storage**: Standard storage class with lifecycle management
- **Secret Manager**: Minimal cost (secrets are small)

## Security

Each resource implements security best practices:

- **IAM roles**: Principle of least privilege
- **Secret Manager**: Encrypted at rest, access controlled
- **Firewall rules**: Only necessary ports open
- **Service accounts**: Separate accounts for each service
- **HTTPS only**: All external communication encrypted

## Learn More

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)

---

# Guía de Recursos de Google Cloud Platform

Esta guía proporciona conocimientos básicos sobre los recursos de Google Cloud Platform utilizados en este proyecto. Comprender estos recursos te ayudará a trabajar con la infraestructura de Terraform y la arquitectura general del sistema.

## ¿Qué es Google Cloud Platform (GCP)?

Google Cloud Platform es un conjunto de servicios de computación en la nube que proporciona servicios de infraestructura, plataforma y software para construir, desplegar y escalar aplicaciones.

## Recursos Utilizados en Este Proyecto

### Google Cloud Storage (GCS)

**Qué es:**
Un servicio de almacenamiento de objetos escalable para almacenar y recuperar cualquier cantidad de datos en cualquier momento.

**Cómo lo usamos:**

- Almacena documentos legales crudos y procesados
- Almacena datos JSON extraídos del procesamiento de texto legal
- Proporciona un repositorio de datos centralizado accesible por todos los servicios

**Cuándo lo encontrarás:**

- En `terraform/modules/gcs/` - Módulo de Terraform que crea el bucket
- En `src/processing/` - Scripts que suben/descargan datos
- En workflows de pipeline de datos

**Conceptos básicos:**

- **Bucket**: Contenedor para almacenar objetos (como una carpeta)
- **Object**: Archivo individual almacenado en un bucket
- **Acceso uniforme a nivel de bucket**: Configuración de seguridad que usa IAM para todos los permisos

### Cloud Run (Service)

**Qué es:**
Una plataforma completamente gestionada para ejecutar aplicaciones en contenedores que escala automáticamente según las peticiones entrantes.

**Cómo lo usamos:**

- Hospeda la aplicación FastAPI
- Proporciona la API REST pública para consultas legales
- Escala automáticamente de 0 a múltiples instancias según el tráfico

**Cuándo lo encontrarás:**

- En `terraform/modules/cloud_run_service/` - Módulo de Terraform
- En `src/lus_laboris_api/` - El código de la aplicación
- En workflows de despliegue de API

**Conceptos básicos:**

- **Service**: Aplicación de larga duración que responde a peticiones HTTP
- **Revision**: Snapshot inmutable de una configuración de servicio
- **División de tráfico**: Enrutar porcentaje de tráfico a diferentes revisiones
- **Autoescalado**: Ajuste automático del número de instancias según la carga

### Cloud Run (Job/Batch)

**Qué es:**
Un servicio gestionado para ejecutar tareas en contenedores que se ejecutan hasta completarse y luego se detienen.

**Cómo lo usamos:**

- Extracción programada de texto legal de fuentes oficiales
- Se ejecuta en un horario cron (ej., diariamente a las 23:00)
- Procesa datos y sube resultados a Cloud Storage

**Cuándo lo encontrarás:**

- En `terraform/modules/cloud_run_job/` - Módulo de Terraform
- En `src/processing/` - El código de procesamiento batch
- En workflows de jobs programados

**Conceptos básicos:**

- **Job**: Tarea que se ejecuta hasta completarse (vs servicio que corre continuamente)
- **Execution**: Ejecución única de un job
- **Schedule**: Expresión cron que define cuándo se ejecuta el job
- **Cloud Scheduler**: Servicio que activa jobs según horario

### Compute Engine

**Qué es:**
Máquinas virtuales (VMs) ejecutándose en la infraestructura de Google, proporcionando control total sobre el entorno de computación.

**Cómo lo usamos:**

- Hospeda la base de datos vectorial Qdrant
- Proporciona almacenamiento persistente y cómputo para el vector store
- Configurado como instancia SPOT para optimización de costos

**Cuándo lo encontrarás:**

- En `terraform/modules/compute_engine/` - Módulo de Terraform
- En scripts de despliegue para Qdrant
- En operaciones de gestión de VM

**Conceptos básicos:**

- **Instance**: Una máquina virtual
- **Machine type**: Configuración de CPU y memoria (ej., e2-micro)
- **Zone**: Ubicación física donde se ejecuta la VM
- **Instancia SPOT**: VM interrumpible a menor costo
- **Reglas de firewall**: Reglas de seguridad de red que controlan el acceso

### Secret Manager

**Qué es:**
Un servicio seguro para almacenar, gestionar y acceder a información sensible como claves API, contraseñas y archivos de configuración.

**Cómo lo usamos:**

- Almacena el archivo de configuración `.env` completo
- Almacena la clave pública JWT para autenticación
- Proporciona secretos al servicio Cloud Run en tiempo de ejecución
- Los secretos se actualizan mediante workflows de GitHub Actions

**Cuándo lo encontrarás:**

- En `terraform/modules/secret_manager/` - Módulo de Terraform
- En workflows de despliegue que actualizan secretos
- En configuración de Cloud Run (montado como volúmenes)

**Conceptos básicos:**

- **Secret**: Contenedor nombrado para datos sensibles
- **Version**: Snapshot inmutable del contenido de un secreto
- **IAM binding**: Permiso que otorga acceso a un secreto
- **Rol secret accessor**: Permiso para leer valores de secretos
- **Rotación automática**: Capacidad de actualizar secretos sin redespliegue

### Cloud Scheduler

**Qué es:**
Un servicio de trabajos cron completamente gestionado para programar virtualmente cualquier tarea, incluyendo jobs batch, trabajos de big data y operaciones de infraestructura en la nube.

**Cómo lo usamos:**

- Activa Cloud Run Job según un horario
- Configurado para ejecutarse diariamente a las 23:00 (hora de Paraguay)
- Envía notificaciones al completar el job (éxito/error)

**Cuándo lo encontrarás:**

- En `terraform/modules/cloud_run_job/` - Creado junto con el job
- En monitoreo y logs de jobs
- En configuración de horarios

**Conceptos básicos:**

- **Schedule**: Expresión cron (ej., "0 23 ** *" = diario a las 23:00)
- **Time zone**: Zona horaria para interpretación del horario
- **HTTP target**: Endpoint a llamar cuando se activa el horario
- **Token OAuth**: Autenticación para llamar a Cloud Run

### Cloud Monitoring & Logging

**Qué es:**
Servicios para recolectar, analizar y visualizar métricas y logs de recursos de GCP.

**Cómo lo usamos:**

- Políticas de alerta para éxito/error de jobs
- Notificaciones por email cuando los jobs se completan
- Recolección de logs de todos los servicios
- Monitoreo de rendimiento

**Cuándo lo encontrarás:**

- En `terraform/modules/cloud_run_job/` - Configuraciones de alertas
- En logs de aplicación
- Al hacer troubleshooting de problemas

**Conceptos básicos:**

- **Log**: Registro de eventos de una aplicación o servicio
- **Metric**: Medición numérica del comportamiento del sistema
- **Alert policy**: Regla que activa notificación cuando se cumplen condiciones
- **Notification channel**: Destino para alertas (ej., email)

## Cómo Funcionan Estos Recursos Juntos

```text
┌─────────────────────────────────────────────────────────┐
│              Cloud Scheduler (Cron)                      │
│  Se activa diariamente a las 23:00                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Cloud Run Job (Procesamiento Batch)             │
│  Extrae texto legal, procesa datos                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Cloud Storage (Bucket GCS)                     │
│  Almacena documentos legales procesados                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│      Compute Engine VM (Base de Datos Qdrant)          │
│  Indexa documentos para búsqueda semántica              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Cloud Run Service (API FastAPI)                 │
│  ├── Lee configuración de Secret Manager               │
│  ├── Consulta Qdrant para búsqueda semántica           │
│  └── Retorna respuestas legales potenciadas por IA     │
└─────────────────────────────────────────────────────────┘
```

## Optimización de Costos

La infraestructura está configurada para eficiencia de costos:

- **Cloud Run Service**: Escala a 0 cuando no se usa (paga solo por peticiones)
- **Cloud Run Job**: Solo se ejecuta cuando está programado (no continuamente)
- **Compute Engine**: Instancia SPOT (hasta 91% más barata que VMs regulares)
- **Cloud Storage**: Clase de almacenamiento estándar con gestión de ciclo de vida
- **Secret Manager**: Costo mínimo (secretos son pequeños)

## Seguridad

Cada recurso implementa mejores prácticas de seguridad:

- **Roles IAM**: Principio de menor privilegio
- **Secret Manager**: Encriptado en reposo, acceso controlado
- **Reglas de firewall**: Solo puertos necesarios abiertos
- **Cuentas de servicio**: Cuentas separadas para cada servicio
- **Solo HTTPS**: Toda comunicación externa encriptada

## Aprender Más

- [Documentación de Google Cloud](https://cloud.google.com/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Documentación de Cloud Run](https://cloud.google.com/run/docs)
- [Documentación de Secret Manager](https://cloud.google.com/secret-manager/docs)
