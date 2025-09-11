# Infrastructure with Terraform

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#what-is-terraform) | [🇪🇸 Español](#qué-es-terraform)

</div>

---

## What is Terraform?

Terraform is an Infrastructure as Code (IaC) tool developed by HashiCorp that allows you to define, plan, and create infrastructure resources declaratively. With Terraform, you can manage infrastructure across multiple cloud providers (like Google Cloud Platform, AWS, Azure) using configuration files in HCL (HashiCorp Configuration Language) format.

## Folder Structure

```
project-root/
├── .env                      # Environment variables for Terraform and tf_menu.sh
├── terraform/
│   ├── main.tf               # Main file defining the modules to use
│   ├── variables.tf          # Input variables definition
│   ├── providers.tf          # Provider configuration (Google Cloud)
│   ├── terraform.tfvars      # Specific values for variables
│   ├── tf_menu.sh            # Interactive menu script for Terraform
│   └── modules/              # Reusable modules
│       └── gcs/              # Google Cloud Storage module
│           ├── main.tf       # GCS bucket resources
│           ├── variables.tf  # Module-specific variables
│           └── outputs.tf    # Module output values
└── ...
```

### Purpose of each file:

- **`.env`**: Stores required environment variables (`GCP_PROJECT_ID`, `GCP_REGION`, `GCP_BUCKET_NAME`) for Terraform and the interactive script.
- **`main.tf`**: Defines main modules and their configurations
- **`variables.tf`**: Declares customizable variables
- **`providers.tf`**: Configures Google Cloud Platform provider with JSON credentials
- **`terraform.tfvars`**: Contains specific values for variables
- **`tf_menu.sh`**: Interactive menu script for common Terraform operations
- **`modules/gcs/`**: Reusable module for creating Google Cloud Storage buckets

## Steps to Implement Infrastructure

### Prerequisites

1. **Terraform installed** (version 1.0 or higher)
2. **Google Cloud Platform account** configured
3. **GCP service account JSON credentials file**
4. **Configuration details**: Check the `docs/setup_gcp_project.md` file for detailed steps on service account creation and required permissions.

### Step 0: Create and Configure the .env File

At the root of the project, create a file named `.env` with the following variables:

```env
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=your-region
GCP_BUCKET_NAME=your-bucket-name
```

These variables are required for the interactive script and for generating the `terraform.tfvars` file automatically.

### Step 1: Create Terraform State Bucket

Before running Terraform commands, you need to create a bucket to store the Terraform state:

```bash
# Navigate to utils directory
cd ../utils

# Create the Terraform state bucket
uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state

# Return to terraform directory
cd ../terraform
```

This bucket will be used to store the Terraform state file remotely, enabling team collaboration and state management.

### Step 2: Configure Environment Variables

