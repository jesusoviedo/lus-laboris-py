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


# Patrones para identificar encabezados y artículos
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
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Descargando desde: {url}")
    response = requests.get(url)
    response.raise_for_status()
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"Página descargada y guardada en: {out_path}")


def extract_metadata(lines: List[str]) -> Dict[str, Any]:
    """Extrae número de ley y fechas desde el encabezado."""
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


def extract_articles(lines: List[str]) -> List[Dict[str, Any]]:
    """Segmenta libros, títulos, capítulos y artículos en detalle."""
    # Contexto de encabezados
    current_libro = None
    current_libro_num = None
    current_titulo = None
    current_capitulo = None
    current_capitulo_num = None
    current_capitulo_desc = None

    # Segmentación de artículos
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
            'texto': body.lower().replace('\n', ''),
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

        # Detectar inicio de Artículo
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


def parse_law_text(raw_text: str) -> Dict[str, Any]:
    """Parsea el texto completo en metadatos y artículos."""
    text = fix_text(raw_text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    
    meta = extract_metadata(lines)
    articles = extract_articles(lines)

    return {
        'meta': meta,
        'articulos': articles,
    }


def save_parsed_json_local(parsed: Dict[str, Any], filename: str = "codigo_trabajo_articulos.json", out_dir: str = "data/processed") -> str:
    """Guarda los datos parseados en un archivo JSON local."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

    print(f"Guardado localmente: {out_path}")
    print(f"Artículos totales: {len(parsed.get('articulos', []))}")
    return str(out_path)


def save_parsed_json_gcs(parsed: Dict[str, Any], bucket_name: str, blob_name: str = "codigo_trabajo_articulos.json") -> str:
    """Guarda los datos parseados en un archivo JSON en Google Cloud Storage."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Convertir a JSON string
    json_str = json.dumps(parsed, ensure_ascii=False, indent=2)
    
    # Subir a GCS
    blob.upload_from_string(json_str, content_type='application/json')
    
    gcs_path = f"gs://{bucket_name}/{blob_name}"
    print(f"Guardado en GCS: {gcs_path}")
    print(f"Artículos totales: {len(parsed.get('articulos', []))}")
    return gcs_path


def upload_file_to_gcs(file_path: str, bucket_name: str, blob_name: str, content_type: str | None = None) -> str:
    """Sube un archivo existente a Google Cloud Storage y devuelve su ruta gs://.

    Args:
        file_path: Ruta local del archivo a subir
        bucket_name: Nombre del bucket de GCS
        blob_name: Ruta/nombre del blob de destino en el bucket
        content_type: Content-Type opcional del archivo
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path, content_type=content_type)
    gcs_path = f"gs://{bucket_name}/{blob_name}"
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


def process_law_local(url: str, output_dir: str = "data/processed") -> str:
    """Procesa la ley en modo local."""
    print("=== MODO LOCAL ===")
    
    # Descargar HTML
    download_law_page(url)
    
    # Extraer texto del HTML
    html_path = "data/raw/codigo_trabajo_py.html"
    try:
        texto_limpio = extract_text_from_html(html_path)
    except ValueError as e:
        print(f"Error: {e}")
        raise
    
    # Parsear texto completo
    parsed = parse_law_text(texto_limpio)
    
    # Guardar resultado localmente
    output_path = save_parsed_json_local(parsed, out_dir=output_dir)
    
    return output_path


def process_law_gcs(url: str, bucket_name: str, blob_name: str = "codigo_trabajo_articulos.json", upload_raw: bool = False, raw_blob_name: str = "codigo_trabajo_py.html") -> str:
    """Procesa la ley en modo GCS con directorios temporales."""
    print("=== MODO GOOGLE CLOUD STORAGE ===")
    
    # Crear directorios temporales
    raw_dir, processed_dir = create_temp_directories()
    temp_dir = raw_dir.parent
    
    try:
        # Descargar HTML a directorio temporal
        html_path = raw_dir / "codigo_trabajo_py.html"
        download_law_page(url, str(html_path))
        
        # Subir HTML crudo si corresponde
        if upload_raw:
            try:
                upload_file_to_gcs(str(html_path), bucket_name, raw_blob_name, content_type='text/html; charset=utf-8')
            except Exception as e:
                print(f"Advertencia: No se pudo subir el HTML crudo a GCS: {e}")

        # Extraer texto del HTML
        try:
            texto_limpio = extract_text_from_html(str(html_path))
        except ValueError as e:
            print(f"Error: {e}")
            raise
        
        # Parsear texto completo
        parsed = parse_law_text(texto_limpio)
        
        # Guardar resultado en GCS
        gcs_path = save_parsed_json_gcs(parsed, bucket_name, blob_name)
        
        return gcs_path
        
    finally:
        # Limpiar directorios temporales
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
    with open(html_path, 'r', encoding='latin-1') as archivo:
        contenido_html = archivo.read()
    
    # Parsear HTML
    soup = BeautifulSoup(contenido_html, 'html.parser')
    contenido_ley = soup.find('div', class_='entry-content')
    
    if not contenido_ley:
        raise ValueError("No se pudo encontrar el contenedor del contenido de la ley.")
    
    # Extraer texto limpio
    texto_limpio = contenido_ley.get_text(separator='\n', strip=True)
    print("--- Contenido de la Ley extraído exitosamente ---")
    
    return texto_limpio


def parse_arguments():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Extrae y procesa el texto del Código Laboral de Paraguay",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Modo local (por defecto)
  python extract_law_text.py
  
  # Modo local con directorio personalizado
  python extract_law_text.py --mode local --output-dir /path/to/output
  
  # Modo GCS
  python extract_law_text.py --mode gcs --bucket-name mi-bucket --blob-name codigo_trabajo.json
  
  # Modo GCS con URL personalizada
  python extract_law_text.py --mode gcs --bucket-name mi-bucket --url "https://otra-url.com"
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['local', 'gcs'],
        default='local',
        help='Modo de ejecución: local (archivos locales) o gcs (Google Cloud Storage)'
    )
    
    parser.add_argument(
        '--url',
        default='https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo',
        help='URL de la página de la ley'
    )
    
    parser.add_argument(
        '--output-dir',
        default='data/processed',
        help='Directorio de salida para modo local (por defecto: data/processed)'
    )
    
    parser.add_argument(
        '--bucket-name',
        help='Nombre del bucket de GCS (requerido para modo gcs)'
    )
    
    parser.add_argument(
        '--blob-name',
        default='codigo_trabajo_articulos.json',
        help='Nombre del archivo en GCS (por defecto: codigo_trabajo_articulos.json)'
    )

    parser.add_argument(
        '--upload-raw',
        action='store_true',
        help='Si se especifica, sube el HTML crudo al bucket de GCS'
    )

    parser.add_argument(
        '--raw-blob-name',
        default='codigo_trabajo_py.html',
        help='Nombre del archivo HTML crudo en GCS (por defecto: codigo_trabajo_py.html)'
    )
    
    return parser.parse_args()


def main():
    """Función principal que ejecuta todo el proceso."""
    args = parse_arguments()
    
    print(f"Iniciando procesamiento en modo: {args.mode.upper()}")
    print(f"URL: {args.url}")
    
    try:
        if args.mode == 'local':
            output_path = process_law_local(args.url, args.output_dir)
            print(f"\n✅ Proceso completado exitosamente!")
            print(f"📁 Archivo guardado en: {output_path}")
            
        elif args.mode == 'gcs':
            if not args.bucket_name:
                print("❌ Error: --bucket-name es requerido para el modo GCS")
                return 1
            
            gcs_path = process_law_gcs(
                args.url,
                args.bucket_name,
                args.blob_name,
                upload_raw=args.upload_raw,
                raw_blob_name=args.raw_blob_name,
            )
            print(f"\n✅ Proceso completado exitosamente!")
            print(f"☁️  Archivo guardado en: {gcs_path}")
            
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
