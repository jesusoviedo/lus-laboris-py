# Google Cloud Platform Project Setup

This guide will help you set up a Google Cloud Platform project with a service account that has the necessary permissions to manage Google Cloud Storage resources.

## Prerequisites

- Active Google Cloud Platform account
- Access to Google Cloud Console
- Google Cloud CLI installed (optional, but recommended)

## Step 1: Create a Project in GCP

### Using Google Cloud Console

1. **Access Google Cloud Console**
   - Go to [console.cloud.google.com](https://console.cloud.google.com)
   - Sign in with your Google account

2. **Create a new project**
   - Click on the project selector at the top
   - Select "New project"
   - Enter a name for the project (e.g., `py-labor-law-rag`)
   - Note the **Project ID** generated automatically
   - Click "Create"

3. **Select the project**
   - Make sure the newly created project is selected

### Using Google Cloud CLI

```bash
# Create a new project
gcloud projects create py-labor-law-rag --name="Py Labor Law RAG"

# Set the project as active
gcloud config set project py-labor-law-rag
```

## Step 2: Enable Required APIs

### Using Google Cloud Console

1. **Enable Google Cloud Storage API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google Cloud Storage API"
   - Click "Enable"

2. **Enable Cloud Resource Manager API**
   - Search for "Cloud Resource Manager API"
   - Click "Enable"

### Using Google Cloud CLI

```bash
# Enable required APIs
gcloud services enable storage.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

## Step 3: Create a Service Account

### Using Google Cloud Console

1. **Navigate to IAM & Admin**
   - Go to "IAM & Admin" > "Service Accounts"

2. **Create service account**
   - Click "Create Service Account"
   - Enter the following data:
     - **Name**: `lus-laboris-py-service-account`
     - **ID**: `lus-laboris-py-service-account` (generated automatically)
     - **Description**: `Service account for Py Labor Law RAG project`
   - Click "Create and Continue"

3. **Assign roles**
   - In the "Grant this service account access to project" section, add the following roles:
     - **Storage Admin** (`roles/storage.admin`)
     - **Storage Object Admin** (`roles/storage.objectAdmin`)
   - Click "Continue" and then "Done"

### Using Google Cloud CLI

```bash
# Create the service account
gcloud iam service-accounts create lus-laboris-py-service-account \
    --display-name="Lus Laboris Py Service Account" \
    --description="Service account for Py Labor Law RAG project"

# Assign Storage Admin role
gcloud projects add-iam-policy-binding py-labor-law-rag \
    --member="serviceAccount:lus-laboris-py-service-account@py-labor-law-rag.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Assign Storage Object Admin role
gcloud projects add-iam-policy-binding py-labor-law-rag \
    --member="serviceAccount:lus-laboris-py-service-account@py-labor-law-rag.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

## Step 4: Generate JSON Key

### Using Google Cloud Console

1. **Access the service account**
   - Go to "IAM & Admin" > "Service Accounts"
   - Find your service account `lus-laboris-py-service-account`
   - Click on the service account email

2. **Create JSON key**
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select "JSON" as key type
   - Click "Create"
   - The JSON file will download automatically

3. **Save the file**
   - Rename the downloaded file to `lus-laboris-py-service-account.json`
   - Place it in the `.gcpcredentials/` folder of the project

### Using Google Cloud CLI

```bash
# Create directory for credentials
mkdir -p .gcpcredentials

# Generate and download JSON key
gcloud iam service-accounts keys create .gcpcredentials/lus-laboris-py-service-account.json \
    --iam-account=lus-laboris-py-service-account@py-labor-law-rag.iam.gserviceaccount.com
```

## Step 5: Verify Configuration

### Verify with Google Cloud CLI

```bash
# Verify the service account has the correct roles
gcloud projects get-iam-policy py-labor-law-rag \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:lus-laboris-py-service-account@py-labor-law-rag.iam.gserviceaccount.com"

# Test authentication with the service account
gcloud auth activate-service-account \
    --key-file=.gcpcredentials/lus-laboris-py-service-account.json

# Verify Storage access
gsutil ls
```

## Assigned Roles

### Storage Admin (`roles/storage.admin`)
- Allows managing Cloud Storage buckets and objects
- Includes permissions to create, modify, and delete buckets
- Allows configuring access policies and versioning

### Storage Object Admin (`roles/storage.objectAdmin`)
- Allows managing objects within buckets
- Includes permissions to upload, download, modify, and delete objects
- Allows configuring object metadata and ACLs

## Security

### Best Practices

1. **Never commit the JSON file to version control**
   - Make sure `.gcpcredentials/` is in your `.gitignore`

2. **Rotate keys regularly**
   - Generate new keys every 90 days
   - Delete old keys

3. **Principle of least privilege**
   - Only assign necessary roles
   - Review permissions periodically

4. **Monitoring**
   - Regularly review access logs
   - Set up alerts for suspicious activities

## Troubleshooting

### Error: "Permission denied"
- Verify the service account has the correct roles
- Make sure the JSON file is in the correct path
- Verify the Project ID is correct

### Error: "API not enabled"
- Enable the required APIs in the GCP console
- Wait a few minutes for changes to propagate

### Error: "Invalid credentials"
- Verify the JSON file is not corrupted
- Regenerate the JSON key if necessary
- Verify the service account is active

## Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [IAM Guide for Storage](https://cloud.google.com/storage/docs/access-control/iam)
- [Security Best Practices](https://cloud.google.com/security/best-practices)


---

# CONFIGURACIÓN DEL PROYECTO GOOGLE CLOUD PLATFORM

Esta guía te ayudará a configurar un proyecto de Google Cloud Platform con una cuenta de servicio que tenga los permisos necesarios para gestionar recursos de Google Cloud Storage.

## Prerrequisitos

- Cuenta de Google Cloud Platform activa
- Acceso a la consola de Google Cloud
- Google Cloud CLI instalado (opcional, pero recomendado)

## Paso 1: Crear un Proyecto en GCP

### Usando la Consola de Google Cloud

1. **Accede a la Consola de Google Cloud**
   - Ve a [console.cloud.google.com](https://console.cloud.google.com)
   - Inicia sesión con tu cuenta de Google

2. **Crear un nuevo proyecto**
   - Haz clic en el selector de proyecto en la parte superior
   - Selecciona "Nuevo proyecto"
   - Ingresa un nombre para el proyecto (ej: `py-labor-law-rag`)
   - Anota el **Project ID** generado automáticamente
   - Haz clic en "Crear"

3. **Seleccionar el proyecto**
   - Asegúrate de que el proyecto recién creado esté seleccionado

### Usando Google Cloud CLI

```bash
# Crear un nuevo proyecto
gcloud projects create py-labor-law-rag --name="Py Labor Law RAG"

# Configurar el proyecto como activo
gcloud config set project py-labor-law-rag
```

## Paso 2: Habilitar APIs Necesarias

### Usando la Consola de Google Cloud

1. **Habilitar Google Cloud Storage API**
   - Ve a "APIs y servicios" > "Biblioteca"
   - Busca "Google Cloud Storage API"
   - Haz clic en "Habilitar"

2. **Habilitar Cloud Resource Manager API**
   - Busca "Cloud Resource Manager API"
   - Haz clic en "Habilitar"

### Usando Google Cloud CLI

```bash
# Habilitar APIs necesarias
gcloud services enable storage.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

## Paso 3: Crear una Cuenta de Servicio

### Usando la Consola de Google Cloud

1. **Navegar a IAM y administración**
   - Ve a "IAM y administración" > "Cuentas de servicio"

2. **Crear cuenta de servicio**
   - Haz clic en "Crear cuenta de servicio"
   - Ingresa los siguientes datos:
     - **Nombre**: `lus-laboris-py-service-account`
     - **ID**: `lus-laboris-py-service-account` (se genera automáticamente)
     - **Descripción**: `Service account for Py Labor Law RAG project`
   - Haz clic en "Crear y continuar"

3. **Asignar roles**
   - En la sección "Otorgar acceso a esta cuenta de servicio al proyecto", agrega los siguientes roles:
     - **Administrador de almacenamiento** (`roles/storage.admin`)
     - **Administrador de objetos de Storage** (`roles/storage.objectAdmin`)
   - Haz clic en "Continuar" y luego en "Listo"

### Usando Google Cloud CLI

```bash
# Crear la cuenta de servicio
gcloud iam service-accounts create lus-laboris-py-service-account \
    --display-name="Lus Laboris Py Service Account" \
    --description="Service account for Py Labor Law RAG project"

# Asignar rol de Administrador de almacenamiento
gcloud projects add-iam-policy-binding py-labor-law-rag \
    --member="serviceAccount:lus-laboris-py-service-account@py-labor-law-rag.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Asignar rol de Administrador de objetos de Storage
gcloud projects add-iam-policy-binding py-labor-law-rag \
    --member="serviceAccount:lus-laboris-py-service-account@py-labor-law-rag.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

## Paso 4: Generar Clave JSON

### Usando la Consola de Google Cloud

1. **Acceder a la cuenta de servicio**
   - Ve a "IAM y administración" > "Cuentas de servicio"
   - Busca tu cuenta de servicio `lus-laboris-py-service-account`
   - Haz clic en el email de la cuenta de servicio

2. **Crear clave JSON**
   - Ve a la pestaña "Claves"
   - Haz clic en "Agregar clave" > "Crear nueva clave"
   - Selecciona "JSON" como tipo de clave
   - Haz clic en "Crear"
   - El archivo JSON se descargará automáticamente

3. **Guardar el archivo**
   - Renombra el archivo descargado a `lus-laboris-py-service-account.json`
   - Colócalo en la carpeta `.gcpcredentials/` del proyecto

### Usando Google Cloud CLI

```bash
# Crear directorio para credenciales
mkdir -p .gcpcredentials

# Generar y descargar clave JSON
gcloud iam service-accounts keys create .gcpcredentials/lus-laboris-py-service-account.json \
    --iam-account=lus-laboris-py-service-account@py-labor-law-rag.iam.gserviceaccount.com
```

## Paso 5: Verificar la Configuración

### Verificar con Google Cloud CLI

```bash
# Verificar que la cuenta de servicio tiene los roles correctos
gcloud projects get-iam-policy py-labor-law-rag \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:lus-laboris-py-service-account@py-labor-law-rag.iam.gserviceaccount.com"

# Probar autenticación con la cuenta de servicio
gcloud auth activate-service-account \
    --key-file=.gcpcredentials/lus-laboris-py-service-account.json

# Verificar acceso a Storage
gsutil ls
```

## Roles Asignados

### Administrador de almacenamiento (`roles/storage.admin`)
- Permite gestionar buckets y objetos de Cloud Storage
- Incluye permisos para crear, modificar y eliminar buckets
- Permite configurar políticas de acceso y versionado

### Administrador de objetos de Storage (`roles/storage.objectAdmin`)
- Permite gestionar objetos dentro de buckets
- Incluye permisos para subir, descargar, modificar y eliminar objetos
- Permite configurar metadatos y ACLs de objetos

## Seguridad

### Buenas Prácticas

1. **Nunca subas el archivo JSON al control de versiones**
   - Asegúrate de que `.gcpcredentials/` esté en tu `.gitignore`

2. **Rotar las claves regularmente**
   - Genera nuevas claves cada 90 días
   - Elimina las claves antiguas

3. **Principio de menor privilegio**
   - Solo asigna los roles necesarios
   - Revisa periódicamente los permisos

4. **Monitoreo**
   - Revisa regularmente los logs de acceso
   - Configura alertas para actividades sospechosas

## Solución de Problemas

### Error: "Permission denied"
- Verifica que la cuenta de servicio tenga los roles correctos
- Asegúrate de que el archivo JSON esté en la ruta correcta
- Verifica que el Project ID sea correcto

### Error: "API not enabled"
- Habilita las APIs necesarias en la consola de GCP
- Espera unos minutos para que los cambios se propaguen

### Error: "Invalid credentials"
- Verifica que el archivo JSON no esté corrupto
- Regenera la clave JSON si es necesario
- Verifica que la cuenta de servicio esté activa

## Recursos Adicionales

- [Documentación de Google Cloud Storage](https://cloud.google.com/storage/docs)
- [Guía de IAM para Storage](https://cloud.google.com/storage/docs/access-control/iam)
- [Mejores prácticas de seguridad](https://cloud.google.com/security/best-practices)