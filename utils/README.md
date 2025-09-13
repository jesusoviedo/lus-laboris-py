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
| `setup_gcp_project.sh` | GCP Project Setup Script | Automated setup of GCP project with APIs, service accounts, and permissions |

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

## GCP Project Setup Script

The `setup_gcp_project.sh` script automates the complete setup of a Google Cloud Platform project with all necessary APIs, service accounts, and permissions for the Py Labor Law RAG project.

### Features

- **Interactive Menu**: Step-by-step setup with individual options
- **Full Automation**: Complete setup in one command
- **Validation**: Comprehensive verification of each step
- **Error Handling**: Robust error checking and rollback capabilities
- **Colorized Output**: Clear visual feedback for different types of messages
- **Configuration Management**: Persistent settings throughout the session

### Prerequisites

1. **Google Cloud CLI**: Must be installed and configured
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Authenticate
   gcloud auth login
   ```

2. **Permissions**: Your Google account must have permission to create projects and manage IAM

### Usage

#### Basic Usage

```bash
# Navigate to the utils directory
cd utils/

# Run the script
./setup_gcp_project.sh
```

#### Menu Options

The script provides an interactive menu with the following options:

1. **Create Project** - Creates a new GCP project
2. **Enable APIs** - Enables all required APIs
3. **Create Service Account** - Creates the service account
4. **Assign Roles** - Assigns all necessary IAM roles
5. **Generate JSON Key** - Generates and downloads the JSON key
6. **Verify Setup** - Verifies the complete setup
7. **Full Setup** - Executes all steps in sequence
8. **Show Configuration** - Displays current settings
9. **Exit** - Exits the script

#### Full Automated Setup

For a completely automated setup, select option **7** and the script will:

1. Create the GCP project
2. Enable all required APIs
3. Create the service account
4. Assign all necessary roles
5. Generate the JSON key
6. Verify the complete setup

### Configuration

#### Default Values

The script uses the following default values:

- **Project Name**: `Py Labor Law RAG`
- **Project ID**: `py-labor-law-rag`
- **Region**: `southamerica-east1`
- **Zone**: `southamerica-east1-a`
- **Service Account Name**: `lus-laboris-py-service-account`
- **Display Name**: `Lus Laboris Py Service Account`
- **Description**: `Service account for Py Labor Law RAG project`

#### Customization

You can customize any of these values when prompted by the script. The script will remember your choices throughout the session.

### APIs Enabled

The script enables the following Google Cloud APIs:

- `storage.googleapis.com` - Cloud Storage
- `cloudresourcemanager.googleapis.com` - Resource Manager
- `compute.googleapis.com` - Compute Engine
- `run.googleapis.com` - Cloud Run
- `cloudscheduler.googleapis.com` - Cloud Scheduler
- `iam.googleapis.com` - Identity and Access Management
- `logging.googleapis.com` - Cloud Logging
- `monitoring.googleapis.com` - Cloud Monitoring

### IAM Roles Assigned

The service account is assigned the following roles:

- `roles/storage.admin` - Storage Admin
- `roles/storage.objectAdmin` - Storage Object Admin
- `roles/run.admin` - Cloud Run Admin
- `roles/iam.serviceAccountUser` - Service Account User
- `roles/cloudscheduler.admin` - Cloud Scheduler Admin
- `roles/compute.instanceAdmin` - Compute Instance Admin
- `roles/compute.networkAdmin` - Compute Network Admin

### Output Files

The script creates the following files:

- `.gcpcredentials/lus-laboris-py-service-account.json` - Service account JSON key
- The JSON key file is automatically set with proper permissions (600)

### Verification

The verification step checks:

1. **Project Exists**: Confirms the project was created
2. **Service Account Exists**: Confirms the service account was created
3. **Roles Assigned**: Lists all assigned roles
4. **Authentication**: Tests the JSON key authentication
5. **File Permissions**: Ensures proper security on the key file

### Error Handling

The script includes comprehensive error handling:

- **Pre-flight Checks**: Verifies gcloud CLI and authentication
- **Command Validation**: Checks if each gcloud command succeeds
- **Rollback Support**: Can be re-run to fix partial failures
- **Clear Error Messages**: Descriptive error messages with suggested fixes

### Security Features

- **Secure File Permissions**: JSON key file is set to 600 (owner read/write only)
- **Validation**: Input validation for project IDs and other parameters
- **Authentication Testing**: Verifies the generated key works correctly
- **No Hardcoded Secrets**: All sensitive information is handled securely

### Troubleshooting

#### Common Issues

1. **"gcloud command not found"**
   - Install the Google Cloud CLI
   - Ensure it's in your PATH

2. **"Authentication required"**
   - Run `gcloud auth login`
   - Ensure you have the necessary permissions

3. **"Project already exists"**
   - The script will use the existing project
   - Or choose a different project ID

4. **"Permission denied"**
   - Ensure your account has Project Creator and IAM Admin permissions
   - Check your organization's policies

#### Getting Help

If you encounter issues:

1. Check the error messages - they often contain helpful hints
2. Verify your Google Cloud CLI is up to date: `gcloud components update`
3. Check your authentication: `gcloud auth list`
4. Verify your permissions in the Google Cloud Console

### Integration with Project

After running this script, you can:

1. **Use with Terraform**: The generated JSON key works with Terraform
2. **GitHub Actions**: Upload the JSON key as a repository secret
3. **Local Development**: Use the key for local gcloud authentication
4. **CI/CD Pipelines**: Reference the key in your deployment scripts

### Next Steps

After completing the setup:

1. **Update your .env file** with the project ID
2. **Configure Terraform** to use the new project
3. **Set up GitHub Actions secrets** with the JSON key
4. **Run Terraform** to create your infrastructure
5. **Deploy your applications** using the configured resources

---

**Note**: This script follows the exact same steps documented in `docs/setup_gcp_project.md` but automates them for convenience and reduces the chance of human error.

---

## Descripción

Esta carpeta contiene scripts de utilidad y herramientas para el proyecto lus-laboris-py. Estos scripts ayudan a automatizar tareas comunes y proporcionan interfaces convenientes para la gestión del proyecto.

### Scripts Disponibles

| Script | Descripción | Propósito |
|--------|-------------|-----------|
| `gcp_utils.py` | Utilidades de Google Cloud Platform | Crear, listar y gestionar buckets GCS para el estado de Terraform |
| `setup_gcp_project.sh` | Script de Configuración de Proyecto GCP | Configuración automatizada de proyecto GCP con APIs, cuentas de servicio y permisos |

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

## Script de Configuración de Proyecto GCP

El script `setup_gcp_project.sh` automatiza la configuración completa de un proyecto de Google Cloud Platform con todas las APIs necesarias, cuentas de servicio y permisos para el proyecto Py Labor Law RAG.

### Características

- **Menú Interactivo**: Configuración paso a paso con opciones individuales
- **Automatización Completa**: Configuración completa en un comando
- **Validación**: Verificación integral de cada paso
- **Manejo de Errores**: Verificación robusta de errores y capacidades de rollback
- **Salida Colorizada**: Retroalimentación visual clara para diferentes tipos de mensajes
- **Gestión de Configuración**: Configuraciones persistentes durante la sesión

### Prerrequisitos

1. **Google Cloud CLI**: Debe estar instalado y configurado
   ```bash
   # Instalar gcloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Autenticar
   gcloud auth login
   ```

2. **Permisos**: Tu cuenta de Google debe tener permisos para crear proyectos y gestionar IAM

### Uso

#### Uso Básico

```bash
# Navegar al directorio utils
cd utils/

