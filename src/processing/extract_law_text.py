#!/usr/bin/env python3
"""
Script para extraer y procesar el texto del Código Laboral de Paraguay.

Este script automatiza el proceso de:
1. Descarga del HTML de la ley desde el sitio oficial
2. Extracción y limpieza del texto
3. Segmentación en artículos estructurados
4. Guardado en formato JSON (local o en Google Cloud Storage)

Modos de ejecución:
- Local: Guarda archivos en el sistema de archivos local
- GCS: Crea carpetas temporales y sube el JSON a Google Cloud Storage

Basado en el notebook: notebooks/01_extract_law_text.ipynb
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

# Phoenix/OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource


# Patrones para identificar encabezados y articulos
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
    Verifica si el endpoint de Phoenix está disponible.
    
    Args:
        endpoint: URL del endpoint de Phoenix
        timeout: Tiempo de espera en segundos
        
    Returns:
        bool: True si Phoenix está disponible, False en caso contrario
    """
    try:
        # Extraer la URL base (sin /v1/traces)
        base_url = endpoint.replace('/v1/traces', '').replace('/v1/spans', '')
        
        # Intentar conectar al endpoint
        response = requests.head(base_url, timeout=timeout)
        return response.status_code < 500
    except (requests.RequestException, Exception):
        return False


def setup_phoenix_tracing() -> bool:
    """
    Configura la instrumentación de Phoenix/OpenTelemetry.
    
    Returns:
        bool: True si la configuración fue exitosa, False en caso contrario
    """
    global _tracer, _tracing_enabled
    
    try:
        # Obtener endpoint de Phoenix desde variables de entorno
        phoenix_endpoint = os.getenv('PHOENIX_COLLECTOR_ENDPOINT', 'http://localhost:6006/v1/traces')
        
        # Verificar disponibilidad de Phoenix
        if not check_phoenix_availability(phoenix_endpoint):
            print(f"[WARNING] Phoenix endpoint is not reachable: {phoenix_endpoint}")
            print(f"[WARNING] Tracing is enabled but spans may not be collected.")
            print(f"[WARNING] Make sure Phoenix is running: cd services/monitoring && docker-compose up -d")
        
        # Configurar recurso con información del servicio
        resource = Resource.create({
            "service.name": "lus-laboris-processing",
            "service.version": "0.1.0",
        })
        
        # Configurar el proveedor de trazas
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        # Configurar el exportador OTLP hacia Phoenix
        otlp_exporter = OTLPSpanExporter(endpoint=phoenix_endpoint)
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        # Auto-instrumentar requests para capturar llamadas HTTP
        RequestsInstrumentor().instrument()
        
        # Obtener tracer para spans personalizados
        _tracer = trace.get_tracer(__name__)
        _tracing_enabled = True
        
        print(f"[INFO] Phoenix tracing configured: {phoenix_endpoint}")
        return True
        
    except Exception as e:
        warnings.warn(f"Failed to setup Phoenix tracing: {e}. Continuing without tracing.")
        _tracing_enabled = False
        return False


def get_tracer():
    """Retorna el tracer global o None si tracing está deshabilitado."""
    return _tracer if _tracing_enabled else None


class TraceSpan:
    """Context manager para crear spans de forma segura."""
    
    def __init__(self, name: str, attributes: dict = None):
        self.name = name
        self.attributes = attributes or {}
        self.span = None
        
    def __enter__(self):
        tracer = get_tracer()
        if tracer:
            try:
                self.span = tracer.start_as_current_span(self.name)
                self.span.__enter__()
                for key, value in self.attributes.items():
                    self.span.set_attribute(key, value)
            except Exception as e:
                warnings.warn(f"Failed to start span '{self.name}': {e}")
                self.span = None
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            try:
                if exc_type:
                    self.span.set_attribute("error", True)
                    self.span.set_attribute("error.type", exc_type.__name__)
                    self.span.set_attribute("error.message", str(exc_val))
                self.span.__exit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                warnings.warn(f"Failed to end span '{self.name}': {e}")
        return False
    
    def set_attribute(self, key: str, value):
        """Set attribute on the span if available."""
        if self.span:
            try:
                self.span.set_attribute(key, value)
            except Exception:
                pass


def roman_to_int(roman: str) -> int:
    """Convierte un número romano a entero."""
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


