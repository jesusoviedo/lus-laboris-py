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

```bash
# Install dependencies using uv
# See UV Guide for detailed commands: ../../docs/uv_guide.md
uv sync

# Or using pip
pip install -r requirements.txt
```

#### Usage

##### Local Mode (default)

```bash
# Basic execution
python src/processing/extract_law_text.py

# With custom directory
python src/processing/extract_law_text.py --mode local --output-dir /path/to/output

# With custom URL
python src/processing/extract_law_text.py --url "https://other-url.com"
```

##### Google Cloud Storage Mode

```bash
# Basic GCS execution
python src/processing/extract_law_text.py --mode gcs --bucket-name my-bucket

# With custom filename
python src/processing/extract_law_text.py --mode gcs --bucket-name my-bucket --blob-name labor_code.json

# With custom URL
python src/processing/extract_law_text.py --mode gcs --bucket-name my-bucket --url "https://other-url.com"
```

#### Command Line Arguments

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| `--mode` | Execution mode: `local` or `gcs` | No | `local` |
| `--url` | Law page URL | No | Official Labor Code URL |
| `--output-dir` | Output directory (local mode) | No | `data/processed` |
| `--bucket-name` | GCS bucket name (gcs mode) | Yes (for gcs mode) | - |
| `--blob-name` | GCS filename | No | `codigo_trabajo_articulos.json` |

#### Google Cloud Storage Configuration

To use GCS mode, you need to configure authentication:

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
python src/processing/extract_law_text.py --help

# Local mode with custom configuration
python src/processing/extract_law_text.py \
  --mode local \
  --output-dir /home/user/data \
  --url "https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo"

# GCS mode with custom configuration
python src/processing/extract_law_text.py \
  --mode gcs \
  --bucket-name my-legal-bucket \
  --blob-name paraguay_labor_code.json \
  --url "https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo"
```

#### Important Notes

- GCS mode creates temporary directories that are automatically cleaned up when finished
- For GCS mode, ensure you have write permissions to the specified bucket
- The script handles network and processing errors robustly
- Temporary files are created with the `lus_laboris_` prefix for easy identification

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#legal-text-processing) | [🇪🇸 Español](#legal-text-processing-1)

</div>

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

```bash
# Instalar dependencias usando uv
# Ver Guía de UV para comandos detallados: ../../docs/uv_guide.md
uv sync

# O usando pip
pip install -r requirements.txt
```

#### Uso

##### Modo Local (por defecto)

```bash
# Ejecución básica
python src/processing/extract_law_text.py

# Con directorio personalizado
python src/processing/extract_law_text.py --mode local --output-dir /path/to/output

# Con URL personalizada
python src/processing/extract_law_text.py --url "https://otra-url.com"
```

##### Modo Google Cloud Storage

```bash
# Ejecución básica con GCS
python src/processing/extract_law_text.py --mode gcs --bucket-name mi-bucket

# Con nombre de archivo personalizado
python src/processing/extract_law_text.py --mode gcs --bucket-name mi-bucket --blob-name codigo_trabajo.json

# Con URL personalizada
python src/processing/extract_law_text.py --mode gcs --bucket-name mi-bucket --url "https://otra-url.com"
```

#### Argumentos de Línea de Comandos

| Argumento | Descripción | Requerido | Por Defecto |
|-----------|-------------|-----------|-------------|
| `--mode` | Modo de ejecución: `local` o `gcs` | No | `local` |
| `--url` | URL de la página de la ley | No | URL oficial del Código Laboral |
| `--output-dir` | Directorio de salida (modo local) | No | `data/processed` |
| `--bucket-name` | Nombre del bucket de GCS (modo gcs) | Sí (para modo gcs) | - |
| `--blob-name` | Nombre del archivo en GCS | No | `codigo_trabajo_articulos.json` |

#### Configuración para Google Cloud Storage

Para usar el modo GCS, necesitas configurar la autenticación:

```bash
# Opción 1: Usar Application Default Credentials
gcloud auth application-default login

# Opción 2: Usar una cuenta de servicio
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

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
python src/processing/extract_law_text.py --help

# Modo local con configuración personalizada
python src/processing/extract_law_text.py \
  --mode local \
  --output-dir /home/user/datos \
  --url "https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo"

# Modo GCS con configuración personalizada
python src/processing/extract_law_text.py \
  --mode gcs \
  --bucket-name mi-bucket-legal \
  --blob-name codigo_trabajo_paraguay.json \
  --url "https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo"
```

#### Notas Importantes

- El modo GCS crea directorios temporales que se limpian automáticamente al finalizar
- Para el modo GCS, asegúrate de tener permisos de escritura en el bucket especificado
- El script maneja errores de red y de procesamiento de manera robusta
- Los archivos temporales se crean con el prefijo `lus_laboris_` para facilitar la identificación