# Ejecutar el script
./setup_gcp_project.sh
```

#### Opciones del Menú

El script proporciona un menú interactivo con las siguientes opciones:

1. **Crear Proyecto** - Crea un nuevo proyecto GCP
2. **Habilitar APIs** - Habilita todas las APIs requeridas
3. **Crear Cuenta de Servicio** - Crea la cuenta de servicio
4. **Asignar Roles** - Asigna todos los roles IAM necesarios
5. **Generar Clave JSON** - Genera y descarga la clave JSON
6. **Verificar Configuración** - Verifica la configuración completa
7. **Configuración Completa** - Ejecuta todos los pasos en secuencia
8. **Mostrar Configuración** - Muestra la configuración actual
9. **Salir** - Sale del script

#### Configuración Automatizada Completa

Para una configuración completamente automatizada, selecciona la opción **7** y el script:

1. Creará el proyecto GCP
2. Habilitará todas las APIs requeridas
3. Creará la cuenta de servicio
4. Asignará todos los roles necesarios
5. Generará la clave JSON
6. Verificará la configuración completa

### Configuración

#### Valores por Defecto

El script utiliza los siguientes valores por defecto:

- **Nombre del Proyecto**: `Py Labor Law RAG`
- **ID del Proyecto**: `py-labor-law-rag`
- **Región**: `southamerica-east1`
- **Zona**: `southamerica-east1-a`
- **Nombre de Cuenta de Servicio**: `lus-laboris-py-service-account`
- **Nombre para Mostrar**: `Lus Laboris Py Service Account`
- **Descripción**: `Service account for Py Labor Law RAG project`

#### Personalización

Puedes personalizar cualquiera de estos valores cuando el script te lo solicite. El script recordará tus elecciones durante la sesión.

### APIs Habilitadas

El script habilita las siguientes APIs de Google Cloud:

- `storage.googleapis.com` - Cloud Storage
- `cloudresourcemanager.googleapis.com` - Resource Manager
- `compute.googleapis.com` - Compute Engine
- `run.googleapis.com` - Cloud Run
- `cloudscheduler.googleapis.com` - Cloud Scheduler
- `iam.googleapis.com` - Identity and Access Management
- `logging.googleapis.com` - Cloud Logging
- `monitoring.googleapis.com` - Cloud Monitoring

### Roles IAM Asignados

La cuenta de servicio recibe los siguientes roles:

- `roles/storage.admin` - Administrador de Storage
- `roles/storage.objectAdmin` - Administrador de Objetos de Storage
- `roles/run.admin` - Administrador de Cloud Run
- `roles/iam.serviceAccountUser` - Usuario de Cuenta de Servicio
- `roles/cloudscheduler.admin` - Administrador de Cloud Scheduler
- `roles/compute.instanceAdmin` - Administrador de Instancias de Compute
- `roles/compute.networkAdmin` - Administrador de Red de Compute

### Archivos de Salida

El script crea los siguientes archivos:

- `.gcpcredentials/lus-laboris-py-service-account.json` - Clave JSON de la cuenta de servicio
- El archivo de clave JSON se configura automáticamente con permisos apropiados (600)

### Verificación

El paso de verificación comprueba:

1. **El Proyecto Existe**: Confirma que el proyecto fue creado
2. **La Cuenta de Servicio Existe**: Confirma que la cuenta de servicio fue creada
3. **Roles Asignados**: Lista todos los roles asignados
4. **Autenticación**: Prueba la autenticación con la clave JSON
5. **Permisos de Archivo**: Asegura la seguridad apropiada en el archivo de clave

### Manejo de Errores

El script incluye manejo integral de errores:

- **Verificaciones Previas**: Verifica gcloud CLI y autenticación
- **Validación de Comandos**: Comprueba si cada comando gcloud tiene éxito
- **Soporte de Rollback**: Puede ejecutarse nuevamente para corregir fallos parciales
- **Mensajes de Error Claros**: Mensajes de error descriptivos con sugerencias de corrección

### Características de Seguridad

- **Permisos Seguros de Archivo**: El archivo de clave JSON se configura en 600 (solo lectura/escritura del propietario)
- **Validación**: Validación de entrada para IDs de proyecto y otros parámetros
- **Prueba de Autenticación**: Verifica que la clave generada funcione correctamente
- **Sin Secretos Codificados**: Toda la información sensible se maneja de forma segura

### Solución de Problemas

#### Problemas Comunes

1. **"comando gcloud no encontrado"**
   - Instala Google Cloud CLI
   - Asegúrate de que esté en tu PATH

2. **"Autenticación requerida"**
   - Ejecuta `gcloud auth login`
   - Asegúrate de tener los permisos necesarios

3. **"El proyecto ya existe"**
   - El script usará el proyecto existente
   - O elige un ID de proyecto diferente

4. **"Permiso denegado"**
   - Asegúrate de que tu cuenta tenga permisos de Creador de Proyecto y Administrador IAM
   - Verifica las políticas de tu organización

#### Obtener Ayuda

Si encuentras problemas:

1. Revisa los mensajes de error - a menudo contienen pistas útiles
2. Verifica que tu Google Cloud CLI esté actualizado: `gcloud components update`
3. Verifica tu autenticación: `gcloud auth list`
4. Verifica tus permisos en la Consola de Google Cloud

### Integración con el Proyecto

Después de ejecutar este script, puedes:

1. **Usar con Terraform**: La clave JSON generada funciona con Terraform
2. **GitHub Actions**: Subir la clave JSON como secret del repositorio
3. **Desarrollo Local**: Usar la clave para autenticación local de gcloud
4. **Pipelines CI/CD**: Referenciar la clave en tus scripts de despliegue

### Próximos Pasos

Después de completar la configuración:

1. **Actualiza tu archivo .env** con el ID del proyecto
2. **Configura Terraform** para usar el nuevo proyecto
3. **Configura secrets de GitHub Actions** con la clave JSON
4. **Ejecuta Terraform** para crear tu infraestructura
5. **Despliega tus aplicaciones** usando los recursos configurados

---

**Nota**: Este script sigue exactamente los mismos pasos documentados en `docs/setup_gcp_project.md` pero los automatiza para conveniencia y reduce la posibilidad de error humano.