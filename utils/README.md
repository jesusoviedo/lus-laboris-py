# Utils

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#description) | [🇪🇸 Español](#descripción)

</div>

---

## Description

This folder contains utility scripts and tools for the lus-laboris-py project. These scripts help automate common tasks and provide convenient interfaces for project management.

### Available Scripts

| Script | Description | Purpose |
|--------|-------------|---------|
| `gcp_utils.py` | Google Cloud Platform utilities | Create, list, and manage GCS buckets for Terraform state |

## GCP Utilities

The `gcp_utils.py` script provides utilities for managing Google Cloud Storage buckets, specifically designed for Terraform state management.

### Features

- **Automatic Credentials Setup**: Automatically searches for JSON credential files in `.gcpcredentials/` folder
- **Bucket Creation**: Create GCS buckets with proper configuration for Terraform state
- **Bucket Listing**: List all buckets in your GCP project
- **Bucket Deletion**: Safely delete empty buckets
- **Versioning**: Automatically enables versioning for Terraform state buckets
- **Error Handling**: Comprehensive error handling and user feedback

### Installation

1. Install dependencies:
```bash
cd utils
uv sync
```

2. Set up GCP credentials (see [GCP Setup Guide](../docs/setup_gcp_project.md))

### Running the Script

The script should be executed using `uv run` to ensure all dependencies are available:

```bash
# Recommended: Use uv run
uv run gcp_utils.py [command] [options]
```

**Why use `uv run`?**
- Ensures the correct Python environment with all required dependencies
- Uses the project's `pyproject.toml` configuration
- Avoids conflicts with system Python packages

### Usage

#### Create a Bucket for Terraform State

```bash
# Basic usage
uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state

# With custom location
uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state --location us-central1

# With specific project
uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state --project-id your-project-id
```

#### List All Buckets

```bash
uv run gcp_utils.py gcs-list
```

#### Delete a Bucket (Use with Caution)

```bash
uv run gcp_utils.py gcs-delete py-labor-law-rag-terraform-state
```

### Configuration

The script uses the following default settings:
- **Location**: `southamerica-east1` (Paraguay region)
- **Versioning**: Enabled automatically for Terraform state buckets
- **Credentials**: Automatically searches for JSON files in `.gcpcredentials/` folder

#### Automatic Credentials Setup

The script automatically searches for GCP credential files in the following locations:
1. `.gcpcredentials/` (current directory)
2. `../.gcpcredentials/` (parent directory)
3. `../../.gcpcredentials/` (grandparent directory)

If multiple JSON files are found, it prioritizes files with "service-account" in the filename.

### Error Handling

The script provides clear error messages and suggestions for common issues:
- Missing credentials
- Missing project ID (400 POST error)
- Bucket already exists
- Permission errors
- Network connectivity issues

#### Common Error: "Required parameter: project"

If you get this error, the script cannot determine your GCP project ID from the credentials file. Solutions:

1. **Specify project ID explicitly**:
   ```bash
   uv run gcp_utils.py gcs-create my-bucket --project-id your-project-id
   ```

2. **Verify credentials file contains project_id**:
   Check that your JSON credentials file includes the `project_id` field. The script automatically reads the project ID from the credentials file specified in `GOOGLE_APPLICATION_CREDENTIALS`.

---

## Descripción

Esta carpeta contiene scripts de utilidad y herramientas para el proyecto lus-laboris-py. Estos scripts ayudan a automatizar tareas comunes y proporcionan interfaces convenientes para la gestión del proyecto.

### Scripts Disponibles

| Script | Descripción | Propósito |
|--------|-------------|-----------|
| `gcp_utils.py` | Utilidades de Google Cloud Platform | Crear, listar y gestionar buckets GCS para el estado de Terraform |

## Utilidades GCP

El script `gcp_utils.py` proporciona utilidades para gestionar buckets de Google Cloud Storage, específicamente diseñado para la gestión del estado de Terraform.

### Características

- **Configuración Automática de Credenciales**: Busca automáticamente archivos JSON de credenciales en la carpeta `.gcpcredentials/`
- **Creación de Buckets**: Crear buckets GCS con configuración adecuada para el estado de Terraform
- **Listado de Buckets**: Listar todos los buckets en tu proyecto GCP
- **Eliminación de Buckets**: Eliminar buckets vacíos de forma segura
- **Versionado**: Habilita automáticamente el versionado para buckets de estado de Terraform
- **Manejo de Errores**: Manejo integral de errores y retroalimentación al usuario

### Instalación

1. Instalar dependencias:
```bash
cd utils
uv sync
```

2. Configurar credenciales GCP (ver [Guía de Configuración GCP](../docs/setup_gcp_project.md))

### Ejecutar el Script

El script debe ejecutarse usando `uv run` para asegurar que todas las dependencias estén disponibles:

```bash
# Recomendado: Usar uv run
uv run gcp_utils.py [comando] [opciones]
```

**¿Por qué usar `uv run`?**
- Asegura el entorno Python correcto con todas las dependencias requeridas
- Usa la configuración del `pyproject.toml` del proyecto
- Evita conflictos con paquetes Python del sistema

### Uso

#### Crear un Bucket para el Estado de Terraform

```bash
# Uso básico
uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state

# Con ubicación personalizada
uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state --location us-central1

# Con proyecto específico
uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state --project-id tu-project-id
```

#### Listar Todos los Buckets

```bash
uv run gcp_utils.py gcs-list
```

#### Eliminar un Bucket (Usar con Precaución)

```bash
uv run gcp_utils.py gcs-delete py-labor-law-rag-terraform-state
```

### Configuración

El script utiliza las siguientes configuraciones por defecto:
- **Ubicación**: `southamerica-east1` (región de Paraguay)
- **Versionado**: Habilitado automáticamente para buckets de estado de Terraform
- **Credenciales**: Busca automáticamente archivos JSON en la carpeta `.gcpcredentials/`

#### Configuración Automática de Credenciales

El script busca automáticamente archivos de credenciales GCP en las siguientes ubicaciones:
1. `.gcpcredentials/` (directorio actual)
2. `../.gcpcredentials/` (directorio padre)
3. `../../.gcpcredentials/` (directorio abuelo)

Si se encuentran múltiples archivos JSON, prioriza los archivos que contengan "service-account" en el nombre.

### Manejo de Errores

El script proporciona mensajes de error claros y sugerencias para problemas comunes:
- Credenciales faltantes
- ID de proyecto faltante (error 400 POST)
- Bucket ya existe
- Errores de permisos
- Problemas de conectividad de red

#### Error Común: "Required parameter: project"

Si obtienes este error, el script no puede determinar tu ID de proyecto GCP desde el archivo de credenciales. Soluciones:

1. **Especificar ID de proyecto explícitamente**:
   ```bash
   uv run gcp_utils.py gcs-create my-bucket --project-id tu-project-id
   ```

2. **Verificar que el archivo de credenciales contenga project_id**:
   Verifica que tu archivo JSON de credenciales incluya el campo `project_id`. El script lee automáticamente el ID del proyecto desde el archivo de credenciales especificado en `GOOGLE_APPLICATION_CREDENTIALS`.
