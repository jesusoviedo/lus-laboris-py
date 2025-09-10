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
  - JSON format saving

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
```

- The raw HTML will be saved to `data/raw/{raw-filename}` (default: `codigo_trabajo_py.html`) in the project root (not the current directory).
- The processed JSON will be saved to `data/processed/{processed-filename}` (default: `codigo_trabajo_articulos.json`) in the project root.

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
|----------------------|-----------------------------------------------------|--------------------|---------------------------------|
| `--mode`             | Execution mode: `local` or `gcs`                    | No                 | `local`                         |
| `--url`              | Law page URL                                        | No                 | Official URL                    |
| `--bucket-name`      | GCS bucket name (gcs mode)                          | Yes (for gcs mode) | -                               |
| `--raw-filename`     | Name for raw HTML file                              | No                 | `codigo_trabajo_py.html`        |
| `--processed-filename`| Name for processed JSON file                        | No                 | `codigo_trabajo_articulos.json` |
| `--use-local-credentials`| Force use of local credentials file (for local dev, not Cloud Run) | No                 | False                           |
| `--gcp-credentials-dir` | Path to the folder where the GCP .json credentials file is located (optional, useful for Docker) | No | Project root `.gcpcredentials` |
| `--output-root`        | Root directory for local output (data/raw and data/processed) (optional, useful for Docker) | No | Project root |

#### Google Cloud Storage Configuration

To use GCS mode, you need to configure authentication:

- By default (recommended for Cloud Run), the script will use the environment's credentials (e.g., Cloud Run's default Service Account).
- If you use the `--use-local-credentials` flag, the script will look for a service account `.json` file in a `.gcpcredentials` folder at the project root and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable automatically. This is useful for local development.
- You can override the credentials folder location with the `--gcp-credentials-dir` flag (recommended for Docker).

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
      "texto": "article content..."
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
   - `IMAGE_NAME_PROCESSING`

3. Build the Docker image:
```bash
docker build -t "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:latest" .
```

4. Log in to Docker Hub:
```bash
echo "$DOCKER_HUB_PASSWORD" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin
```

5. Tag the image with the date:
```bash
DATE_TAG=$(date +%Y%m%d)
docker tag "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:latest" "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$DATE_TAG"
```

6. Push both tags:
```bash
docker push "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:latest"
docker push "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$DATE_TAG"
```

> **Note:** The script and commands generate two tags: one with `latest` and one with the current date (`YYYYMMDD`).
> **Best practice:** In production, always use the date tag (`YYYYMMDD`) to avoid running unexpected versions that may be under the `latest` tag.

For more details about Docker and Docker Hub usage, see the guides:
- [docker_guide.md](../../docs/docker_guide.md)
- [docker_hub_guide.md](../../docs/docker_hub_guide.md)

##### Automatic method (recommended)

You can use the `docker_build_push.sh` script to automate the entire process. The script looks for the `.env` file at the project root (two levels above the `processing` folder).

```bash
bash docker_build_push.sh
```

The script will validate the required variables, build the image, tag it, and push it to Docker Hub with both tags.

> **Note:** The script also generates both `latest` and date tags. Use the date tag for safer production deployments.

For more information about scripts and automation, also see:
- [docker_build_push.sh](./docker_build_push.sh)
- [docker_guide.md](../../docs/docker_guide.md)
- [docker_hub_guide.md](../../docs/docker_hub_guide.md)

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
  - Guardado en formato JSON

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
```

- El HTML crudo se guardará en `data/raw/{raw-filename}` (por defecto: `codigo_trabajo_py.html`) en la raíz del proyecto (no en el directorio actual).
- El JSON procesado se guardará en `data/processed/{processed-filename}` (por defecto: `codigo_trabajo_articulos.json`) en la raíz del proyecto.

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

#### Configuración para Google Cloud Storage

Para usar el modo GCS, necesitas configurar la autenticación:

- Por defecto (recomendado para Cloud Run), el script usará las credenciales del entorno (por ejemplo, la Service Account por defecto de Cloud Run).
- Si usas el flag `--use-local-credentials`, el script buscará automáticamente un archivo `.json` de cuenta de servicio en la carpeta `.gcpcredentials` en la raíz del proyecto y establecerá la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`. Esto es útil para desarrollo local.
- Puedes sobrescribir la ubicación de la carpeta de credenciales con el flag `--gcp-credentials-dir` (recomendado para Docker).

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
      "texto": "contenido del artículo..."
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
   - `IMAGE_NAME_PROCESSING`

3. Construye la imagen Docker:
```bash
docker build -t "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:latest" .
```

4. Inicia sesión en Docker Hub:
```bash
echo "$DOCKER_HUB_PASSWORD" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin
```

5. Etiqueta la imagen con la fecha:
```bash
DATE_TAG=$(date +%Y%m%d)
docker tag "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:latest" "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$DATE_TAG"
```

6. Sube ambas etiquetas:
```bash
docker push "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:latest"
docker push "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$DATE_TAG"
```

> **Nota:** El script y los comandos generan dos tags: uno con la palabra `latest` y otro con la fecha actual (formato `YYYYMMDD`).
> **Buena práctica:** En producción, siempre utiliza el tag de fecha (`YYYYMMDD`) para evitar ejecutar versiones inesperadas que puedan estar bajo el tag `latest`.

Para más detalles sobre el uso de Docker y Docker Hub, consulta los manuales:
- [docker_guide.md](../../docs/docker_guide.md)
- [docker_hub_guide.md](../../docs/docker_hub_guide.md)

##### Método automático (recomendado)

Puedes usar el script `docker_build_push.sh` que automatiza todo el proceso. El script busca el archivo `.env` en la raíz del proyecto (dos niveles arriba de la carpeta `processing`).

```bash
bash docker_build_push.sh
```

El script validará las variables necesarias, construirá la imagen, la etiquetará y la subirá a Docker Hub con los tags correspondientes.

> **Nota:** El script también genera los tags `latest` y de fecha. Usa el tag de fecha para mayor seguridad en producción.

Para más información sobre scripts y automatización, revisa también:
- [docker_build_push.sh](./docker_build_push.sh)
- [docker_guide.md](../../docs/docker_guide.md)
- [docker_hub_guide.md](../../docs/docker_hub_guide.md)