def download_law_page(url: str, output_path: str = "data/raw/codigo_trabajo_py.html") -> None:
    """
    Descarga la página HTML de la ley y la guarda localmente.
    
    Args:
        url: URL de la página de la ley
        output_path: Ruta donde guardar el archivo HTML
    """
    with TraceSpan("download_law_page", {"url": url, "output_path": output_path}) as span:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Descargando desde: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        span.set_attribute("response.status_code", response.status_code)
        span.set_attribute("response.size_bytes", len(response.content))
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"Página descargada y guardada en: {out_path}")


def extract_metadata(lines: List[str]) -> Dict[str, Any]:
    """Extrae número de ley y fechas desde el encabezado."""
    with TraceSpan("extract_metadata", {"total_lines": len(lines)}) as span:
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
            span.set_attribute("numero_ley", ley_match.group(1))

        promulg_match = re.search(r"Fecha\s+de\s+Promulgaci[oó]n:?\s*(\d{2}-\d{2}-\d{4})", encabezado_text, re.IGNORECASE)
        if promulg_match:
            meta["fecha_promulgacion"] = promulg_match.group(1)

        public_match = re.search(r"Fecha\s+de\s+Publicaci[oó]n:?\s*(\d{2}-\d{2}-\d{4})", encabezado_text, re.IGNORECASE)
        if public_match:
            meta["fecha_publicacion"] = public_match.group(1)

        return meta


def extract_articles(lines: List[str]) -> List[Dict[str, Any]]:
    """Segmenta libros, títulos, capítulos y artículos en detalle."""
    with TraceSpan("extract_articles", {"total_lines": len(lines)}) as span:
        # Contexto de encabezados
        current_libro = None
        current_libro_num = None
        current_titulo = None
        current_capitulo = None
        current_capitulo_num = None
        current_capitulo_desc = None

        # Segmentacion de articulos
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

            # Detectar LIBRO
            m_lib = HEADER_PATTERNS['libro'].match(ln)
            if m_lib:
                current_libro = f"LIBRO {m_lib.group(1).title()}"
                current_libro_num = ROMAN_MAP.get(m_lib.group(1).upper())
                i += 1
                continue

            # Detectar TITULO
            m_tit = HEADER_PATTERNS['titulo'].match(ln)
            if m_tit:
                current_titulo = f"TITULO {m_tit.group(1).title()}"
                i += 1
                continue

            # Detectar CAPITULO
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

            # Detectar inicio de Articulo
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
        span.set_attribute("articles_extracted", len(articles))
        return articles


def parse_law_text(raw_text: str) -> Dict[str, Any]:
    """Parsea el texto completo en metadatos y artículos."""
    with TraceSpan("parse_law_text", {"text_length": len(raw_text)}) as span:
        text = fix_text(raw_text)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        
        span.set_attribute("total_lines", len(lines))
        
        meta = extract_metadata(lines)
        articles = extract_articles(lines)
        
        span.set_attribute("total_articles", len(articles))

        return {
            'meta': meta,
            'articulos': articles,
        }


def save_parsed_json_local(parsed: Dict[str, Any], processed_filename: str = "codigo_trabajo_articulos.json", output_root: str = None) -> str:
    """Guarda los datos parseados en un archivo JSON local en data/processed/ (raíz del proyecto o la indicada)"""
    with TraceSpan("save_parsed_json_local", {"filename": processed_filename}) as span:
        if output_root:
            project_root = Path(output_root)
        else:
            project_root = Path(__file__).resolve().parent.parent.parent
        out_dir = project_root / "data/processed"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / processed_filename
        
        articles_count = len(parsed.get('articulos', []))
        span.set_attribute("articles_count", articles_count)
        span.set_attribute("output_path", str(out_path))
        
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        
        file_size = out_path.stat().st_size
        span.set_attribute("file_size_bytes", file_size)
        
        print(f"Guardado localmente: {out_path}")
        print(f"Artículos totales: {articles_count}")
        return str(out_path)


