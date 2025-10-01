#!/usr/bin/env python3
"""
Script to extract and process the text of Paraguay's Labor Code.

This script automates the process of:
1. Downloading the HTML of the law from the official site
2. Extracting and cleaning the text
3. Segmenting into structured articles
4. Saving in JSON format (local or Google Cloud Storage)

Execution modes:
- Local: Saves files to local filesystem
- GCS: Creates temporary folders and uploads JSON to Google Cloud Storage

Based on notebook: notebooks/01_extract_law_text.ipynb
"""

import re
import json
import os
import tempfile
import argparse
import requests
from pathlib import Path
from ftfy import fix_text
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from google.cloud import storage
import glob
import warnings
from phoenix.otel import register
from opentelemetry.instrumentation.requests import RequestsInstrumentor


# Patterns to identify headers and articles
HEADER_PATTERNS = {
    'libro': re.compile(r"^LIBRO\s+([A-ZÁÉÍÓÚÑ]+)\s*$", re.IGNORECASE),
    'titulo': re.compile(r"^TITULO\s+([A-ZÁÉÍÓÚÑ]+)\s*$", re.IGNORECASE),
    'capitulo': re.compile(r"^CAPITULO\s+([IVXLCDM]+)\s*$", re.IGNORECASE),
}

ARTICULO_PATTERN = re.compile(r"^Art[íi]?t?culo\s+(\d+)\s*(?:[°º])?\s*\.?\s*-\s*$", re.IGNORECASE)

ROMAN_MAP = {
    'PRIMERO': 1, 'SEGUNDO': 2, 'TERCERO': 3, 'CUARTO': 4, 'QUINTO': 5,
    'SEXTO': 6, 'SÉPTIMO': 7, 'SEPTIMO': 7, 'OCTAVO': 8, 'NOVENO': 9,
    'DÉCIMO': 10, 'DECIMO': 10, 'UNDÉCIMO': 11, 'UNDECIMO': 11, 'DUODÉCIMO': 12, 'DUODECIMO': 12,
}

_ROMAN_VALUES = {"I":1,"V":5,"X":10,"L":50,"C":100,"D":500,"M":1000}

# Global tracer instance
_tracer = None
_tracing_enabled = False


def check_phoenix_availability(endpoint: str, timeout: int = 2) -> bool:
    """
    Checks if the Phoenix endpoint is available.
    
    Args:
        endpoint: Phoenix endpoint URL
        timeout: Timeout in seconds
        
    Returns:
        bool: True if Phoenix is available, False otherwise
    """
    try:
        # Extract base URL (without /v1/traces)
        base_url = endpoint.replace('/v1/traces', '').replace('/v1/spans', '')
        
        # Try to connect to endpoint
        response = requests.head(base_url, timeout=timeout)
        return response.status_code < 500
    except (requests.RequestException, Exception):
        return False


