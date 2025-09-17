<div align="center">

**Language / Idioma:**
[🇺🇸 English](#description) | [🇪🇸 Español](#descripción)

</div>

---

# Utils

## Description

This folder contains utility scripts and tools for the lus-laboris-py project. These scripts help automate common tasks and provide convenient interfaces for project management.

### Available Scripts

| Script | Description | Purpose |
|--------|-------------|---------|
| `gcp_utils.py` | Google Cloud Platform utilities | Create, list, and manage GCS buckets for Terraform state |
| `setup_gcp_project.sh` | GCP Project Setup Script | Automated setup of GCP project with APIs, service accounts, and permissions |
| `generate_jwt_keys.sh` | JWT Keys Generator | Generate RSA public/private key pairs for JWT authentication |
| `generate_jwt_token.py` | JWT Token Generator | Generate and validate JWT tokens for API authentication |

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

## JWT Keys Generator

The `generate_jwt_keys.sh` script generates RSA public and private key pairs necessary for JWT authentication in the Lus Laboris API.

### Features

- **Configurable Key Size**: Generate RSA keys of 2048 bits by default (configurable)
- **Project Root Detection**: Automatically detects project root directory for consistent key placement
- **Automatic Directory Creation**: Creates output directory automatically
- **Secure Permissions**: Sets secure permissions (600 for private, 644 for public)
- **Dependency Validation**: Validates OpenSSL installation
- **Overwrite Protection**: Prevents accidental file overwriting
- **Detailed Key Information**: Shows comprehensive information about generated keys
- **Colorized Output**: Clear visual feedback for different types of messages
- **Parameter Validation**: Validates input parameters and provides helpful error messages

### Key Location Strategy

The script automatically detects the project root directory and places keys in `PROJECT_ROOT/keys/` by default. This ensures:

- **Consistency**: Keys are always in the same location regardless of where the script is executed
- **Integration**: Works seamlessly with the API and other project components
- **Security**: Keys are placed in a predictable, project-specific location
- **Flexibility**: Users can still specify custom locations using the `--directory` option

### Prerequisites

- **OpenSSL**: Must be installed on the system
  - Ubuntu/Debian: `sudo apt-get install openssl`
  - CentOS/RHEL: `sudo yum install openssl`
  - macOS: `brew install openssl`

### Usage

#### Basic Usage

```bash
# Generate keys with default configuration
./generate_jwt_keys.sh

# Specify directory and key size
./generate_jwt_keys.sh -d /path/to/keys -s 4096

# Overwrite existing files
./generate_jwt_keys.sh -f

# Show complete help
./generate_jwt_keys.sh -h
```

#### Command Line Options

| Option | Description | Default Value |
|--------|-------------|---------------|
| `-d, --directory DIR` | Output directory | `keys` |
| `-s, --size SIZE` | Key size in bits | `2048` |
| `-p, --private FILE` | Private key filename | `private_key.pem` |
| `-u, --public FILE` | Public key filename | `public_key.pem` |
| `-f, --force` | Overwrite existing files | `false` |
| `-h, --help` | Show help | - |

#### Examples

```bash
# Generate keys with default configuration
./generate_jwt_keys.sh

# Generate 4096-bit keys in specific directory
./generate_jwt_keys.sh -d /home/user/api-keys -s 4096

# Generate keys with custom filenames
./generate_jwt_keys.sh -p my_private.pem -u my_public.pem

# Force overwrite existing files
./generate_jwt_keys.sh -f
```

### Output

The script generates:

1. **Private Key** (`private_key.pem`): For signing JWT tokens
2. **Public Key** (`public_key.pem`): For validating JWT tokens

#### Generated Files

```
keys/
├── private_key.pem    # Private key (permissions: 600)
└── public_key.pem     # Public key (permissions: 644)
```

### API Configuration

After generating the keys, configure the environment variables in your `.env` file:

```env
# JWT Configuration
JWT_PRIVATE_KEY_PATH=keys/private_key.pem
JWT_PUBLIC_KEY_PATH=keys/public_key.pem
JWT_TOKEN_EXPIRY_MINUTES=60
```

### Security

- Private key has `600` permissions (owner read/write only)
- Public key has `644` permissions (read for everyone)
- Private key should **NEVER** be shared or versioned
- Public key can be shared for token validation

### Integration with API

The generated keys are compatible with the Lus Laboris API:

1. **Token Generation**: Uses private key for signing
2. **Token Validation**: Uses public key for verification
3. **Algorithm**: RSA with SHA-256 (RS256)

### Troubleshooting

#### Common Issues

1. **"OpenSSL not installed"**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install openssl
   
   # CentOS/RHEL
   sudo yum install openssl
   
   # macOS
   brew install openssl
   ```

2. **"Files already exist"**
   ```bash
   # Use --force to overwrite
   ./generate_jwt_keys.sh -f
   ```

3. **"Permission denied"**
   ```bash
   # Make script executable
   chmod +x generate_jwt_keys.sh
   ```

### Key Information Display

The script provides detailed information about generated keys:

- **File paths and sizes**
- **File permissions**
- **Key fingerprints** for verification
- **Usage instructions** for API configuration

---

## JWT Token Generator

The `generate_jwt_token.py` script generates and validates JWT tokens using the RSA keys created by `generate_jwt_keys.sh`. It provides both command-line and programmatic interfaces for token management.

### Features

- **Command-Line Interface**: Easy-to-use CLI for token generation and validation
- **Programmatic API**: Can be imported and used in other Python scripts
- **Environment Configuration**: Uses environment variables for key paths and settings
- **Project Root Detection**: Automatically resolves relative paths relative to project root
- **Modern Python Support**: Uses timezone-aware datetime objects (no deprecation warnings)
- **Token Validation**: Built-in token validation using public key
- **Custom Claims**: Support for additional claims in tokens
- **Flexible Expiry**: Configurable token expiration times in minutes
- **File Output**: Option to save tokens to files
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## JWT Token Setup Script

The `setup_jwt_token.sh` script automates the complete process of generating RSA keys and JWT tokens in a single command. This script is designed to **streamline and accelerate** the JWT setup process, making it ideal for scenarios where you want to quickly generate both keys and tokens without running multiple commands separately.

### Why Use This Script?

This script **facilitates and accelerates** the JWT setup task by:

- **One-Command Solution**: Combines key generation and token creation in a single execution
- **Time-Saving**: Eliminates the need to run `generate_jwt_keys.sh` and `generate_jwt_token.py` separately
- **Reduced Complexity**: Handles all the coordination between different scripts automatically
- **Perfect for Quick Setup**: Ideal when you need to rapidly set up JWT authentication
- **Streamlined Workflow**: Reduces manual steps and potential errors in the setup process

### Features

- **Complete Automation**: Generates keys and tokens in one command
- **Interactive Confirmation**: Asks for confirmation before overwriting existing keys
- **Flexible Configuration**: Supports all options from individual scripts
- **Token Validation**: Automatically validates generated tokens
- **File Output**: Option to save tokens to files
- **Environment Variable Setup**: Shows instructions for using JWT_TOKEN variable
- **Colorized Output**: Clear visual feedback with colored messages
- **Error Handling**: Comprehensive error handling and user guidance
- **UV Integration**: Requires `uv` for consistent environment and dependency management

### UV Integration

The script requires `uv` to be installed and uses it for running Python scripts, ensuring:

- **Consistent Environment**: Uses the project's virtual environment managed by `uv`
- **Dependency Management**: Automatically installs and uses the correct dependencies
- **Project Integration**: Works seamlessly with the project's dependency management
- **Reliable Execution**: Always uses the same environment regardless of system configuration

**Behavior**:
- Changes to project root directory and uses `uv run generate_jwt_token.py`
- Project root detection ensures `uv run` works correctly with the project's virtual environment
- Shows clear error message with installation instructions if `uv` is not available
- Consistent execution environment for all Python operations

### Prerequisites

- **uv**: Required for running Python scripts (install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Python 3.13+**: Required for running the script
- **Dependencies**: PyJWT and cryptography packages (automatically managed by `uv`)
- **Bash**: Required for running the setup script
- **OpenSSL**: Required for key generation

### Usage

#### Command Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `--username` | Username for the token | No (default: admin) |
| `--expiry` | Token expiry in minutes | No (default: 60) |
| `--key-size` | RSA key size in bits | No (default: 2048) |
| `--output` | Output file to save token | No |
| `--force` | Overwrite existing keys without confirmation | No |
| `--help` | Show help message | No |

#### Examples

**Basic usage with default values:**
```bash
./setup_jwt_token.sh
```

**Generate token for specific user with custom expiry:**
```bash
./setup_jwt_token.sh -u myuser -e 120
```

**Save token to file:**
```bash
./setup_jwt_token.sh -u admin -o my_token.txt
```

**Force overwrite existing keys:**
```bash
./setup_jwt_token.sh --force
```

**Generate 4096-bit keys:**
```bash
./setup_jwt_token.sh -k 4096 --force
```

#### How This Script Facilitates the Task

**Without this script (manual process):**
```bash
# Step 1: Generate RSA keys
./generate_jwt_keys.sh --size 2048

# Step 2: Set environment variables
export JWT_PRIVATE_KEY_PATH=keys/private_key.pem
export JWT_PUBLIC_KEY_PATH=keys/public_key.pem
export JWT_TOKEN_EXPIRY_MINUTES=60

# Step 3: Generate token
uv run generate_jwt_token.py --username admin --expiry 60

# Step 4: Validate token (optional)
uv run generate_jwt_token.py --validate --token "eyJ..."
```

**With this script (streamlined process):**
```bash
# Single command does everything
./setup_jwt_token.sh -u admin -e 60
```

**Benefits:**
- **3-4 commands reduced to 1**: Eliminates manual coordination
- **No environment variable setup**: Handles paths automatically
- **Automatic validation**: Ensures token works correctly
- **Error handling**: Clear messages if something goes wrong
- **Time savings**: Complete setup in seconds instead of minutes

#### Output

The script provides:
- **Colored output** for better readability
- **Progress indicators** for each step
- **Token validation** to ensure correctness
- **Environment variable instructions** for easy usage
- **File output** if requested

#### Environment Variable Setup

After successful execution, the script shows how to use the generated token:

```bash
# Set the token as an environment variable
export JWT_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."

# Use in API calls
curl -H "Authorization: Bearer $JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/data/load-to-vectorstore
```

### Path Resolution

The script automatically resolves relative paths relative to the project root directory. This means:

- **Relative paths** (e.g., `keys/private_key.pem`) are resolved relative to the project root
- **Absolute paths** (e.g., `/path/to/keys/private_key.pem`) are used as-is
- **Works from anywhere**: The script can be executed from any directory and will find the correct key files

**Example**:
```bash
# From any directory, this will work:
cd /tmp
python3 /path/to/project/utils/generate_jwt_token.py --username admin

# The script will automatically look for keys in:
# /path/to/project/keys/private_key.pem
# /path/to/project/keys/public_key.pem
```

### Prerequisites

- **Python 3.13+**: Required for running the script
- **Dependencies**: PyJWT and cryptography packages
- **JWT Keys**: RSA keys generated by `generate_jwt_keys.sh`
- **Environment Variables**: JWT configuration must be set

### Installation

1. Install dependencies:
```bash
cd utils
uv sync
```

2. Set up environment variables in your `.env` file:
```env
JWT_PRIVATE_KEY_PATH=keys/private_key.pem
JWT_PUBLIC_KEY_PATH=keys/public_key.pem
JWT_TOKEN_EXPIRY_MINUTES=60
```

### Usage

#### Command Line Interface

```bash
# Basic token generation
python generate_jwt_token.py --username admin

# Token with custom expiry
python generate_jwt_token.py --username admin --expiry 120

# Token with additional claims
python generate_jwt_token.py --username admin --claims '{"role": "admin", "permissions": ["read", "write"]}'

# Save token to file
python generate_jwt_token.py --username admin --output token.txt

# Validate existing token
python generate_jwt_token.py --validate --token "YOUR_TOKEN_HERE"
```

#### Command Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `--username` | Username for the token | Yes (for generation) |
| `--expiry` | Token expiry in minutes | No |
| `--claims` | Additional claims as JSON string | No |
| `--output` | Output file to save token | No |
| `--validate` | Validate an existing token | No |
| `--token` | Token to validate (with --validate) | Yes (for validation) |

#### Programmatic Usage

```python
from generate_jwt_token import JWTTokenGenerator

# Initialize generator
generator = JWTTokenGenerator()

# Generate basic token
token = generator.generate_token(
    username="admin",
    expiry_minutes=60
)

# Generate token with additional claims
token_with_claims = generator.generate_token(
    username="user123",
    expiry_minutes=120,
    additional_claims={
        "role": "admin",
        "permissions": ["read", "write", "delete"],
        "department": "IT"
    }
)

# Validate token
payload = generator.validate_token(token)
print(f"Token is valid for user: {payload['username']}")
```

### Token Structure

Generated tokens include the following standard claims:

- **`sub`**: Subject (username)
- **`username`**: Username
- **`iat`**: Issued at timestamp
- **`exp`**: Expiration timestamp (in minutes)
- **`iss`**: Issuer ("lus-laboris-api")
- **`aud`**: Audience ("lus-laboris-client")

> **Security Note**: Passwords are NOT stored in JWT tokens for security reasons. JWT tokens are decodable and should only contain non-sensitive information.

### API Integration

The generated tokens are compatible with the Lus Laboris API:

1. **Authorization Header**: Use `Authorization: Bearer <token>`
2. **Token Validation**: API validates tokens using the public key
3. **User Authentication**: Username is extracted from token claims

### Examples

#### Example 1: Basic Token Generation

```bash
# Generate a token
python generate_jwt_token.py --username admin

# Output:
# 🔑 JWT Token Generated Successfully!
# ==================================================
# eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
# ==================================================
```

#### Example 2: Token with Custom Claims

```bash
# Generate token with role and permissions
python generate_jwt_token.py \
  --username admin \
  --claims '{"role": "admin", "permissions": ["read", "write", "delete"]}'
```

#### Example 3: Token Validation

```bash
# Validate a token
python generate_jwt_token.py --validate --token "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."

# Output:
# ✅ Token is valid!
# 📋 Token payload:
# {
#   "sub": "admin",
#   "username": "admin",
#   "iat": 1703123456,
#   "exp": 1703209856,
#   "iss": "lus-laboris-api",
#   "aud": "lus-laboris-client"
# }
```

### Error Handling

The script provides clear error messages for common issues:

- **Missing keys**: "Private key file not found"
- **Invalid token**: "Invalid token" with specific error details
- **Expired token**: "Token has expired"
- **Invalid JSON**: "Invalid JSON in --claims"
- **Missing arguments**: Clear usage instructions

### Security Considerations

- **Private Key Security**: Private key should be kept secure and never shared
- **Token Expiry**: Use appropriate expiry times for your use case
- **No Sensitive Data**: Never store passwords or sensitive data in JWT tokens
- **Key Rotation**: Regularly rotate RSA keys for enhanced security
- **Token Validation**: Always validate tokens on the server side
- **HTTPS Only**: Always use HTTPS when transmitting tokens

### Troubleshooting

#### Common Issues

1. **"Private key file not found"**
   ```bash
   # Generate keys first
   ./generate_jwt_keys.sh
   ```

2. **"Module not found" errors**
   ```bash
   # Install dependencies
   uv sync
   ```

3. **"Invalid token" errors**
   - Check if token is expired
   - Verify token format
   - Ensure public key is available

4. **Environment variable issues**
   ```bash
   # Check environment variables
   echo $JWT_PRIVATE_KEY_PATH
   echo $JWT_PUBLIC_KEY_PATH
   echo $JWT_TOKEN_EXPIRY_HOURS
   ```

### Integration Examples

#### Using with curl

```bash
# Generate token
TOKEN=$(python generate_jwt_token.py --username admin --output -)

# Use token in API call
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/data/load-to-vectorstore \
     -d '{"mode": "local", "filename": "data.json"}'
```

#### Using in Python scripts

```python
import requests
from generate_jwt_token import JWTTokenGenerator

# Generate token
generator = JWTTokenGenerator()
token = generator.generate_token("admin", "secret123")

# Make API request
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/api/data/load-to-vectorstore",
    json={"mode": "local", "filename": "data.json"},
    headers=headers
)
```

---

## Descripción

Esta carpeta contiene scripts de utilidad y herramientas para el proyecto lus-laboris-py. Estos scripts ayudan a automatizar tareas comunes y proporcionan interfaces convenientes para la gestión del proyecto.

### Scripts Disponibles

| Script | Descripción | Propósito |
|--------|-------------|-----------|
| `gcp_utils.py` | Utilidades de Google Cloud Platform | Crear, listar y gestionar buckets GCS para el estado de Terraform |
| `setup_gcp_project.sh` | Script de Configuración de Proyecto GCP | Configuración automatizada de proyecto GCP con APIs, cuentas de servicio y permisos |
| `generate_jwt_keys.sh` | Generador de Claves JWT | Generar pares de claves RSA pública/privada para autenticación JWT |
| `generate_jwt_token.py` | Generador de Tokens JWT | Generar y validar tokens JWT para autenticación de API |

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

---

## Script de Configuración JWT

El script `setup_jwt_token.sh` automatiza el proceso completo de generación de claves RSA y tokens JWT en un solo comando. Este script está diseñado para **simplificar y acelerar** el proceso de configuración JWT, siendo ideal para escenarios donde quieres generar rápidamente tanto claves como tokens sin ejecutar múltiples comandos por separado.

### ¿Por Qué Usar Este Script?

Este script **facilita y acelera** la tarea de configuración JWT al:

- **Solución de Un Comando**: Combina la generación de claves y creación de tokens en una sola ejecución
- **Ahorro de Tiempo**: Elimina la necesidad de ejecutar `generate_jwt_keys.sh` y `generate_jwt_token.py` por separado
- **Reducción de Complejidad**: Maneja toda la coordinación entre diferentes scripts automáticamente
- **Perfecto para Configuración Rápida**: Ideal cuando necesitas configurar rápidamente la autenticación JWT
- **Flujo de Trabajo Simplificado**: Reduce pasos manuales y errores potenciales en el proceso de configuración

### Características

- **Automatización Completa**: Genera claves y tokens en un solo comando
- **Confirmación Interactiva**: Pide confirmación antes de sobrescribir claves existentes
- **Configuración Flexible**: Soporta todas las opciones de los scripts individuales
- **Validación de Tokens**: Valida automáticamente los tokens generados
- **Salida a Archivo**: Opción para guardar tokens en archivos
- **Configuración de Variable de Entorno**: Muestra instrucciones para usar la variable JWT_TOKEN
- **Salida Coloreada**: Retroalimentación visual clara con mensajes coloreados
- **Manejo de Errores**: Manejo comprensivo de errores y orientación al usuario
- **Integración con UV**: Requiere `uv` para entorno consistente y gestión de dependencias

### Uso

#### Opciones de Línea de Comandos

| Opción | Descripción | Requerido |
|--------|-------------|-----------|
| `--username` | Nombre de usuario para el token | No (por defecto: admin) |
| `--expiry` | Expiración del token en minutos | No (por defecto: 60) |
| `--key-size` | Tamaño de clave RSA en bits | No (por defecto: 2048) |
| `--output` | Archivo de salida para guardar token | No |
| `--force` | Sobrescribir claves existentes sin confirmación | No |
| `--help` | Mostrar mensaje de ayuda | No |

#### Ejemplos

**Uso básico con valores por defecto:**
```bash
./setup_jwt_token.sh
```

**Generar token para usuario específico con expiración personalizada:**
```bash
./setup_jwt_token.sh -u miusuario -e 120
```

**Guardar token en archivo:**
```bash
./setup_jwt_token.sh -u admin -o mi_token.txt
```

**Forzar sobrescritura de claves existentes:**
```bash
./setup_jwt_token.sh --force
```

**Generar claves de 4096 bits:**
```bash
./setup_jwt_token.sh -k 4096 --force
```

#### Cómo Este Script Facilita la Tarea

**Sin este script (proceso manual):**
```bash
# Paso 1: Generar claves RSA
./generate_jwt_keys.sh --size 2048