def save_parsed_json_gcs(parsed: Dict[str, Any], bucket_name: str, processed_filename: str = "codigo_trabajo_articulos.json") -> str:
    """Guarda los datos parseados en un archivo JSON en GCS en processed/codigo_trabajo_articulos.json"""
    with TraceSpan("save_parsed_json_gcs", {"bucket_name": bucket_name, "filename": processed_filename}) as span:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"processed/{processed_filename}")
        json_str = json.dumps(parsed, ensure_ascii=False, indent=2)
        
        articles_count = len(parsed.get('articulos', []))
        span.set_attribute("articles_count", articles_count)
        span.set_attribute("json_size_bytes", len(json_str.encode('utf-8')))
        
        blob.upload_from_string(json_str, content_type='application/json')
        gcs_path = f"gs://{bucket_name}/processed/{processed_filename}"
        
        span.set_attribute("gcs_path", gcs_path)
        
        print(f"Guardado en GCS: {gcs_path}")
        print(f"Artículos totales: {articles_count}")
        return gcs_path


def upload_file_to_gcs(file_path: str, bucket_name: str, raw_filename: str = "codigo_trabajo_py.html") -> str:
    """Sube el HTML crudo a GCS en raw/codigo_trabajo_py.html"""
    with TraceSpan("upload_file_to_gcs", {"bucket_name": bucket_name, "filename": raw_filename}) as span:
        file_size = Path(file_path).stat().st_size
        span.set_attribute("file_size_bytes", file_size)
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"raw/{raw_filename}")
        blob.upload_from_filename(file_path, content_type='text/html; charset=utf-8')
        gcs_path = f"gs://{bucket_name}/raw/{raw_filename}"
        
        span.set_attribute("gcs_path", gcs_path)
        
        print(f"Archivo subido a GCS: {gcs_path}")
        return gcs_path


def create_temp_directories() -> tuple[Path, Path]:
    """Crea directorios temporales para el procesamiento."""
    temp_dir = Path(tempfile.mkdtemp(prefix="lus_laboris_"))
    raw_dir = temp_dir / "raw"
    processed_dir = temp_dir / "processed"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Directorios temporales creados en: {temp_dir}")
    return raw_dir, processed_dir


def cleanup_temp_directories(temp_dir: Path) -> None:
    """Limpia los directorios temporales."""
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print(f"Directorio temporal limpiado: {temp_dir}")
    except Exception as e:
        print(f"Advertencia: No se pudo limpiar el directorio temporal {temp_dir}: {e}")


def set_gcp_credentials(gcp_credentials_dir: str = None):
    """Busca un archivo .json en la carpeta indicada o en .gcpcredentials dos niveles arriba y setea GOOGLE_APPLICATION_CREDENTIALS si existe."""
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


def process_law_local(url: str, raw_filename: str = "codigo_trabajo_py.html", processed_filename: str = "codigo_trabajo_articulos.json", output_root: str = None) -> str:
    """Procesa la ley en modo local, guardando archivos en data/raw y data/processed en la raíz del proyecto o la indicada"""
    with TraceSpan("process_law_local", {"mode": "local", "url": url}) as span:
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
        
        span.set_attribute("output_path", output_path)
        span.set_attribute("success", True)
        
        return output_path


def process_law_gcs(url: str, bucket_name: str, raw_filename: str = "codigo_trabajo_py.html", processed_filename: str = "codigo_trabajo_articulos.json", use_local_credentials: bool = False, gcp_credentials_dir: str = None) -> str:
    """Procesa la ley en modo GCS, subiendo archivos a raw/ y processed/ en el bucket"""
    with TraceSpan("process_law_gcs", {"mode": "gcs", "url": url, "bucket_name": bucket_name}) as span:
        print("=== MODO GOOGLE CLOUD STORAGE ===")
        if use_local_credentials:
            set_gcp_credentials(gcp_credentials_dir)
        raw_dir, processed_dir = create_temp_directories()
        temp_dir = raw_dir.parent
        try:
            html_path = raw_dir / raw_filename
            download_law_page(url, str(html_path))
            # Siempre subir el HTML crudo
            try:
                upload_file_to_gcs(str(html_path), bucket_name, raw_filename)
            except Exception as e:
                print(f"Advertencia: No se pudo subir el HTML crudo a GCS: {e}")
                span.set_attribute("html_upload_failed", True)
            try:
                texto_limpio = extract_text_from_html(str(html_path))
            except ValueError as e:
                print(f"Error: {e}")
                raise
            parsed = parse_law_text(texto_limpio)
            # Siempre subir el JSON procesado
            gcs_path = save_parsed_json_gcs(parsed, bucket_name, processed_filename)
            
            span.set_attribute("gcs_path", gcs_path)
            span.set_attribute("success", True)
            
            return gcs_path
        finally:
            cleanup_temp_directories(temp_dir)


