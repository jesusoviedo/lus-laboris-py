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

#### Google Cloud Storage Configuration

To use GCS mode, you need to configure authentication:

- By default (recommended for Cloud Run), the script will use the environment's credentials (e.g., Cloud Run's default Service Account).
- If you use the `--use-local-credentials` flag, the script will look for a service account `.json` file in a `.gcpcredentials` folder at the project root and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable automatically. This is useful for local development.

```bash
# Option 1: Use Application Default Credentials
gcloud auth application-default login

# Option 2: Use a service account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

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

#### Configuración para Google Cloud Storage

Para usar el modo GCS, necesitas configurar la autenticación:

- Por defecto (recomendado para Cloud Run), el script usará las credenciales del entorno (por ejemplo, la Service Account por defecto de Cloud Run).
- Si usas el flag `--use-local-credentials`, el script buscará automáticamente un archivo `.json` de cuenta de servicio en la carpeta `.gcpcredentials` en la raíz del proyecto y establecerá la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`. Esto es útil para desarrollo local.

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