# Paso 2: Configurar variables de entorno
export JWT_PRIVATE_KEY_PATH=keys/private_key.pem
export JWT_PUBLIC_KEY_PATH=keys/public_key.pem
export JWT_TOKEN_EXPIRY_MINUTES=60

# Paso 3: Generar token
uv run generate_jwt_token.py --username admin --expiry 60

# Paso 4: Validar token (opcional)
uv run generate_jwt_token.py --validate --token "eyJ..."
```

**Con este script (proceso simplificado):**
```bash
# Un solo comando hace todo
./setup_jwt_token.sh -u admin -e 60
```

**Beneficios:**
- **3-4 comandos reducidos a 1**: Elimina la coordinación manual
- **Sin configuración de variables de entorno**: Maneja las rutas automáticamente
- **Validación automática**: Asegura que el token funcione correctamente
- **Manejo de errores**: Mensajes claros si algo sale mal
- **Ahorro de tiempo**: Configuración completa en segundos en lugar de minutos

#### Salida

El script proporciona:
- **Salida coloreada** para mejor legibilidad
- **Indicadores de progreso** para cada paso
- **Validación de tokens** para asegurar corrección
- **Instrucciones de variable de entorno** para uso fácil
- **Salida a archivo** si se solicita

#### Configuración de Variable de Entorno

Después de una ejecución exitosa, el script muestra cómo usar el token generado:

```bash
# Establecer el token como variable de entorno
export JWT_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."