def setup_phoenix_tracing(phoenix_endpoint: str = None, project_name: str = None) -> bool:
    """
    Configures Phoenix/OpenTelemetry instrumentation using the official method.
    
    Args:
        phoenix_endpoint: Phoenix endpoint URL (default: http://localhost:6006/v1/traces)
        project_name: Phoenix project name (default: lus-laboris-processing)
    
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    global _tracer, _tracing_enabled
    
    try:
        # Use provided values or defaults
        phoenix_endpoint = phoenix_endpoint or 'http://localhost:6006/v1/traces'
        project_name = project_name or 'lus-laboris-processing'
        
        # Check Phoenix availability
        if not check_phoenix_availability(phoenix_endpoint):
            print(f"[WARNING] Phoenix endpoint is not reachable: {phoenix_endpoint}")
            print(f"[WARNING] Tracing is enabled but spans may not be collected.")
            print(f"[WARNING] Make sure Phoenix is running: cd services/monitoring && docker-compose up -d")
        
        # Configure Phoenix using official method
        tracer_provider = register(protocol="http/protobuf", project_name=project_name)
        _tracer = tracer_provider.get_tracer(__name__)
        
        # Auto-instrument requests to capture HTTP calls
        RequestsInstrumentor().instrument()
        
        _tracing_enabled = True
        print(f"[INFO] Phoenix tracing configured: {phoenix_endpoint}")
        return True
        
    except Exception as e:
        warnings.warn(f"Failed to setup Phoenix tracing: {e}. Continuing without tracing.")
        _tracing_enabled = False
        return False


def get_tracer():
    """Returns the global tracer or None if tracing is disabled."""
    return _tracer if _tracing_enabled else None


def get_phoenix_tracer():
    """Gets the Phoenix tracer for use with official decorators."""
    tracer = get_tracer()
    if not tracer or not _tracing_enabled:
        return None
    return tracer


# Decorator that will be initialized after configuring Phoenix
chain_decorator = None

def initialize_phoenix_decorator():
    """Initializes the official Phoenix decorator."""
    global chain_decorator
    phoenix_tracer = get_phoenix_tracer()
    if phoenix_tracer:
        # Use official Phoenix decorator for processing functions
        chain_decorator = phoenix_tracer.chain
        print("[INFO] Usando decorador oficial de Phoenix (@tracer.chain)")
    else:
        # Fallback: decorator that does nothing if Phoenix is not available
        def chain_decorator(func):
            return func
        print("[INFO] Phoenix no disponible, usando decorador de fallback")


def roman_to_int(roman: str) -> int:
    """Converts a Roman numeral to integer."""
    roman = roman.strip().upper()
    total = 0
    prev = 0
    for ch in reversed(roman):
        val = _ROMAN_VALUES.get(ch, 0)
        if val < prev:
            total -= val
        else:
            total += val
            prev = val
    return total


@chain_decorator
def download_law_page(url: str, output_path: str = "data/raw/codigo_trabajo_py.html") -> None:
    """
    Downloads the HTML page of the law and saves it locally.
    
    Args:
        url: URL of the law page
        output_path: Path where to save the HTML file
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Descargando desde: {url}")
    response = requests.get(url)
    response.raise_for_status()
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"Página descargada y guardada en: {out_path}")


@chain_decorator
def extract_metadata(lines: List[str]) -> Dict[str, Any]:
    """Extracts law number and dates from the header."""
    meta = {}

    encabezado = []
    for ln in lines:
        if re.match(r"CAP[IÍ]TULO\s+I\b", ln, re.IGNORECASE):
            break
        encabezado.append(ln)

    encabezado_text = " ".join(encabezado)

    ley_match = re.search(r"LEY\s*N[°º]?\s*(\d+)", encabezado_text, re.IGNORECASE)
    if ley_match:
        meta["numero_ley"] = ley_match.group(1)

    promulg_match = re.search(r"Fecha\s+de\s+Promulgaci[oó]n:?\s*(\d{2}-\d{2}-\d{4})", encabezado_text, re.IGNORECASE)
    if promulg_match:
        meta["fecha_promulgacion"] = promulg_match.group(1)

    public_match = re.search(r"Fecha\s+de\s+Publicaci[oó]n:?\s*(\d{2}-\d{2}-\d{4})", encabezado_text, re.IGNORECASE)
    if public_match:
        meta["fecha_publicacion"] = public_match.group(1)

    return meta


