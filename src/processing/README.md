<div align="center">

**Language / Idioma:**
[🇺🇸 English](#legal-text-processing) | [🇪🇸 Español](#procesamiento-de-texto-legal)

</div>

---

# Legal Text Processing

This directory contains scripts for extracting and processing text from Paraguay's Labor Code.

## Available Scripts

### `extract_law_text.py`

Main script for extracting and processing text from Paraguay's Labor Code from its official source.

#### Features

- **Two execution modes**:
  - **Local**: Saves files to local filesystem
  - **GCS**: Creates temporary folders and uploads JSON to Google Cloud Storage

- **Functionalities**:
  - Automatic HTML download from official site
  - Text extraction and cleaning
  - Structured article segmentation
  - Quality validation and reporting
  - JSON format saving
  - Phoenix/OpenTelemetry tracing for observability (always enabled)

#### Dependencies Installation

- See the [UV documentation](https://github.com/astral-sh/uv) for more details.

```bash
# Install dependencies using uv
uv sync
```

#### Usage

##### Local Mode (default)

```bash
# Basic execution
uv run extract_law_text.py

# Custom filenames
uv run extract_law_text.py --raw-filename mylaw.html --processed-filename myoutput.json

# Skip quality validation for faster processing
uv run extract_law_text.py --skip-quality-validation
```

- The raw HTML will be saved to `data/raw/{raw-filename}` (default: `codigo_trabajo_py.html`) in the project root (not the current directory).
- The processed JSON will be saved to `data/processed/{processed-filename}` (default: `codigo_trabajo_articulos.json`) in the project root.

#### Quality Validation

The script automatically validates processed data quality by:
- **Structure validation**: Checks required fields and valid article numbers (1-413)
- **Completeness verification**: Ensures all 413 articles are present without duplicates
- **Content analysis**: Analyzes article length, special characters, and content quality
- **Comprehensive reporting**: Generates detailed quality reports with metrics and status

Use `--skip-quality-validation` to disable validation for faster processing.

##### Google Cloud Storage Mode

```bash
# Basic GCS execution
uv run extract_law_text.py --mode gcs --bucket-name my-bucket

# Use local credentials (for local development)
uv run extract_law_text.py --mode gcs --bucket-name my-bucket --use-local-credentials
```

- The raw HTML will always be uploaded to `raw/{raw-filename}` in the bucket (default: `codigo_trabajo_py.html`).
- The processed JSON will always be uploaded to `processed/{processed-filename}` in the bucket (default: `codigo_trabajo_articulos.json`).

#### Command Line Arguments

| Argument             | Description                                         | Required           | Default                        |
|---------------------|-----------------------------------------------------|--------------------|--------------------------------|
| `--mode`             | Execution mode: `local` or `gcs`                    | No                 | `local`                         |
| `--url`              | Law page URL                                        | No                 | Official URL                    |
| `--bucket-name`      | GCS bucket name (gcs mode)                          | Yes (for gcs mode) | -                               |
| `--raw-filename`     | Name for raw HTML file                              | No                 | `codigo_trabajo_py.html`        |
| `--processed-filename`| Name for processed JSON file                        | No                 | `codigo_trabajo_articulos.json` |
| `--use-local-credentials`| Force use of local credentials file (for local dev, not Cloud Run) | No                 | False                           |
| `--gcp-credentials-dir` | Path to the folder where the GCP .json credentials file is located (optional, useful for Docker) | No | Project root `.gcpcredentials` |
| `--output-root`        | Root directory for local output (data/raw and data/processed) (optional, useful for Docker) | No | Project root |
| `--phoenix-endpoint`   | Phoenix endpoint URL for tracing                    | No                 | `http://localhost:6006/v1/traces` |
| `--phoenix-project-name`| Phoenix project name for tracing                   | No                 | `lus-laboris-processing` |
| `--phoenix-log-level`  | Phoenix logging level (DEBUG/INFO/WARNING/ERROR)   | No                 | `INFO` |
| `--skip-quality-validation` | Skip quality validation and reporting | No | False |

#### Docker Usage

The script can be run using Docker with custom Phoenix configuration:

```bash
# Build the Docker image
docker build -t lus-laboris-processing .

# Run with default Phoenix configuration
docker run --rm lus-laboris-processing

# Run with custom Phoenix endpoint
docker run --rm lus-laboris-processing --phoenix-endpoint http://host.docker.internal:6006/v1/traces

# Run with custom Phoenix project name
docker run --rm lus-laboris-processing --phoenix-project-name my-docker-project

# Run in GCS mode with custom Phoenix settings
docker run --rm -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v /path/to/credentials.json:/app/credentials.json:ro \
  lus-laboris-processing --mode gcs --bucket-name my-bucket \
  --phoenix-endpoint http://host.docker.internal:6006/v1/traces \
  --phoenix-project-name my-docker-project
```

**Note:** When using Docker, use `host.docker.internal` instead of `localhost` to connect to Phoenix running on the host machine.

#### Google Cloud Storage Configuration

To use GCS mode, you need to configure authentication:

- By default (recommended for Cloud Run), the script will use the environment's credentials (e.g., Cloud Run's default Service Account).
- If you use the `--use-local-credentials` flag, the script will look for a service account `.json` file in a `.gcpcredentials` folder at the project root and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable automatically. This is useful for local development.
- You can override the credentials folder location with the `--gcp-credentials-dir` flag (recommended for Docker).

#### Phoenix Tracing

The script includes built-in support for Phoenix/OpenTelemetry tracing to monitor execution and performance. **Tracing is always enabled** when you run the script.

> **For detailed Phoenix setup and advanced features, see the [Phoenix Guide](../../docs/phoenix_guide.md)**

**Features:**
- Automatic HTTP request instrumentation
- Custom spans for all major operations (download, parsing, saving)
- Captures metadata: file sizes, article counts, execution times, errors
- **Automatic verification**: Checks if Phoenix is reachable before processing
- **Graceful degradation**: If Phoenix is unavailable, shows a warning but continues processing (traces won't be collected)

**Configuration:**

Phoenix tracing is configured via command-line arguments with sensible defaults:

```bash
# Use default Phoenix configuration (localhost)
uv run extract_law_text.py

# Custom Phoenix endpoint
uv run extract_law_text.py --phoenix-endpoint http://localhost:6006/v1/traces

# Custom Phoenix project name
uv run extract_law_text.py --phoenix-project-name my-project

# Both custom Phoenix settings
uv run extract_law_text.py --phoenix-endpoint https://your-instance.phoenix.arize.com/v1/traces --phoenix-project-name my-project
```

**Phoenix Arguments:**

| Argument | Description | Default | Required |
|----------|-------------|---------|----------|
| `--phoenix-endpoint` | Phoenix endpoint URL for sending traces | `http://localhost:6006/v1/traces` | No |
| `--phoenix-project-name` | Phoenix project name for traces | `lus-laboris-processing` | No |

**Usage:**

1. Start Phoenix (local):
   ```bash
   cd ../../services/monitoring
   docker-compose up -d
   ```

2. Run the script normally (tracing is automatic):
   ```bash
   uv run extract_law_text.py --mode local
   ```

3. View traces at: http://localhost:6006

**Important Notes:**
- **Tracing is always active**: The script always attempts to send traces
- **Phoenix verification**: Before processing, the script checks if Phoenix is reachable
- **Warning if unavailable**: If Phoenix is not running, you'll see warnings but processing continues
- **No data loss**: If Phoenix becomes available during execution, traces will be sent

#### Separate Logging System

The script implements a separate logging system that distinguishes between main process messages and Phoenix/debug messages:

**Main Process Logs:**
```
10:30:15 [PROCESO] 🔄 Starting processing in mode: LOCAL
10:30:15 [PROCESO] 🔄 Downloading from: https://example.com/ley
10:30:16 [PROCESO] ✅ Page downloaded and saved to: data/raw/ley.html
10:30:16 [PROCESO] ✅ Law content extracted successfully
10:30:17 [PROCESO] ✅ Saved locally: data/processed/articulos.json
10:30:17 [PROCESO] 📊 Total articles: 150
10:30:17 [PROCESO] ✅ Process completed successfully!
```

**Phoenix/Debug Logs:**
```
10:30:15 [PHOENIX] Phoenix tracing initialized correctly
10:30:15 [PHOENIX] Session created: 550e8400-e29b-41d4-a716-446655440000
10:30:15 [PHOENIX] Starting Phoenix span: download_law_page (kind: CLIENT) [Session: 550e8400]
10:30:16 [PHOENIX] Ending Phoenix span: download_law_page
10:30:17 [PHOENIX] Session ended: 550e8400-e29b-41d4-a716-446655440000
```

**Log Level Control:**

```bash
# See all Phoenix logs (full debug)
uv run extract_law_text.py --phoenix-log-level DEBUG

# Only important Phoenix information (default)
uv run extract_law_text.py --phoenix-log-level INFO

# Only Phoenix warnings and errors
uv run extract_law_text.py --phoenix-log-level WARNING

# Only critical Phoenix errors
uv run extract_law_text.py --phoenix-log-level ERROR
```

**Benefits:**
- **Clear separation**: Main process vs debugging/tracing
- **Granular control**: Adjust Phoenix verbosity level
- **Professional format**: Consistent timestamps and categorization
- **Easy filtering**: Quickly identify important messages

#### Output Structure

The script generates a JSON file with the following structure:

```json
{
  "meta": {
    "numero_ley": "213",
    "fecha_promulgacion": "DD-MM-YYYY",
    "fecha_publicacion": "DD-MM-YYYY"
  },
  "articulos": [
    {
      "articulo_numero": 1,
      "libro": "libro primero",
      "libro_numero": 1,
      "titulo": "título i",
      "capitulo": "capítulo i",
      "capitulo_numero": 1,
      "capitulo_descripcion": "chapter description",
      "articulo": "article content..."
    }
  ]
}
```

#### Complete Usage Examples

```bash
# Help
uv run extract_law_text.py --help

# Local mode
uv run extract_law_text.py

# Local mode with custom output root (e.g., for Docker volume)
uv run extract_law_text.py --output-root /app

# Local mode with custom filenames
uv run extract_law_text.py --raw-filename ley.html --processed-filename salida.json

# GCS mode (Cloud Run or default credentials)
uv run extract_law_text.py --mode gcs --bucket-name my-bucket

# GCS mode with local credentials (for local development)
uv run extract_law_text.py --mode gcs --bucket-name my-bucket --use-local-credentials

# GCS mode with custom filenames
uv run extract_law_text.py --mode gcs --bucket-name my-bucket --raw-filename ley.html --processed-filename salida.json
```

#### Important Notes

- GCS mode creates temporary directories that are automatically cleaned up when finished
- For GCS mode, ensure you have write permissions to the specified bucket
- The script handles network and processing errors robustly
- Temporary files are created with the `lus_laboris_` prefix for easy identification

#### Docker Usage

You can build and run the script in a Docker container for maximum portability. See [docker_guide.md](../../docs/docker_guide.md) for more details.

**Build the image:**
```bash
docker build -t labor-law-extractor .
```

**Docker Usage - Local Mode**

You can also run the script in local mode and persist output to a mounted volume:

```bash
# Get the absolute path to the data folder
DATA_DIR=$(realpath ../../data)

docker run --rm \
  -v "${DATA_DIR}:/app/data" \
  labor-law-extractor \
  uv run extract_law_text.py --output-root /app
```

This will save all output in your local 'data' folder.

**Docker Usage - GCS Mode (mounting credentials):**

```bash
# Get the absolute path to the GCP credentials folder
GCP_CREDS=$(realpath ../../.gcpcredentials)

docker run --rm \
  -v "${GCP_CREDS}:/gcpcreds:ro" \
  labor-law-extractor \
  uv run extract_law_text.py \
    --mode gcs \
    --bucket-name py-labor-law-rag-bucket \
    --use-local-credentials \
    --gcp-credentials-dir /gcpcreds
```

This allows you to run the script in GCS mode from Docker, mounting the GCP credentials securely.

#### Publish Docker Image to Docker Hub

You can upload the generated Docker image to Docker Hub manually or automatically.

##### Manual method

1. Load the environment variables from the `.env` file located at the project root (run this from the `src/processing` folder):
```bash
set -o allexport
source ../../.env
set +o allexport
```

2. Make sure you have a `.env` file at the project root with the variables:
   - `DOCKER_HUB_USERNAME`
   - `DOCKER_HUB_PASSWORD`
   - `DOCKER_IMAGE_NAME_PROCESSING`

3. Build the Docker image:
```bash
docker build -t "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:latest" .
```

4. Log in to Docker Hub:
```bash
echo "$DOCKER_HUB_PASSWORD" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin
```

5. Tag the image with the date:
```bash
DATE_TAG=$(date +%Y%m%d)
docker tag "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:latest" "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$DATE_TAG"
```

6. Push both tags:
```bash
docker push "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:latest"
docker push "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$DATE_TAG"
```

> **Note:** The script and commands generate two tags: one with `latest` and one with the current date (`YYYYMMDD`).
> **Best practice:** In production, always use the date tag (`YYYYMMDD`) to avoid running unexpected versions that may be under the `latest` tag.

For more details about Docker usage (including Compose and Hub), see the guide:
- [docker_guide.md](../../docs/docker_guide.md)

##### Automatic method (recommended)

You can use the `docker_build_push.sh` script to automate the entire process. The script looks for the `.env` file at the project root (two levels above the `processing` folder).

```bash
bash docker_build_push.sh
```

The script will validate the required variables, build the image, tag it, and push it to Docker Hub with both tags. For more information, see:
- [docker_guide.md](../../docs/docker_guide.md)

---

# Procesamiento de Texto Legal

Este directorio contiene scripts para extraer y procesar texto del Código Laboral de Paraguay.

## Scripts Disponibles

### `extract_law_text.py`

Script principal para extraer y procesar el texto del Código Laboral de Paraguay desde su fuente oficial.

#### Características

- **Dos modos de ejecución**:
  - **Local**: Guarda archivos en el sistema de archivos local
  - **GCS**: Crea carpetas temporales y sube el JSON a Google Cloud Storage

- **Funcionalidades**:
  - Descarga automática del HTML desde el sitio oficial
  - Extracción y limpieza del texto
  - Segmentación en artículos estructurados
  - Validación de calidad y reportes
  - Guardado en formato JSON
  - Trazas Phoenix/OpenTelemetry para observabilidad (siempre activo)

#### Instalación de Dependencias

- Consulta la [documentación de UV](https://github.com/astral-sh/uv) para más detalles.

```bash
# Instalar dependencias usando uv
uv sync
```

#### Uso

##### Modo Local (por defecto)

```bash
# Ejecución básica
uv run extract_law_text.py

# Personalizando nombres de archivos
uv run extract_law_text.py --raw-filename mi_ley.html --processed-filename salida.json

# Omitir validación de calidad para procesamiento más rápido
uv run extract_law_text.py --skip-quality-validation
```

- El HTML crudo se guardará en `data/raw/{raw-filename}` (por defecto: `codigo_trabajo_py.html`) en la raíz del proyecto (no en el directorio actual).
- El JSON procesado se guardará en `data/processed/{processed-filename}` (por defecto: `codigo_trabajo_articulos.json`) en la raíz del proyecto.

#### Validación de Calidad

El script valida automáticamente la calidad de los datos procesados mediante:
- **Validación de estructura**: Verifica campos requeridos y números de artículo válidos (1-413)
- **Verificación de completitud**: Asegura que los 413 artículos estén presentes sin duplicados
- **Análisis de contenido**: Analiza longitud de artículos, caracteres especiales y calidad del contenido
- **Reportes comprensivos**: Genera reportes detallados de calidad con métricas y estado

Usa `--skip-quality-validation` para deshabilitar la validación y procesar más rápido.

##### Modo Google Cloud Storage

```bash
# Ejecución básica con GCS
uv run extract_law_text.py --mode gcs --bucket-name mi-bucket

# Forzar uso de credenciales locales (para desarrollo local)
uv run extract_law_text.py --mode gcs --bucket-name mi-bucket --use-local-credentials
```

- El HTML crudo siempre se subirá a `raw/{raw-filename}` en el bucket (por defecto: `codigo_trabajo_py.html`).
- El JSON procesado siempre se subirá a `processed/{processed-filename}` en el bucket (por defecto: `codigo_trabajo_articulos.json`).

#### Argumentos de Línea de Comandos

| Argumento             | Descripción                                         | Requerido           | Por Defecto                    |
|-----------------------|-----------------------------------------------------|---------------------|-------------------------------|
| `--mode`              | Modo de ejecución: `local` o `gcs`                  | No                  | `local`                       |
| `--url`               | URL de la página de la ley                          | No                  | URL oficial                   |
| `--bucket-name`       | Nombre del bucket de GCS (modo gcs)                 | Sí (para modo gcs)  | -                             |
| `--raw-filename`      | Nombre para el archivo HTML crudo                   | No                  | `codigo_trabajo_py.html`      |
| `--processed-filename`| Nombre para el archivo JSON procesado               | No                  | `codigo_trabajo_articulos.json`|
| `--use-local-credentials`| Forzar uso de credenciales locales (para desarrollo local, no Cloud Run) | No                  | False                         |
| `--gcp-credentials-dir` | Ruta a la carpeta donde buscar el archivo .json de credenciales de GCP (opcional, util para Docker) | No | `.gcpcredentials` en la raíz |
| `--output-root`        | Raíz donde se crearán las carpetas data/raw y data/processed en modo local (opcional, útil para Docker) | No | Raíz del proyecto |
| `--skip-quality-validation` | Omitir validación de calidad y reportes | No | False |

#### Uso con Docker

El script se puede ejecutar usando Docker con configuración personalizada de Phoenix:

```bash
# Construir la imagen Docker
docker build -t lus-laboris-processing .

# Ejecutar con configuración por defecto de Phoenix
docker run --rm lus-laboris-processing

# Ejecutar con endpoint personalizado de Phoenix
docker run --rm lus-laboris-processing --phoenix-endpoint http://host.docker.internal:6006/v1/traces

# Ejecutar con nombre de proyecto personalizado de Phoenix
docker run --rm lus-laboris-processing --phoenix-project-name mi-proyecto-docker

# Ejecutar en modo GCS con configuraciones personalizadas de Phoenix
docker run --rm -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v /ruta/a/credentials.json:/app/credentials.json:ro \
  lus-laboris-processing --mode gcs --bucket-name mi-bucket \
  --phoenix-endpoint http://host.docker.internal:6006/v1/traces \
  --phoenix-project-name mi-proyecto-docker
```

**Nota:** Cuando uses Docker, usa `host.docker.internal` en lugar de `localhost` para conectarte a Phoenix ejecutándose en la máquina host.

#### Configuración para Google Cloud Storage

Para usar el modo GCS, necesitas configurar la autenticación:

- Por defecto (recomendado para Cloud Run), el script usará las credenciales del entorno (por ejemplo, la Service Account por defecto de Cloud Run).
- Si usas el flag `--use-local-credentials`, el script buscará automáticamente un archivo `.json` de cuenta de servicio en la carpeta `.gcpcredentials` en la raíz del proyecto y establecerá la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`. Esto es útil para desarrollo local.
- Puedes sobrescribir la ubicación de la carpeta de credenciales con el flag `--gcp-credentials-dir` (recomendado para Docker).

#### Trazas Phoenix

El script incluye soporte integrado para trazas Phoenix/OpenTelemetry para monitorear la ejecución y rendimiento. **El trazado siempre está activo** cuando ejecutas el script.

> **Para configuración detallada de Phoenix y características avanzadas, consulta la [Guía de Phoenix](../../docs/phoenix_guide.md)**

**Características:**
- Instrumentación automática de peticiones HTTP
- Spans personalizados para todas las operaciones principales (descarga, parsing, guardado)
- Captura de metadatos: tamaños de archivos, conteo de artículos, tiempos de ejecución, errores
- **Verificación automática**: Verifica si Phoenix es alcanzable antes del procesamiento
- **Degradación elegante**: Si Phoenix no está disponible, muestra una advertencia pero continúa el procesamiento (las trazas no se recolectarán)

**Configuración:**

El tracing de Phoenix se configura mediante argumentos de línea de comandos con valores por defecto sensatos:

```bash
# Usar configuración por defecto de Phoenix (localhost)
uv run extract_law_text.py

# Endpoint personalizado de Phoenix
uv run extract_law_text.py --phoenix-endpoint http://localhost:6006/v1/traces

# Nombre de proyecto personalizado de Phoenix
uv run extract_law_text.py --phoenix-project-name mi-proyecto

# Ambas configuraciones personalizadas de Phoenix
uv run extract_law_text.py --phoenix-endpoint https://tu-instancia.phoenix.arize.com/v1/traces --phoenix-project-name mi-proyecto
```

**Argumentos de Phoenix:**

| Argumento | Descripción | Por Defecto | Requerido |
|-----------|-------------|-------------|-----------|
| `--phoenix-endpoint` | URL del endpoint de Phoenix para enviar trazas | `http://localhost:6006/v1/traces` | No |
| `--phoenix-project-name` | Nombre del proyecto para las trazas de Phoenix | `lus-laboris-processing` | No |
| `--phoenix-log-level` | Nivel de logging de Phoenix (DEBUG/INFO/WARNING/ERROR) | `INFO` | No |

**Uso:**

1. Iniciar Phoenix (local):
   ```bash
   cd ../../services/monitoring
   docker-compose up -d
   ```

2. Ejecutar el script normalmente (el tracing es automático):
   ```bash
   uv run extract_law_text.py --mode local
   ```

3. Ver las trazas en: http://localhost:6006

**Notas Importantes:**
- **Trazado siempre activo**: El script siempre intenta enviar trazas
- **Verificación de Phoenix**: Antes del procesamiento, el script verifica si Phoenix es alcanzable
- **Advertencia si no disponible**: Si Phoenix no está ejecutándose, verás advertencias pero el procesamiento continuará
- **Sin pérdida de datos**: Si Phoenix se vuelve disponible durante la ejecución, las trazas se enviarán

#### Sistema de Logging Separado

El script implementa un sistema de logging separado que distingue entre mensajes del proceso principal y mensajes de Phoenix/debug:

**Logs del Proceso Principal:**
```
10:30:15 [PROCESO] 🔄 Iniciando procesamiento en modo: LOCAL
10:30:15 [PROCESO] 🔄 Descargando desde: https://example.com/ley
10:30:16 [PROCESO] ✅ Página descargada y guardada en: data/raw/ley.html
10:30:16 [PROCESO] ✅ Contenido de la Ley extraído exitosamente
10:30:17 [PROCESO] ✅ Guardado localmente: data/processed/articulos.json
10:30:17 [PROCESO] 📊 Artículos totales: 150
10:30:17 [PROCESO] ✅ Proceso completado exitosamente!
```

**Logs de Phoenix/Debug:**
```
10:30:15 [PHOENIX] Phoenix tracing inicializado correctamente
10:30:15 [PHOENIX] Sesión creada: 550e8400-e29b-41d4-a716-446655440000
10:30:15 [PHOENIX] Iniciando span Phoenix: download_law_page (kind: CLIENT) [Sesión: 550e8400]
10:30:16 [PHOENIX] Finalizando span Phoenix: download_law_page
10:30:17 [PHOENIX] Sesión finalizada: 550e8400-e29b-41d4-a716-446655440000
```

**Control de Nivel de Logging:**

```bash
# Ver todos los logs de Phoenix (debug completo)
uv run extract_law_text.py --phoenix-log-level DEBUG

# Solo información importante de Phoenix (por defecto)
uv run extract_law_text.py --phoenix-log-level INFO

# Solo warnings y errores de Phoenix
uv run extract_law_text.py --phoenix-log-level WARNING

# Solo errores críticos de Phoenix
uv run extract_law_text.py --phoenix-log-level ERROR
```

**Beneficios:**
- **Separación clara**: Proceso principal vs debugging/tracing
- **Control granular**: Ajustar nivel de verbosidad de Phoenix
- **Formato profesional**: Timestamps y categorización consistente
- **Fácil filtrado**: Identificar rápidamente mensajes importantes

#### Estructura de Salida

El script genera un archivo JSON con la siguiente estructura:

```json
{
  "meta": {
    "numero_ley": "213",
    "fecha_promulgacion": "DD-MM-YYYY",
    "fecha_publicacion": "DD-MM-YYYY"
  },
  "articulos": [
    {
      "articulo_numero": 1,
      "libro": "libro primero",
      "libro_numero": 1,
      "titulo": "título i",
      "capitulo": "capítulo i",
      "capitulo_numero": 1,
      "capitulo_descripcion": "descripción del capítulo",
      "articulo": "contenido del artículo..."
    }
  ]
}
```

#### Ejemplos de Uso Completos

```bash
# Ayuda
uv run extract_law_text.py --help

# Modo local
uv run extract_law_text.py

# Modo local con raíz de salida personalizada (por ejemplo, para volumen Docker)
uv run extract_law_text.py --output-root /app

# Modo local con nombres personalizados
uv run extract_law_text.py --raw-filename ley.html --processed-filename salida.json

# Modo GCS (Cloud Run o credenciales por defecto)
uv run extract_law_text.py --mode gcs --bucket-name mi-bucket

# Modo GCS con credenciales locales (para desarrollo local)
uv run extract_law_text.py --mode gcs --bucket-name mi-bucket --use-local-credentials

# Modo GCS con nombres personalizados
uv run extract_law_text.py --mode gcs --bucket-name mi-bucket --raw-filename ley.html --processed-filename salida.json
```

#### Notas Importantes

- El modo GCS crea directorios temporales que se limpian automáticamente al finalizar
- Para el modo GCS, asegúrate de tener permisos de escritura en el bucket especificado
- El script maneja errores de red y de procesamiento de manera robusta
- Los archivos temporales se crean con el prefijo `lus_laboris_` para facilitar la identificación

#### Uso con Docker

Puedes construir y ejecutar el script en un contenedor Docker para máxima portabilidad. Consulta [docker_guide.md](../../docs/docker_guide.md) para más detalles.

**Construir la imagen:**
```bash
docker build -t labor-law-extractor .
```

**Uso con Docker - Modo Local**

Puedes ejecutar el script en modo local y persistir la salida en un volumen montado:

```bash
# Obtener la ruta absoluta de la carpeta data
DATA_DIR=$(realpath ../../data)

docker run --rm \
  -v "${DATA_DIR}:/app/data" \
  labor-law-extractor \
  uv run extract_law_text.py --output-root /app
```

Esto guardará toda la salida en tu carpeta local 'data'.

**Uso con Docker - Modo GCS (montando credenciales):**

```bash
# Obtener la ruta absoluta de la carpeta de credenciales GCP
GCP_CREDS=$(realpath ../../.gcpcredentials)

docker run --rm \
  -v "${GCP_CREDS}:/gcpcreds:ro" \
  labor-law-extractor \
  uv run extract_law_text.py \
    --mode gcs \
    --bucket-name py-labor-law-rag-bucket \
    --use-local-credentials \
    --gcp-credentials-dir /gcpcreds
```

Esto permite ejecutar el script en modo GCS desde Docker, montando las credenciales de GCP de forma segura.

#### Publicar imagen en Docker Hub

Puedes subir la imagen Docker generada a Docker Hub de forma manual o automática.

##### Método manual

1. Carga las variables de entorno desde el archivo `.env` ubicado en la raíz del proyecto (ejecuta esto desde la carpeta `src/processing`):
```bash
set -o allexport
source ../../.env
set +o allexport
```

2. Asegúrate de tener un archivo `.env` en la raíz del proyecto con las variables:
   - `DOCKER_HUB_USERNAME`
   - `DOCKER_HUB_PASSWORD`
   - `DOCKER_IMAGE_NAME_PROCESSING`

3. Construye la imagen Docker:
```bash
docker build -t "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:latest" .
```

4. Inicia sesión en Docker Hub:
```bash
echo "$DOCKER_HUB_PASSWORD" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin
```

5. Etiqueta la imagen con la fecha:
```bash
DATE_TAG=$(date +%Y%m%d)
docker tag "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:latest" "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$DATE_TAG"
```

6. Sube ambas etiquetas:
```bash
docker push "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:latest"
docker push "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$DATE_TAG"
```

> **Nota:** El script y los comandos generan dos tags: uno con la palabra `latest` y otro con la fecha actual (formato `YYYYMMDD`).
> **Buena práctica:** En producción, siempre utiliza el tag de fecha (`YYYYMMDD`) para evitar ejecutar versiones inesperadas que puedan estar bajo el tag `latest`.

Para más detalles sobre el uso de Docker (incluyendo Compose y Hub), consulta la guía:
- [docker_guide.md](../../docs/docker_guide.md)

##### Método automático (recomendado)

Puedes usar el script `docker_build_push.sh` que automatiza todo el proceso. El script busca el archivo `.env` en la raíz del proyecto (dos niveles arriba de la carpeta `processing`).

```bash
bash docker_build_push.sh
```

El script validará las variables necesarias, construirá la imagen, la etiquetará y la subirá a Docker Hub con los tags correspondientes. Para más información, revisa:
- [docker_guide.md](../../docs/docker_guide.md)