# Usar en llamadas API
curl -H "Authorization: Bearer $JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/data/load-to-vectorstore
```

---

## Generador de Claves JWT

El script `generate_jwt_keys.sh` genera pares de claves RSA pública y privada necesarias para la autenticación JWT en la API Lus Laboris.

### Características

- **Tamaño de Clave Configurable**: Genera claves RSA de 2048 bits por defecto (configurable)
- **Detección Automática del Proyecto**: Detecta automáticamente el directorio raíz del proyecto para ubicación consistente de claves
- **Creación Automática de Directorio**: Crea el directorio de salida automáticamente
- **Permisos Seguros**: Establece permisos seguros (600 para privada, 644 para pública)
- **Validación de Dependencias**: Valida la instalación de OpenSSL
- **Protección contra Sobrescritura**: Previene la sobrescritura accidental de archivos
- **Información Detallada de Claves**: Muestra información integral sobre las claves generadas
- **Salida Colorizada**: Retroalimentación visual clara para diferentes tipos de mensajes
- **Validación de Parámetros**: Valida parámetros de entrada y proporciona mensajes de error útiles

### Estrategia de Ubicación de Claves

El script detecta automáticamente el directorio raíz del proyecto y coloca las claves en `PROJECT_ROOT/keys/` por defecto. Esto asegura:

- **Consistencia**: Las claves siempre están en la misma ubicación independientemente de dónde se ejecute el script
- **Integración**: Funciona perfectamente con la API y otros componentes del proyecto
- **Seguridad**: Las claves se colocan en una ubicación predecible y específica del proyecto
- **Flexibilidad**: Los usuarios aún pueden especificar ubicaciones personalizadas usando la opción `--directory`

### Prerrequisitos

- **OpenSSL**: Debe estar instalado en el sistema
  - Ubuntu/Debian: `sudo apt-get install openssl`
  - CentOS/RHEL: `sudo yum install openssl`
  - macOS: `brew install openssl`

### Uso

#### Uso Básico

```bash
# Generar claves con configuración por defecto
./generate_jwt_keys.sh