Set the Google Cloud credentials environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="../.gcpcredentials/lus-laboris-py-service-account.json"
```

**Important**: This environment variable must be set before running any Terraform commands.

### Step 3: Initialize Terraform
```bash
terraform init
```
This command downloads necessary providers and initializes the working directory.

### Step 4: Validate Configuration
```bash
terraform validate
```
Verifies that the configuration files syntax is correct.

### Step 5: Plan and Apply Changes
```bash
# Plan changes
terraform plan
```
Shows an execution plan of resources that will be created, modified, or destroyed.

```bash
# Apply changes
terraform apply
```
Executes the plan and creates/modifies infrastructure according to the configuration.

### Additional Commands

#### View current state
```bash
terraform show
```
Shows the current state of deployed infrastructure.

#### Destroy infrastructure
```bash
terraform destroy
```
⚠️ **WARNING**: This command removes all resources created by Terraform.

### Variable Configuration

Before running `terraform apply`, make sure to configure variables in `terraform.tfvars`:

```hcl
project_id  = "your-gcp-project"
region      = "southamerica-east1"
bucket_name = "your-bucket-name"
```

**Note**: The Terraform state bucket (`py-labor-law-rag-terraform-state`) is hardcoded in `providers.tf` and should match the bucket created in Step 1 using the `gcp_utils.py` script.

### Credentials Configuration

This project uses a service account JSON credentials file. The file should be located at:

```
.gcpcredentials/lus-laboris-py-service-account.json
```

**Important**: Make sure the JSON credentials file has the necessary permissions to create and manage Google Cloud Storage resources.

## Created Resources

This Terraform project creates:

- **Google Cloud Storage Bucket**: A bucket for storing files with uniform bucket-level access
- **Regional configuration**: The bucket is created in the region specified in `terraform.tfvars`

## Important Notes

- The `terraform.tfstate` file contains the infrastructure state and **should NOT be deleted**
- `.tfvars` files may contain sensitive information, make sure not to commit them to version control
- Always review the plan before applying changes with `terraform plan`

## Easy Terraform Menu Script

For users who do not want to manually set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable, you can use the provided interactive script:

```bash
bash ./tf_menu.sh
```

This script will:
- Automatically search for a `.json` credentials file in the `.gcpcredentials` folder at the project root (two levels up).
- Export the `GOOGLE_APPLICATION_CREDENTIALS` variable if not already set.
- Read the `.env` file at the project root, extract the variables `GCP_PROJECT_ID`, `GCP_REGION`, and `GCP_BUCKET_NAME`, and generate the `terraform.tfvars` file automatically.
- Provide a menu for common Terraform operations: `init`, `plan`, `apply`, `destroy`.

**Note:** You must run this script from the `terraform` directory. The `.env` file must exist at the project root.

---

## ¿Qué es Terraform?

Terraform es una herramienta de infraestructura como código (IaC) desarrollada por HashiCorp que permite definir, planificar y crear recursos de infraestructura de manera declarativa. Con Terraform, puedes gestionar infraestructura en múltiples proveedores de nube (como Google Cloud Platform, AWS, Azure) usando archivos de configuración en formato HCL (HashiCorp Configuration Language).

## Estructura de Carpetas

```
raiz-del-proyecto/
├── .env                      # Variables de entorno para Terraform y tf_menu.sh
├── terraform/
│   ├── main.tf               # Archivo principal que define los módulos a usar
│   ├── variables.tf          # Definición de variables de entrada
│   ├── providers.tf          # Configuración de proveedores (Google Cloud)
│   ├── terraform.tfvars      # Valores específicos de las variables 
│   ├── tf_menu.sh            # Script de menú interactivo para Terraform
│   └── modules/              # Módulos reutilizables
│       └── gcs/              # Módulo para Google Cloud Storage
│           ├── main.tf       # Recursos del bucket de GCS
│           ├── variables.tf  # Variables específicas del módulo
│           └── outputs.tf    # Valores de salida del módulo
└── ...
```

### Propósito de cada archivo:

- **`.env`**: Almacena las variables de entorno requeridas (`GCP_PROJECT_ID`, `GCP_REGION`, `GCP_BUCKET_NAME`) para Terraform y el script interactivo.
- **`main.tf`**: Define los módulos principales y sus configuraciones
- **`variables.tf`**: Declara las variables que se pueden personalizar
- **`providers.tf`**: Configura el proveedor de Google Cloud Platform con credenciales JSON
- **`terraform.tfvars`**: Contiene los valores específicos para las variables 
- **`tf_menu.sh`**: Script de menú interactivo para operaciones comunes de Terraform
- **`modules/gcs/`**: Módulo reutilizable para crear buckets de Google Cloud Storage

## Pasos para Implementar la Infraestructura

### Prerrequisitos

1. **Terraform instalado** (versión 1.0 o superior)
2. **Cuenta de Google Cloud Platform** configurada
3. **Archivo de credenciales JSON** de cuenta de servicio de GCP
4. **Detalles de configuración**: Consulta el archivo `docs/setup_gcp_project.md` para los pasos detallados de creación de cuenta de servicio y permisos necesarios.

### Paso 0: Crear y Configurar el archivo .env

En la raíz del proyecto, crea un archivo llamado `.env` con las siguientes variables:

```env
GCP_PROJECT_ID=tu-proyecto-gcp
GCP_REGION=tu-region
GCP_BUCKET_NAME=nombre-de-tu-bucket
```

Estas variables son requeridas por el script interactivo y para la generación automática del archivo `terraform.tfvars`.

### Paso 1: Crear Bucket para Estado de Terraform

Antes de ejecutar comandos de Terraform, necesitas crear un bucket para almacenar el estado de Terraform:

```bash
# Navegar al directorio utils
cd ../utils