def extract_text_from_html(html_path: str) -> str:
    """
    Extrae el texto limpio del archivo HTML de la ley.
    
    Args:
        html_path: Ruta al archivo HTML
        
    Returns:
        Texto limpio extraído del HTML
        
    Raises:
        ValueError: Si no se puede encontrar el contenedor del contenido
    """
    with TraceSpan("extract_text_from_html", {"html_path": html_path}) as span:
        with open(html_path, 'r', encoding='latin-1') as archivo:
            contenido_html = archivo.read()
        
        span.set_attribute("html_size_bytes", len(contenido_html))
        
        # Parsear HTML
        soup = BeautifulSoup(contenido_html, 'html.parser')
        contenido_ley = soup.find('div', class_='entry-content')
        
        if not contenido_ley:
            raise ValueError("No se pudo encontrar el contenedor del contenido de la ley.")
        
        # Extraer texto limpio
        texto_limpio = contenido_ley.get_text(separator='\n', strip=True)
        span.set_attribute("extracted_text_length", len(texto_limpio))
        
        print("--- Contenido de la Ley extraído exitosamente ---")
        
        return texto_limpio


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extrae y procesa el texto del Código Laboral de Paraguay",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Ejemplos de uso:
        # Modo local (por defecto)
        python extract_law_text.py
        # Modo GCS
        python extract_law_text.py --mode gcs --bucket-name mi-bucket
        # Personalizando nombres de archivos
        python extract_law_text.py --raw-filename ley.html --processed-filename salida.json
        # Forzar uso de credenciales locales (desarrollo local)
        python extract_law_text.py --mode gcs --bucket-name mi-bucket --use-local-credentials
        # Especificar carpeta de credenciales
        python extract_law_text.py --mode gcs --bucket-name mi-bucket --use-local-credentials --gcp-credentials-dir /ruta/a/credenciales
        # Cambiar la raíz de salida local
        python extract_law_text.py --output-root /ruta/deseada
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['local', 'gcs'], 
        default='local', 
        help='Modo de ejecución: local (archivos locales) o gcs (Google Cloud Storage)')
    
    parser.add_argument(
        '--url', 
        default='https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo', 
        help='URL de la página de la ley')
    
    parser.add_argument(
        '--bucket-name', 
        help='Nombre del bucket de GCS (requerido para modo gcs)')
    
    parser.add_argument(
        '--raw-filename', 
        default='codigo_trabajo_py.html', 
        help='Nombre del archivo HTML crudo (por defecto: codigo_trabajo_py.html)')
    
    parser.add_argument(
        '--processed-filename', 
        default='codigo_trabajo_articulos.json', 
        help='Nombre del archivo JSON procesado (por defecto: codigo_trabajo_articulos.json)')
    
    parser.add_argument(
        '--use-local-credentials', 
        action='store_true', 
        help='Forzar uso de credenciales desde archivo local (para desarrollo local).')

    parser.add_argument(
        '--gcp-credentials-dir', 
        default=None, 
        help='Ruta a la carpeta donde buscar el archivo .json de credenciales de GCP (opcional, por defecto busca en la raíz del proyecto).')
    
    parser.add_argument(
        '--output-root', 
        default=None, 
        help='Raíz donde se crearán las carpetas data/raw y data/processed en modo local (opcional).')
        
    return parser.parse_args()


def main() -> int:
    # Inicializar Phoenix tracing (no falla si no está disponible)
    setup_phoenix_tracing()
    
    args = parse_arguments()
    print(f"Iniciando procesamiento en modo: {args.mode.upper()}")
    print(f"URL: {args.url}")
    
    with TraceSpan("main_process", {"mode": args.mode, "url": args.url}) as main_span:
        try:
            if args.mode == 'local':
                output_path = process_law_local(args.url, args.raw_filename, args.processed_filename, output_root=args.output_root)
                print(f"\n[SUCCESS] Proceso completado exitosamente!")
                print(f"[INFO] Archivo guardado en: {output_path}")
                main_span.set_attribute("output_path", output_path)
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
                main_span.set_attribute("gcs_path", gcs_path)
            
            main_span.set_attribute("status", "success")
            return 0
            
        except Exception as e:
            print(f"[ERROR] Error durante el procesamiento: {e}")
            main_span.set_attribute("status", "error")
            main_span.set_attribute("error_message", str(e))
            return 1


if __name__ == "__main__":
    exit(main())