# Especificar directorio y tamaño de clave
./generate_jwt_keys.sh -d /ruta/a/keys -s 4096

# Sobrescribir archivos existentes
./generate_jwt_keys.sh -f

# Mostrar ayuda completa
./generate_jwt_keys.sh -h
```

#### Opciones de Línea de Comandos

| Opción | Descripción | Valor por Defecto |
|--------|-------------|-------------------|
| `-d, --directory DIR` | Directorio de salida | `keys` |
| `-s, --size SIZE` | Tamaño de la clave en bits | `2048` |
| `-p, --private FILE` | Nombre del archivo de clave privada | `private_key.pem` |
| `-u, --public FILE` | Nombre del archivo de clave pública | `public_key.pem` |
| `-f, --force` | Sobrescribir archivos existentes | `false` |
| `-h, --help` | Mostrar ayuda | - |

#### Ejemplos

```bash
# Generar claves con configuración por defecto
./generate_jwt_keys.sh

# Generar claves de 4096 bits en directorio específico
./generate_jwt_keys.sh -d /home/usuario/api-keys -s 4096

# Generar claves con nombres personalizados
./generate_jwt_keys.sh -p mi_privada.pem -u mi_publica.pem

# Forzar sobrescritura de archivos existentes
./generate_jwt_keys.sh -f
```

### Salida

El script genera:

1. **Clave Privada** (`private_key.pem`): Para firmar tokens JWT
2. **Clave Pública** (`public_key.pem`): Para validar tokens JWT

#### Archivos Generados

```
keys/
├── private_key.pem    # Clave privada (permisos: 600)
└── public_key.pem     # Clave pública (permisos: 644)
```

### Configuración de la API

Después de generar las claves, configura las variables de entorno en tu archivo `.env`:

```env
# Configuración JWT
JWT_PRIVATE_KEY_PATH=keys/private_key.pem
JWT_PUBLIC_KEY_PATH=keys/public_key.pem
JWT_TOKEN_EXPIRY_MINUTES=60
```

### Seguridad

- La clave privada tiene permisos `600` (solo lectura/escritura del propietario)
- La clave pública tiene permisos `644` (lectura para todos)
- La clave privada **NUNCA** debe ser compartida o versionada
- La clave pública puede ser compartida para validación de tokens

### Integración con la API

Las claves generadas son compatibles con la API Lus Laboris:

1. **Generación de Tokens**: Usa la clave privada para firmar
2. **Validación de Tokens**: Usa la clave pública para verificar
3. **Algoritmo**: RSA con SHA-256 (RS256)

### Solución de Problemas

#### Problemas Comunes

1. **"OpenSSL no instalado"**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install openssl
   
   # CentOS/RHEL
   sudo yum install openssl
   
   # macOS
   brew install openssl
   ```