@chain_decorator
def extract_articles(lines: List[str]) -> List[Dict[str, Any]]:
    """Segments books, titles, chapters and articles in detail."""
    # Header context
    current_libro = None
    current_libro_num = None
    current_titulo = None
    current_capitulo = None
    current_capitulo_num = None
    current_capitulo_desc = None

    # Article segmentation
    articles = []
    current_article_num = None
    current_article_lines = []

    def flush_article():
        if current_article_num is None:
            return
        body = "\n".join(current_article_lines).strip()
        articles.append({
            'articulo_numero': int(current_article_num),
            'libro': current_libro.lower() if current_libro else None,
            'libro_numero': current_libro_num,
            'titulo': current_titulo.lower() if current_titulo else None,
            'capitulo': current_capitulo.lower() if current_capitulo else None,
            'capitulo_numero': current_capitulo_num,
            'capitulo_descripcion': current_capitulo_desc.lower() if current_capitulo_desc else None,
            'articulo': body.lower().replace('\n', ''),
        })

    i = 0
    while i < len(lines):
        ln = lines[i]

        # Detect BOOK
        m_lib = HEADER_PATTERNS['libro'].match(ln)
        if m_lib:
            current_libro = f"LIBRO {m_lib.group(1).title()}"
            current_libro_num = ROMAN_MAP.get(m_lib.group(1).upper())
            i += 1
            continue

        # Detect TITLE
        m_tit = HEADER_PATTERNS['titulo'].match(ln)
        if m_tit:
            current_titulo = f"TITULO {m_tit.group(1).title()}"
            i += 1
            continue

        # Detect CHAPTER
        m_cap = HEADER_PATTERNS['capitulo'].match(ln)
        if m_cap:
            roman = m_cap.group(1)
            current_capitulo = f"CAPITULO {roman}"
            current_capitulo_num = roman_to_int(roman)
            next_desc = None
            if i + 1 < len(lines):
                nxt = lines[i + 1]
                if not (HEADER_PATTERNS['libro'].match(nxt) or HEADER_PATTERNS['titulo'].match(nxt) or HEADER_PATTERNS['capitulo'].match(nxt) or ARTICULO_PATTERN.match(nxt)):
                    next_desc = nxt
            current_capitulo_desc = next_desc
            i += 2 if next_desc else 1
            continue

        # Detect article start
        m_art = ARTICULO_PATTERN.match(ln)
        if m_art:
            flush_article()
            current_article_num = m_art.group(1)
            current_article_lines = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if (HEADER_PATTERNS['libro'].match(nxt) or HEADER_PATTERNS['titulo'].match(nxt) or
                    HEADER_PATTERNS['capitulo'].match(nxt) or ARTICULO_PATTERN.match(nxt)):
                    break
                current_article_lines.append(nxt)
                i += 1
            continue

        i += 1

    flush_article()
    return articles