# Crear el bucket para el estado de Terraform
uv run gcp_utils.py gcs-create py-labor-law-rag-terraform-state

# Regresar al directorio terraform
cd ../terraform
```

Este bucket se utilizará para almacenar el archivo de estado de Terraform de forma remota, permitiendo colaboración en equipo y gestión del estado.

### Paso 2: Configurar Variables de Entorno

Configura la variable de entorno de credenciales de Google Cloud:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="../.gcpcredentials/lus-laboris-py-service-account.json"
```

**Importante**: Esta variable de entorno debe configurarse antes de ejecutar cualquier comando de Terraform.

### Paso 3: Inicializar Terraform
```bash
terraform init
```
Este comando descarga los proveedores necesarios e inicializa el directorio de trabajo.

### Paso 4: Validar la Configuración
```bash
terraform validate
```
Verifica que la sintaxis de los archivos de configuración sea correcta.

### Paso 5: Planificar y Aplicar Cambios
```bash
# Planificar los cambios
terraform plan
```
Muestra un plan de ejecución de los recursos que se van a crear, modificar o eliminar.

```bash
# Aplicar los cambios
terraform apply
```
Ejecuta el plan y crea/modifica la infraestructura según la configuración.

### Comandos Adicionales

#### Ver el estado actual
```bash
terraform show
```
Muestra el estado actual de la infraestructura desplegada.

#### Destruir la infraestructura
```bash
terraform destroy
```
⚠️ **CUIDADO**: Este comando elimina todos los recursos creados por Terraform.

### Configuración de Variables

Antes de ejecutar `terraform apply`, asegúrate de configurar las variables en `terraform.tfvars`:

```hcl
project_id  = "tu-proyecto-gcp"
region      = "southamerica-east1"
bucket_name = "nombre-de-tu-bucket"
```

**Nota**: El bucket de estado de Terraform (`py-labor-law-rag-terraform-state`) está hardcodeado en `providers.tf` y debe coincidir con el bucket creado en el Paso 1 usando el script `gcp_utils.py`.

### Configuración de Credenciales

Este proyecto utiliza un archivo JSON de credenciales de cuenta de servicio. El archivo debe estar ubicado en:

```
.gcpcredentials/lus-laboris-py-service-account.json
```

**Importante**: Asegúrate de que el archivo de credenciales JSON tenga los permisos necesarios para crear y gestionar recursos de Google Cloud Storage.

## Recursos Creados

Este proyecto de Terraform crea:

- **Google Cloud Storage Bucket**: Un bucket para almacenar archivos con acceso uniforme a nivel de bucket
- **Configuración regional**: El bucket se crea en la región especificada en `terraform.tfvars`

## Notas Importantes

- El archivo `terraform.tfstate` contiene el estado de la infraestructura y **NO debe ser eliminado**
- Los archivos `.tfvars` pueden contener información sensible, asegúrate de no subirlos al control de versiones
- Siempre revisa el plan antes de aplicar cambios con `terraform plan`

## Script de menú fácil para Terraform

Para quienes no pueden o no quieren setear manualmente la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`, puedes usar el script interactivo incluido:

```bash
bash ./tf_menu.sh
```

Este script:
- Busca automáticamente un archivo `.json` de credenciales en la carpeta `.gcpcredentials` en la raíz del proyecto (dos niveles arriba).
- Exporta la variable `GOOGLE_APPLICATION_CREDENTIALS` si no está seteada.
- Lee el archivo `.env` en la raíz del proyecto, extrae las variables `GCP_PROJECT_ID`, `GCP_REGION` y `GCP_BUCKET_NAME`, y genera automáticamente el archivo `terraform.tfvars`.
- Ofrece un menú para las operaciones comunes de Terraform: `init`, `plan`, `apply`, `destroy`.

**Nota:** Debes ejecutar este script desde el directorio `terraform`. El archivo `.env` debe existir en la raíz del proyecto.

---