2. **"Los archivos ya existen"**
   ```bash
   # Usar --force para sobrescribir
   ./generate_jwt_keys.sh -f
   ```

3. **"Permiso denegado"**
   ```bash
   # Hacer el script ejecutable
   chmod +x generate_jwt_keys.sh
   ```

### Visualización de Información de Claves

El script proporciona información detallada sobre las claves generadas:

- **Rutas y tamaños de archivos**
- **Permisos de archivos**
- **Huellas digitales de claves** para verificación
- **Instrucciones de uso** para configuración de la API

---

## Generador de Tokens JWT

El script `generate_jwt_token.py` genera y valida tokens JWT usando las claves RSA creadas por `generate_jwt_keys.sh`. Proporciona interfaces tanto de línea de comandos como programáticas para la gestión de tokens.

### Características

- **Interfaz de Línea de Comandos**: CLI fácil de usar para generación y validación de tokens
- **API Programática**: Puede ser importado y usado en otros scripts de Python
- **Configuración de Entorno**: Usa variables de entorno para rutas de claves y configuraciones
- **Detección de Raíz del Proyecto**: Resuelve automáticamente rutas relativas respecto a la raíz del proyecto
- **Soporte Moderno de Python**: Usa objetos datetime con zona horaria (sin warnings de deprecación)
- **Validación de Tokens**: Validación de tokens integrada usando la clave pública
- **Claims Personalizados**: Soporte para claims adicionales en tokens
- **Expiración Flexible**: Tiempos de expiración de tokens configurables en minutos
- **Salida a Archivo**: Opción para guardar tokens en archivos
- **Logging Integral**: Logging detallado para depuración y monitoreo