@chain_decorator
def parse_law_text(raw_text: str) -> Dict[str, Any]:
    """Parses the complete text into metadata and articles."""
    text = fix_text(raw_text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    
    meta = extract_metadata(lines)
    articles = extract_articles(lines)

    return {
        'meta': meta,
        'articulos': articles,
    }


@chain_decorator
def save_parsed_json_local(parsed: Dict[str, Any], processed_filename: str = "codigo_trabajo_articulos.json", output_root: str = None) -> str:
    """Saves parsed data to a local JSON file in data/processed/ (project root or specified one)"""
    if output_root:
        project_root = Path(output_root)
    else:
        project_root = Path(__file__).resolve().parent.parent.parent
    out_dir = project_root / "data/processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / processed_filename
    
    articles_count = len(parsed.get('articulos', []))
    
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    
    print(f"Guardado localmente: {out_path}")
    print(f"Artículos totales: {articles_count}")
    return str(out_path)


@chain_decorator
def save_parsed_json_gcs(parsed: Dict[str, Any], bucket_name: str, processed_filename: str = "codigo_trabajo_articulos.json") -> str:
    """Saves parsed data to a JSON file in GCS at processed/codigo_trabajo_articulos.json"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"processed/{processed_filename}")
    json_str = json.dumps(parsed, ensure_ascii=False, indent=2)
    
    articles_count = len(parsed.get('articulos', []))
    
    blob.upload_from_string(json_str, content_type='application/json')
    gcs_path = f"gs://{bucket_name}/processed/{processed_filename}"
    
    print(f"Guardado en GCS: {gcs_path}")
    print(f"Artículos totales: {articles_count}")
    return gcs_path


@chain_decorator
def upload_file_to_gcs(file_path: str, bucket_name: str, raw_filename: str = "codigo_trabajo_py.html") -> str:
    """Uploads raw HTML to GCS at raw/codigo_trabajo_py.html"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"raw/{raw_filename}")
    blob.upload_from_filename(file_path, content_type='text/html; charset=utf-8')
    gcs_path = f"gs://{bucket_name}/raw/{raw_filename}"
    
    print(f"Archivo subido a GCS: {gcs_path}")
    return gcs_path


def create_temp_directories() -> tuple[Path, Path]:
    """Creates temporary directories for processing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="lus_laboris_"))
    raw_dir = temp_dir / "raw"
    processed_dir = temp_dir / "processed"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Directorios temporales creados en: {temp_dir}")
    return raw_dir, processed_dir


def cleanup_temp_directories(temp_dir: Path) -> None:
    """Cleans up temporary directories."""
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print(f"Directorio temporal limpiado: {temp_dir}")
    except Exception as e:
        print(f"Advertencia: No se pudo limpiar el directorio temporal {temp_dir}: {e}")


def set_gcp_credentials(gcp_credentials_dir: str = None):
    """Searches for a .json file in the specified folder or in .gcpcredentials two levels up and sets GOOGLE_APPLICATION_CREDENTIALS if it exists."""
    from pathlib import Path
    import os
    if gcp_credentials_dir:
        cred_dir = Path(gcp_credentials_dir)
    else:
        project_root = Path(__file__).resolve().parent.parent.parent
        cred_dir = project_root / '.gcpcredentials'
    json_files = list(cred_dir.glob('*.json'))
    if json_files:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(json_files[0])
        print(f"Usando credenciales de servicio: {json_files[0]}")


@chain_decorator
def process_law_local(url: str, raw_filename: str = "codigo_trabajo_py.html", processed_filename: str = "codigo_trabajo_articulos.json", output_root: str = None) -> str:
    """Processes the law in local mode, saving files in data/raw and data/processed in the project root or specified one"""
    print("=== MODO LOCAL ===")
    if output_root:
        project_root = Path(output_root)
    else:
        project_root = Path(__file__).resolve().parent.parent.parent
    raw_path = project_root / "data/raw" / raw_filename
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    download_law_page(url, str(raw_path))
    try:
        texto_limpio = extract_text_from_html(str(raw_path))
    except ValueError as e:
        print(f"Error: {e}")
        raise
    parsed = parse_law_text(texto_limpio)
    output_path = save_parsed_json_local(parsed, processed_filename, output_root=output_root)
    
    return output_path


@chain_decorator
def process_law_gcs(url: str, bucket_name: str, raw_filename: str = "codigo_trabajo_py.html", processed_filename: str = "codigo_trabajo_articulos.json", use_local_credentials: bool = False, gcp_credentials_dir: str = None) -> str:
    """Processes the law in GCS mode, uploading files to raw/ and processed/ in the bucket"""
    print("=== MODO GOOGLE CLOUD STORAGE ===")
    if use_local_credentials:
        set_gcp_credentials(gcp_credentials_dir)
    raw_dir, processed_dir = create_temp_directories()
    temp_dir = raw_dir.parent
    try:
        html_path = raw_dir / raw_filename
        download_law_page(url, str(html_path))
        # Always upload raw HTML
        try:
            upload_file_to_gcs(str(html_path), bucket_name, raw_filename)
        except Exception as e:
            print(f"Advertencia: No se pudo subir el HTML crudo a GCS: {e}")
        try:
            texto_limpio = extract_text_from_html(str(html_path))
        except ValueError as e:
            print(f"Error: {e}")
            raise
        parsed = parse_law_text(texto_limpio)
        # Always upload processed JSON
        gcs_path = save_parsed_json_gcs(parsed, bucket_name, processed_filename)
        
        return gcs_path
    finally:
        cleanup_temp_directories(temp_dir)


@chain_decorator
def extract_text_from_html(html_path: str) -> str:
    """
    Extracts clean text from the law's HTML file.
    
    Args:
        html_path: Path to the HTML file
        
    Returns:
        Clean text extracted from HTML
        
    Raises:
        ValueError: If the content container cannot be found
    """
    with open(html_path, 'r', encoding='latin-1') as archivo:
        contenido_html = archivo.read()
    
    # Parse HTML
    soup = BeautifulSoup(contenido_html, 'html.parser')
    contenido_ley = soup.find('div', class_='entry-content')
    
    if not contenido_ley:
        raise ValueError("No se pudo encontrar el contenedor del contenido de la ley.")
    
    # Extract clean text
    texto_limpio = contenido_ley.get_text(separator='\n', strip=True)
    
    print("--- Contenido de la Ley extraído exitosamente ---")
    
    return texto_limpio


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extracts and processes the text of Paraguay's Labor Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Usage examples:
        # Local mode (default)
        python extract_law_text.py
        # GCS mode
        python extract_law_text.py --mode gcs --bucket-name mi-bucket
        # Customizing file names
        python extract_law_text.py --raw-filename ley.html --processed-filename salida.json
        # Force use of local credentials (local development)
        python extract_law_text.py --mode gcs --bucket-name mi-bucket --use-local-credentials
        # Specify credentials folder
        python extract_law_text.py --mode gcs --bucket-name mi-bucket --use-local-credentials --gcp-credentials-dir /ruta/a/credenciales
        # Change local output root
        python extract_law_text.py --output-root /ruta/deseada
        # Custom Phoenix configuration
        python extract_law_text.py --phoenix-endpoint http://localhost:6006/v1/traces --phoenix-project-name mi-proyecto
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['local', 'gcs'], 
        default='local', 
        help='Execution mode: local (local files) or gcs (Google Cloud Storage)')
    
    parser.add_argument(
        '--url', 
        default='https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo', 
        help='URL of the law page')
    
    parser.add_argument(
        '--bucket-name', 
        help='GCS bucket name (required for gcs mode)')
    
    parser.add_argument(
        '--raw-filename', 
        default='codigo_trabajo_py.html', 
        help='Raw HTML filename (default: codigo_trabajo_py.html)')
    
    parser.add_argument(
        '--processed-filename', 
        default='codigo_trabajo_articulos.json', 
        help='Processed JSON filename (default: codigo_trabajo_articulos.json)')
    
    parser.add_argument(
        '--use-local-credentials', 
        action='store_true', 
        help='Force use of credentials from local file (for local development).')

    parser.add_argument(
        '--gcp-credentials-dir', 
        default=None, 
        help='Path to folder where to search for GCP .json credential file (optional, defaults to project root).')
    
    parser.add_argument(
        '--output-root', 
        default=None, 
        help='Root where data/raw and data/processed folders will be created in local mode (optional).')
    
    parser.add_argument(
        '--phoenix-endpoint',
        default=None,
        help='Phoenix endpoint URL for tracing (default: http://localhost:6006/v1/traces)')
    
    parser.add_argument(
        '--phoenix-project-name',
        default=None,
        help='Phoenix project name for tracing (default: lus-laboris-processing)')
        
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    
    # Initialize Phoenix tracing (doesn't fail if not available)
    setup_phoenix_tracing(args.phoenix_endpoint, args.phoenix_project_name)
    
    # Initialize official Phoenix decorator
    initialize_phoenix_decorator()
    
    print(f"Iniciando procesamiento en modo: {args.mode.upper()}")
    print(f"URL: {args.url}")
    
    try:
        if args.mode == 'local':
            output_path = process_law_local(args.url, args.raw_filename, args.processed_filename, output_root=args.output_root)
            print(f"\n[SUCCESS] Proceso completado exitosamente!")
            print(f"[INFO] Archivo guardado en: {output_path}")
        elif args.mode == 'gcs':
            if not args.bucket_name:
                print("[ERROR] --bucket-name es requerido para el modo GCS")
                return 1
            gcs_path = process_law_gcs(
                args.url,
                args.bucket_name,
                raw_filename=args.raw_filename,
                processed_filename=args.processed_filename,
                use_local_credentials=args.use_local_credentials,
                gcp_credentials_dir=args.gcp_credentials_dir,
            )
            print(f"\n[SUCCESS] Proceso completado exitosamente!")
            print(f"[INFO] Archivo guardado en GCS: {gcs_path}")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error durante el procesamiento: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