### Resolución de Rutas

El script resuelve automáticamente las rutas relativas respecto al directorio raíz del proyecto. Esto significa:

- **Rutas relativas** (ej., `keys/private_key.pem`) se resuelven respecto a la raíz del proyecto
- **Rutas absolutas** (ej., `/path/to/keys/private_key.pem`) se usan tal como están
- **Funciona desde cualquier lugar**: El script puede ejecutarse desde cualquier directorio y encontrará los archivos de claves correctos

**Ejemplo**:
```bash
# Desde cualquier directorio, esto funcionará:
cd /tmp
python3 /path/to/project/utils/generate_jwt_token.py --username admin

# El script buscará automáticamente las claves en:
# /path/to/project/keys/private_key.pem
# /path/to/project/keys/public_key.pem
```

### Integración con UV

El script requiere que `uv` esté instalado y lo usa para ejecutar scripts de Python, asegurando:

- **Entorno Consistente**: Usa el entorno virtual del proyecto gestionado por `uv`
- **Gestión de Dependencias**: Instala y usa automáticamente las dependencias correctas
- **Integración del Proyecto**: Funciona perfectamente con la gestión de dependencias del proyecto
- **Ejecución Confiable**: Siempre usa el mismo entorno independientemente de la configuración del sistema

**Comportamiento**:
- Cambia al directorio raíz del proyecto y usa `uv run generate_jwt_token.py`
- La detección de la raíz del proyecto asegura que `uv run` funcione correctamente con el entorno virtual del proyecto
- Muestra mensaje de error claro con instrucciones de instalación si `uv` no está disponible
- Entorno de ejecución consistente para todas las operaciones de Python

### Prerrequisitos

- **uv**: Requerido para ejecutar scripts de Python (instalar con: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Python 3.13+**: Requerido para ejecutar el script
- **Dependencias**: Paquetes PyJWT y cryptography (gestionados automáticamente por `uv`)
- **Claves JWT**: Claves RSA generadas por `generate_jwt_keys.sh`
- **Variables de Entorno**: La configuración JWT debe estar establecida

### Instalación

1. Instalar dependencias:
```bash
cd utils
uv sync
```

2. Configurar variables de entorno en tu archivo `.env`:
```env
JWT_PRIVATE_KEY_PATH=keys/private_key.pem
JWT_PUBLIC_KEY_PATH=keys/public_key.pem
JWT_TOKEN_EXPIRY_MINUTES=60
```

### Uso

#### Interfaz de Línea de Comandos

```bash
# Generación básica de token
python generate_jwt_token.py --username admin

# Token con expiración personalizada
python generate_jwt_token.py --username admin --expiry 120

# Token con claims adicionales
python generate_jwt_token.py --username admin --claims '{"role": "admin", "permissions": ["read", "write"]}'

# Guardar token en archivo
python generate_jwt_token.py --username admin --output token.txt

# Validar token existente
python generate_jwt_token.py --validate --token "TU_TOKEN_AQUI"
```

#### Opciones de Línea de Comandos

| Opción | Descripción | Requerido |
|--------|-------------|-----------|
| `--username` | Nombre de usuario para el token | Sí (para generación) |
| `--expiry` | Expiración del token en minutos | No |
| `--claims` | Claims adicionales como string JSON | No |
| `--output` | Archivo de salida para guardar token | No |
| `--validate` | Validar un token existente | No |
| `--token` | Token a validar (con --validate) | Sí (para validación) |

#### Uso Programático

```python
from generate_jwt_token import JWTTokenGenerator

# Inicializar generador
generator = JWTTokenGenerator()

# Generar token básico
token = generator.generate_token(
    username="admin",
    expiry_minutes=60
)

# Generar token con claims adicionales
token_with_claims = generator.generate_token(
    username="user123",
    expiry_minutes=120,
    additional_claims={
        "role": "admin",
        "permissions": ["read", "write", "delete"],
        "department": "IT"
    }
)

# Validar token
payload = generator.validate_token(token)
print(f"Token es válido para usuario: {payload['username']}")
```

### Estructura del Token

Los tokens generados incluyen los siguientes claims estándar:

- **`sub`**: Sujeto (nombre de usuario)
- **`username`**: Nombre de usuario
- **`iat`**: Timestamp de emisión
- **`exp`**: Timestamp de expiración (en minutos)
- **`iss`**: Emisor ("lus-laboris-api")
- **`aud`**: Audiencia ("lus-laboris-client")

> **Nota de Seguridad**: Las contraseñas NO se almacenan en los tokens JWT por razones de seguridad. Los tokens JWT son decodificables y solo deben contener información no sensible.

### Integración con la API

Los tokens generados son compatibles con la API Lus Laboris:

1. **Header de Autorización**: Usar `Authorization: Bearer <token>`
2. **Validación de Token**: La API valida tokens usando la clave pública
3. **Autenticación de Usuario**: El nombre de usuario se extrae de los claims del token

### Ejemplos

#### Ejemplo 1: Generación Básica de Token

```bash
# Generar un token
python generate_jwt_token.py --username admin

# Salida:
# 🔑 Token JWT Generado Exitosamente!
# ==================================================
# eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
# ==================================================
```

#### Ejemplo 2: Token con Claims Personalizados

```bash
# Generar token con rol y permisos
python generate_jwt_token.py \
  --username admin \
  --claims '{"role": "admin", "permissions": ["read", "write", "delete"]}'
```

#### Ejemplo 3: Validación de Token

```bash
# Validar un token
python generate_jwt_token.py --validate --token "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."

# Salida:
# ✅ Token es válido!
# 📋 Payload del token:
# {
#   "sub": "admin",
#   "username": "admin",
#   "iat": 1703123456,
#   "exp": 1703209856,
#   "iss": "lus-laboris-api",
#   "aud": "lus-laboris-client"
# }
```

### Manejo de Errores

El script proporciona mensajes de error claros para problemas comunes:

- **Claves faltantes**: "Archivo de clave privada no encontrado"
- **Token inválido**: "Token inválido" con detalles específicos del error
- **Token expirado**: "El token ha expirado"
- **JSON inválido**: "JSON inválido en --claims"
- **Argumentos faltantes**: Instrucciones de uso claras

### Consideraciones de Seguridad

- **Seguridad de Clave Privada**: La clave privada debe mantenerse segura y nunca compartirse
- **Expiración de Token**: Usar tiempos de expiración apropiados para tu caso de uso
- **Sin Datos Sensibles**: Nunca almacenar contraseñas o datos sensibles en tokens JWT
- **Rotación de Claves**: Rotar regularmente las claves RSA para mayor seguridad
- **Validación de Tokens**: Siempre validar tokens en el lado del servidor
- **Solo HTTPS**: Siempre usar HTTPS al transmitir tokens

### Solución de Problemas

#### Problemas Comunes

1. **"Archivo de clave privada no encontrado"**
   ```bash
   # Generar claves primero
   ./generate_jwt_keys.sh
   ```

2. **Errores "Módulo no encontrado"**
   ```bash
   # Instalar dependencias
   uv sync
   ```

3. **Errores "Token inválido"**
   - Verificar si el token ha expirado
   - Verificar formato del token
   - Asegurar que la clave pública esté disponible

4. **Problemas con variables de entorno**
   ```bash
   # Verificar variables de entorno
   echo $JWT_PRIVATE_KEY_PATH
   echo $JWT_PUBLIC_KEY_PATH
   echo $JWT_TOKEN_EXPIRY_HOURS
   ```

### Ejemplos de Integración

#### Usando con curl

```bash
# Generar token
TOKEN=$(python generate_jwt_token.py --username admin --output -)

# Usar token en llamada API
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/api/data/load-to-vectorstore \
     -d '{"mode": "local", "filename": "data.json"}'
```

#### Usando en scripts de Python

```python
import requests
from generate_jwt_token import JWTTokenGenerator

# Generar token
generator = JWTTokenGenerator()
token = generator.generate_token("admin", "secret123")

# Hacer petición API
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/api/data/load-to-vectorstore",
    json={"mode": "local", "filename": "data.json"},
    headers=headers
)
```