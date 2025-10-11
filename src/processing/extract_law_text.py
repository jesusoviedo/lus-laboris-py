#!/usr/bin/env python3
"""
Script to extract and process the text of Paraguay's Labor Code.

This script automates the process of:
1. Downloading the HTML of the law from the official site
2. Extracting and cleaning the text
3. Segmenting into structured articles
4. Validating data quality and completeness
5. Saving in JSON format (local or Google Cloud Storage)

Execution modes:
- Local: Saves files to local filesystem
- GCS: Creates temporary folders and uploads JSON to Google Cloud Storage

Quality validation features:
- Validates article structure and required fields
- Verifies completeness (all 413 articles present)
- Analyzes content quality metrics
- Generates comprehensive quality reports

Based on notebook: notebooks/01_extract_law_text.ipynb
"""

import argparse
import json
import logging
import os
import re
import sys
import tempfile
import uuid
import warnings
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from ftfy import fix_text
from google.cloud import storage
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import SpanKind, set_span_in_context
from phoenix.otel import register

# Patterns to identify headers and articles
HEADER_PATTERNS = {
    "libro": re.compile(r"^LIBRO\s+([A-ZÁÉÍÓÚÑ]+)\s*$", re.IGNORECASE),
    "titulo": re.compile(r"^TITULO\s+([A-ZÁÉÍÓÚÑ]+)\s*$", re.IGNORECASE),
    "capitulo": re.compile(r"^CAPITULO\s+([IVXLCDM]+)\s*$", re.IGNORECASE),
}

ARTICULO_PATTERN = re.compile(r"^Art[íi]?t?culo\s+(\d+)\s*(?:[°º])?\s*\.?\s*-?\s*", re.IGNORECASE)

ROMAN_MAP = {
    "PRIMERO": 1,
    "SEGUNDO": 2,
    "TERCERO": 3,
    "CUARTO": 4,
    "QUINTO": 5,
    "SEXTO": 6,
    "SÉPTIMO": 7,
    "SEPTIMO": 7,
    "OCTAVO": 8,
    "NOVENO": 9,
    "DÉCIMO": 10,
    "DECIMO": 10,
    "UNDÉCIMO": 11,
    "UNDECIMO": 11,
    "DUODÉCIMO": 12,
    "DUODECIMO": 12,
}

_ROMAN_VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

# Global tracer instance
_tracer = None
_tracing_enabled = False

# Session management
_session_id = None
_session_start_time = None
_session_context = None

# Logging configuration
_process_logger = None
_phoenix_logger = None


def setup_logging(phoenix_log_level: str = "INFO"):
    """Configura el sistema de logging separado para proceso y Phoenix."""
    global _process_logger, _phoenix_logger

    # Logger para el proceso principal
    _process_logger = logging.getLogger("law_processing")
    _process_logger.setLevel(logging.INFO)

    # Logger para Phoenix/debug
    _phoenix_logger = logging.getLogger("phoenix_tracing")
    _phoenix_logger.setLevel(getattr(logging, phoenix_log_level.upper()))

    # Formatters
    process_formatter = logging.Formatter("%(asctime)s [PROCESO] %(message)s", datefmt="%H:%M:%S")
    phoenix_formatter = logging.Formatter("%(asctime)s [PHOENIX] %(message)s", datefmt="%H:%M:%S")

    # Console handlers
    process_handler = logging.StreamHandler()
    process_handler.setFormatter(process_formatter)
    process_handler.setLevel(logging.INFO)

    phoenix_handler = logging.StreamHandler()
    phoenix_handler.setFormatter(phoenix_formatter)
    phoenix_handler.setLevel(logging.DEBUG)

    # Add handlers
    _process_logger.addHandler(process_handler)
    _phoenix_logger.addHandler(phoenix_handler)

    # Prevent propagation to root logger
    _process_logger.propagate = False
    _phoenix_logger.propagate = False


def log_process(message: str, level: str = "info"):
    """Log para mensajes del proceso principal."""
    if _process_logger is None:
        setup_logging()

    if level.lower() == "info":
        _process_logger.info(message)
    elif level.lower() == "warning":
        _process_logger.warning(message)
    elif level.lower() == "error":
        _process_logger.error(message)
    elif level.lower() == "success":
        _process_logger.info(f"✅ {message}")
    elif level.lower() == "step":
        _process_logger.info(f"🔄 {message}")
    elif level.lower() == "result":
        _process_logger.info(f"📊 {message}")


def log_phoenix(message: str, level: str = "debug"):
    """Log para mensajes de Phoenix/debug."""
    if _phoenix_logger is None:
        setup_logging()

    if level.lower() == "debug":
        _phoenix_logger.debug(message)
    elif level.lower() == "info":
        _phoenix_logger.info(message)
    elif level.lower() == "warning":
        _phoenix_logger.warning(message)
    elif level.lower() == "error":
        _phoenix_logger.error(message)


def create_span_with_kind_fallback(
    tracer, operation_name: str, kind: SpanKind, attributes: dict[str, Any] = None, context=None
):
    """
    Creates a span with multiple fallback methods to ensure SpanKind is properly set.

    This function tries different approaches to ensure Phoenix recognizes the span kind:
    1. Standard OpenTelemetry approach
    2. Direct span kind setting
    3. Attribute-based approach
    """
    span = None

    try:
        # Method 1: Standard OpenTelemetry approach
        if context:
            span = tracer.start_span(
                operation_name, kind=kind, attributes=attributes, context=context
            )
        else:
            span = tracer.start_span(operation_name, kind=kind, attributes=attributes)

        log_phoenix(
            f"Span created with standard method: {operation_name} (kind: {kind.name})", "debug"
        )

    except Exception as e1:
        log_phoenix(f"Error with standard method: {e1}, trying alternative method", "warning")

        try:
            # Method 2: Try without context first, then add kind manually
            if context:
                span = tracer.start_span(operation_name, attributes=attributes, context=context)
            else:
                span = tracer.start_span(operation_name, attributes=attributes)

            # Try to set kind manually if possible
            if span and hasattr(span, "_kind"):
                span._kind = kind
                log_phoenix(f"Span kind establecido manualmente: {kind.name}", "debug")
            elif span and hasattr(span, "set_attribute"):
                span.set_attribute("span.kind", kind.name)
                span.set_attribute("span.type", str(kind))
                log_phoenix(f"Span kind establecido como atributo: {kind.name}", "debug")

        except Exception as e2:
            log_phoenix(f"Error with alternative method: {e2}, using basic span", "warning")

            # Method 3: Basic span creation
            if context:
                span = tracer.start_span(operation_name, attributes=attributes, context=context)
            else:
                span = tracer.start_span(operation_name, attributes=attributes)

            if span and hasattr(span, "set_attribute"):
                span.set_attribute("span.kind", kind.name)
                span.set_attribute("span.type", str(kind))
                log_phoenix(f"Basic span created with kind attributes: {kind.name}", "debug")

    return span


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
        base_url = endpoint.replace("/v1/traces", "").replace("/v1/spans", "")

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
        phoenix_endpoint = phoenix_endpoint or "http://localhost:6006/v1/traces"
        project_name = project_name or "lus-laboris-processing"

        # Check Phoenix availability
        if not check_phoenix_availability(phoenix_endpoint):
            log_phoenix(f"Phoenix endpoint is not reachable: {phoenix_endpoint}", "warning")
            log_phoenix("Tracing is enabled but spans may not be collected.", "warning")
            log_phoenix(
                "Make sure Phoenix is running: cd services/monitoring && docker-compose up -d",
                "warning",
            )

        # Configure Phoenix using official method
        tracer_provider = register(
            protocol="http/protobuf", project_name=project_name, endpoint=phoenix_endpoint
        )

        _tracer = tracer_provider.get_tracer(__name__)

        # Auto-instrument requests to capture HTTP calls
        RequestsInstrumentor().instrument()

        _tracing_enabled = True
        log_phoenix(f"Phoenix tracing configured: {phoenix_endpoint}", "info")
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


def initialize_phoenix_tracing():
    """Initializes Phoenix tracing and prints status."""
    phoenix_tracer = get_phoenix_tracer()
    if phoenix_tracer:
        log_phoenix("Phoenix tracing inicializado correctamente", "info")
    else:
        log_phoenix("Phoenix no disponible, continuando sin tracing", "info")


def create_session():
    """Creates a new session for grouping all spans of an execution."""
    global _session_id, _session_start_time, _session_context

    _session_id = str(uuid.uuid4())
    _session_start_time = datetime.now()

    # Create a custom trace context with session ID
    tracer = get_phoenix_tracer()
    if tracer and _tracing_enabled:
        # Create a root span for the session
        session_span = tracer.start_span(
            "execution_session",
            kind=SpanKind.SERVER,
            attributes={
                "session.id": _session_id,
                "session.start_time": _session_start_time.isoformat(),
                "session.type": "law_processing",
                "session.version": "1.0",
            },
        )
        _session_context = set_span_in_context(session_span)
        log_phoenix(f"Session created: {_session_id}", "info")
        return session_span
    _session_context = None
    log_phoenix(f"Session created (without tracing): {_session_id}", "info")
    return None


def get_session_info():
    """Returns current session information."""
    return {
        "session_id": _session_id,
        "start_time": _session_start_time,
        "context": _session_context,
    }


def add_session_attributes(attributes: dict[str, Any]) -> dict[str, Any]:
    """Adds session information to span attributes."""
    if not attributes:
        attributes = {}

    if _session_id:
        attributes.update(
            {
                "session.id": _session_id,
                "session.start_time": _session_start_time.isoformat()
                if _session_start_time
                else None,
                "execution.timestamp": datetime.now().isoformat(),
            }
        )

    return attributes


def end_session():
    """Ends the current session and closes the root span."""
    global _session_id, _session_start_time, _session_context

    if _session_context and _tracing_enabled:
        # Get the current span and end it
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute("session.end_time", datetime.now().isoformat())
            current_span.set_attribute(
                "session.duration_ms",
                int((datetime.now() - _session_start_time).total_seconds() * 1000),
            )
            current_span.end()
            log_phoenix(f"Session ended: {_session_id}", "info")

    # Reset session variables
    _session_id = None
    _session_start_time = None
    _session_context = None


@contextmanager
def phoenix_span(
    operation_name: str, kind: SpanKind = SpanKind.INTERNAL, attributes: dict[str, Any] = None
):
    """
    Context manager to create custom Phoenix spans with session information.

    Args:
        operation_name: Name of the operation for the span
        kind: Type of span (INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER)
        attributes: Dictionary of attributes for the span

    Yields:
        span: The Phoenix span or None if not available
    """
    tracer = get_phoenix_tracer()
    span = None

    if tracer and _tracing_enabled:
        try:
            # Add session attributes to span attributes
            enriched_attributes = add_session_attributes(attributes or {})

            # Add span kind as attribute for better visibility in Phoenix
            enriched_attributes["span.kind"] = kind.name
            enriched_attributes["span.type"] = kind.value if hasattr(kind, "value") else str(kind)

            # Use the fallback function to ensure proper span kind setting
            span = create_span_with_kind_fallback(
                tracer, operation_name, kind, enriched_attributes, _session_context
            )

            log_phoenix(
                f"Starting Phoenix span: {operation_name} (kind: {kind.name}) [Session: {_session_id[:8] if _session_id else 'N/A'}]",
                "debug",
            )
            yield span
        except Exception as e:
            log_phoenix(f"Error creando span Phoenix: {e}", "warning")
            yield None
        finally:
            if span:
                try:
                    span.end()
                    log_phoenix(f"Finalizando span Phoenix: {operation_name}", "debug")
                except Exception as e:
                    log_phoenix(f"Error finalizando span Phoenix: {e}", "warning")
    else:
        log_phoenix(f"Phoenix no disponible, ejecutando sin span: {operation_name}", "debug")
        yield None


# Context managers are now used instead of decorators for Phoenix tracing


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


def download_law_page(url: str, output_path: str = "data/raw/codigo_trabajo_py.html") -> None:
    """
    Downloads the HTML page of the law and saves it locally.

    Args:
        url: URL of the law page
        output_path: Path where to save the HTML file
    """
    with phoenix_span(
        "download_law_page", SpanKind.CLIENT, {"url": url, "output_path": output_path}
    ):
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        log_process(f"Descargando desde: {url}", "step")
        response = requests.get(url)
        response.raise_for_status()

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        log_process(f"Page downloaded and saved to: {out_path}", "success")


def extract_metadata(lines: list[str]) -> dict[str, Any]:
    """Extracts law number and dates from the header."""
    with phoenix_span("extract_metadata", SpanKind.INTERNAL, {"lines_count": len(lines)}):
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

        promulg_match = re.search(
            r"Fecha\s+de\s+Promulgaci[oó]n:?\s*(\d{2}-\d{2}-\d{4})", encabezado_text, re.IGNORECASE
        )
        if promulg_match:
            meta["fecha_promulgacion"] = promulg_match.group(1)

        public_match = re.search(
            r"Fecha\s+de\s+Publicaci[oó]n:?\s*(\d{2}-\d{2}-\d{4})", encabezado_text, re.IGNORECASE
        )
        if public_match:
            meta["fecha_publicacion"] = public_match.group(1)

        return meta


def extract_articles(lines: list[str]) -> list[dict[str, Any]]:
    """Segments books, titles, chapters and articles in detail."""
    with phoenix_span("extract_articles", SpanKind.INTERNAL, {"lines_count": len(lines)}):
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
            articles.append(
                {
                    "articulo_numero": int(current_article_num),
                    "libro": current_libro.lower() if current_libro else None,
                    "libro_numero": current_libro_num,
                    "titulo": current_titulo.lower() if current_titulo else None,
                    "capitulo": current_capitulo.lower() if current_capitulo else None,
                    "capitulo_numero": current_capitulo_num,
                    "capitulo_descripcion": current_capitulo_desc.lower()
                    if current_capitulo_desc
                    else None,
                    "articulo": body.lower().replace("\n", ""),
                }
            )

        i = 0
        while i < len(lines):
            ln = lines[i]

            # Detect BOOK
            m_lib = HEADER_PATTERNS["libro"].match(ln)
            if m_lib:
                current_libro = f"LIBRO {m_lib.group(1).title()}"
                current_libro_num = ROMAN_MAP.get(m_lib.group(1).upper())
                i += 1
                continue

            # Detect TITLE
            m_tit = HEADER_PATTERNS["titulo"].match(ln)
            if m_tit:
                current_titulo = f"TITULO {m_tit.group(1).title()}"
                i += 1
                continue

            # Detect CHAPTER
            m_cap = HEADER_PATTERNS["capitulo"].match(ln)
            if m_cap:
                roman = m_cap.group(1)
                current_capitulo = f"CAPITULO {roman}"
                current_capitulo_num = roman_to_int(roman)
                next_desc = None
                if i + 1 < len(lines):
                    nxt = lines[i + 1]
                    if not (
                        HEADER_PATTERNS["libro"].match(nxt)
                        or HEADER_PATTERNS["titulo"].match(nxt)
                        or HEADER_PATTERNS["capitulo"].match(nxt)
                        or ARTICULO_PATTERN.match(nxt)
                    ):
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
                    if (
                        HEADER_PATTERNS["libro"].match(nxt)
                        or HEADER_PATTERNS["titulo"].match(nxt)
                        or HEADER_PATTERNS["capitulo"].match(nxt)
                        or ARTICULO_PATTERN.match(nxt)
                    ):
                        break
                    current_article_lines.append(nxt)
                    i += 1
                continue

            i += 1

        flush_article()
        return articles


def parse_law_text(raw_text: str) -> dict[str, Any]:
    """Parses the complete text into metadata and articles."""
    with phoenix_span("parse_law_text", SpanKind.INTERNAL, {"text_length": len(raw_text)}):
        text = fix_text(raw_text)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        meta = extract_metadata(lines)
        articles = extract_articles(lines)

        return {
            "meta": meta,
            "articulos": articles,
        }


def validate_processed_data(articles: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Validates the integrity and quality of processed data.
    """
    with phoenix_span(
        "validate_processed_data", SpanKind.INTERNAL, {"articles_count": len(articles)}
    ):
        validation_results = {
            "total_articles": len(articles),
            "valid_articles": 0,
            "invalid_articles": [],
            "missing_fields": [],
            "quality_score": 0.0,
        }

        required_fields = ["articulo_numero", "libro", "capitulo", "articulo"]

        for article in articles:
            article_valid = True
            article_issues = []

            # Check required fields
            for field in required_fields:
                if field not in article or not article[field]:
                    article_issues.append(f"Campo faltante: {field}")
                    article_valid = False

            # Check that article number is valid
            if "articulo_numero" in article:
                art_num = article["articulo_numero"]
                if not isinstance(art_num, int) or art_num < 1 or art_num > 413:
                    article_issues.append(f"Número de artículo inválido: {art_num}")
                    article_valid = False

            # Check that content is not empty
            if "articulo" in article and len(article["articulo"].strip()) < 10:
                article_issues.append("Contenido del artículo demasiado corto")
                article_valid = False

            if article_valid:
                validation_results["valid_articles"] += 1
            else:
                validation_results["invalid_articles"].append(
                    {
                        "articulo_numero": article.get("articulo_numero", "desconocido"),
                        "issues": article_issues,
                    }
                )

        # Calcular score de calidad
        if validation_results["total_articles"] > 0:
            validation_results["quality_score"] = (
                validation_results["valid_articles"] / validation_results["total_articles"]
            )

        log_process(
            f"Validation completed: {validation_results['valid_articles']}/{validation_results['total_articles']} valid articles",
            "result",
        )
        log_process(f"Score de calidad: {validation_results['quality_score']:.2%}", "result")

        return validation_results


def verify_data_completeness(articles: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Verifies that all expected articles are present.
    """
    with phoenix_span(
        "verify_data_completeness", SpanKind.INTERNAL, {"articles_count": len(articles)}
    ):
        article_numbers = [art["articulo_numero"] for art in articles if "articulo_numero" in art]

        # Verificar rango completo (1-413)
        expected_range = set(range(1, 414))
        found_numbers = set(article_numbers)

        missing_articles = expected_range - found_numbers
        duplicate_articles = [num for num in article_numbers if article_numbers.count(num) > 1]

        completeness_report = {
            "expected_total": 413,
            "found_total": len(found_numbers),
            "missing_articles": sorted(list(missing_articles)),
            "duplicate_articles": duplicate_articles,
            "completeness_percentage": len(found_numbers) / 413 * 100,
        }

        log_process(
            f"Completitud de datos: {completeness_report['completeness_percentage']:.1f}%", "result"
        )

        if missing_articles:
            log_process(f"Missing articles: {missing_articles}", "warning")

        if duplicate_articles:
            log_process(f"Duplicate articles: {duplicate_articles}", "warning")

        return completeness_report


def analyze_content_quality(articles: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analyzes the quality of extracted content.
    """
    with phoenix_span(
        "analyze_content_quality", SpanKind.INTERNAL, {"articles_count": len(articles)}
    ):
        quality_metrics = {
            "avg_content_length": 0,
            "short_articles": 0,  # < 50 caracteres
            "medium_articles": 0,  # 50-200 caracteres
            "long_articles": 0,  # > 200 caracteres
            "articles_with_special_chars": 0,
            "articles_with_numbers": 0,
        }

        content_lengths = []

        for article in articles:
            if "articulo" not in article:
                continue

            content = article["articulo"]
            content_length = len(content.strip())
            content_lengths.append(content_length)

            # Classify by length
            if content_length < 50:
                quality_metrics["short_articles"] += 1
            elif content_length <= 200:
                quality_metrics["medium_articles"] += 1
            else:
                quality_metrics["long_articles"] += 1

            # Check special characteristics
            if any(char in content for char in ["°", "º", "§", "¶"]):
                quality_metrics["articles_with_special_chars"] += 1

            if any(char.isdigit() for char in content):
                quality_metrics["articles_with_numbers"] += 1

        if content_lengths:
            quality_metrics["avg_content_length"] = sum(content_lengths) / len(content_lengths)

        log_process("Quality analysis completed", "result")
        log_process(
            f"Average article length: {quality_metrics['avg_content_length']:.1f} characters",
            "result",
        )

        return quality_metrics


def generate_quality_report(articles: list[dict[str, Any]]) -> str:
    """
    Generates a comprehensive data quality report.
    """
    with phoenix_span(
        "generate_quality_report", SpanKind.INTERNAL, {"articles_count": len(articles)}
    ):
        validation_results = validate_processed_data(articles)
        completeness_report = verify_data_completeness(articles)
        quality_metrics = analyze_content_quality(articles)

        report = f"""
📊 REPORTE DE CALIDAD DE DATOS PROCESADOS
{"=" * 50}

✅ VALIDACIÓN DE ESTRUCTURA:
   • Artículos válidos: {validation_results["valid_articles"]}/{validation_results["total_articles"]}
   • Score de calidad: {validation_results["quality_score"]:.2%}
   • Artículos con problemas: {len(validation_results["invalid_articles"])}

📋 COMPLETITUD DE DATOS:
   • Artículos encontrados: {completeness_report["found_total"]}/413
   • Completitud: {completeness_report["completeness_percentage"]:.1f}%
   • Artículos faltantes: {len(completeness_report["missing_articles"])}
   • Artículos duplicados: {len(completeness_report["duplicate_articles"])}

📝 ANÁLISIS DE CONTENIDO:
   • Longitud promedio: {quality_metrics["avg_content_length"]:.1f} caracteres
   • Artículos cortos (< 50 chars): {quality_metrics["short_articles"]}
   • Artículos medianos (50-200 chars): {quality_metrics["medium_articles"]}
   • Artículos largos (> 200 chars): {quality_metrics["long_articles"]}
   • Con caracteres especiales: {quality_metrics["articles_with_special_chars"]}
   • Con números: {quality_metrics["articles_with_numbers"]}

🎯 ESTADO GENERAL: {"✅ EXCELENTE" if validation_results["quality_score"] > 0.95 else "⚠️ REQUIERE ATENCIÓN"}
"""

        log_process("Reporte de calidad generado", "result")
        return report


def save_parsed_json_local(
    parsed: dict[str, Any],
    processed_filename: str = "codigo_trabajo_articulos.json",
    output_root: str = None,
) -> str:
    """Saves parsed data to a local JSON file in data/processed/ (project root or specified one)"""
    articles_count = len(parsed.get("articulos", []))
    with phoenix_span(
        "save_parsed_json_local",
        SpanKind.INTERNAL,
        {
            "filename": processed_filename,
            "articles_count": articles_count,
            "output_root": output_root,
        },
    ):
        if output_root:
            project_root = Path(output_root)
        else:
            project_root = Path(__file__).resolve().parent.parent.parent
        out_dir = project_root / "data/processed"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / processed_filename

        with out_path.open("w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)

        log_process(f"Guardado localmente: {out_path}", "success")
        log_process(f"Total articles: {articles_count}", "result")
        return str(out_path)


def save_parsed_json_gcs(
    parsed: dict[str, Any],
    bucket_name: str,
    processed_filename: str = "codigo_trabajo_articulos.json",
) -> str:
    """Saves parsed data to a JSON file in GCS at processed/codigo_trabajo_articulos.json"""
    articles_count = len(parsed.get("articulos", []))
    with phoenix_span(
        "save_parsed_json_gcs",
        SpanKind.PRODUCER,
        {
            "bucket_name": bucket_name,
            "filename": processed_filename,
            "articles_count": articles_count,
        },
    ):
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"processed/{processed_filename}")
        json_str = json.dumps(parsed, ensure_ascii=False, indent=2)

        blob.upload_from_string(json_str, content_type="application/json")
        gcs_path = f"gs://{bucket_name}/processed/{processed_filename}"

        log_process(f"Guardado en GCS: {gcs_path}", "success")
        log_process(f"Total articles: {articles_count}", "result")
        return gcs_path


def upload_file_to_gcs(
    file_path: str, bucket_name: str, raw_filename: str = "codigo_trabajo_py.html"
) -> str:
    """Uploads raw HTML to GCS at raw/codigo_trabajo_py.html"""
    with phoenix_span(
        "upload_file_to_gcs",
        SpanKind.PRODUCER,
        {"file_path": file_path, "bucket_name": bucket_name, "filename": raw_filename},
    ):
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"raw/{raw_filename}")
        blob.upload_from_filename(file_path, content_type="text/html; charset=utf-8")
        gcs_path = f"gs://{bucket_name}/raw/{raw_filename}"

        log_process(f"Archivo subido a GCS: {gcs_path}", "success")
        return gcs_path


def create_temp_directories() -> tuple[Path, Path]:
    """Creates temporary directories for processing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="lus_laboris_"))
    raw_dir = temp_dir / "raw"
    processed_dir = temp_dir / "processed"

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    log_process(f"Directorios temporales creados en: {temp_dir}", "step")
    return raw_dir, processed_dir


def cleanup_temp_directories(temp_dir: Path) -> None:
    """Cleans up temporary directories."""
    import shutil

    try:
        shutil.rmtree(temp_dir)
        log_process(f"Directorio temporal limpiado: {temp_dir}", "step")
    except Exception as e:
        log_process(f"No se pudo limpiar el directorio temporal {temp_dir}: {e}", "warning")


def set_gcp_credentials(gcp_credentials_dir: str = None):
    """Searches for a .json file in the specified folder or in .gcpcredentials two levels up and sets GOOGLE_APPLICATION_CREDENTIALS if it exists."""
    from pathlib import Path

    if gcp_credentials_dir:
        cred_dir = Path(gcp_credentials_dir)
    else:
        project_root = Path(__file__).resolve().parent.parent.parent
        cred_dir = project_root / ".gcpcredentials"
    json_files = list(cred_dir.glob("*.json"))
    if json_files:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(json_files[0])
        log_process(f"Usando credenciales de servicio: {json_files[0]}", "step")


def process_law_local(
    url: str,
    raw_filename: str = "codigo_trabajo_py.html",
    processed_filename: str = "codigo_trabajo_articulos.json",
    output_root: str = None,
    skip_quality_validation: bool = False,
) -> str:
    """Processes the law in local mode, saving files in data/raw and data/processed in the project root or specified one"""
    with phoenix_span(
        "process_law_local",
        SpanKind.SERVER,
        {
            "url": url,
            "raw_filename": raw_filename,
            "processed_filename": processed_filename,
            "output_root": output_root,
        },
    ):
        log_process("=== MODO LOCAL ===", "step")
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
            log_process(f"Error: {e}", "error")
            raise
        parsed = parse_law_text(texto_limpio)

        # Data quality validation (optional)
        if not skip_quality_validation:
            log_process("=== QUALITY VALIDATION ===", "step")
            quality_report = generate_quality_report(parsed["articulos"])
            print(quality_report)  # Mostrar reporte completo
        else:
            log_process("Quality validation skipped", "step")

        output_path = save_parsed_json_local(parsed, processed_filename, output_root=output_root)

        return output_path


def process_law_gcs(
    url: str,
    bucket_name: str,
    raw_filename: str = "codigo_trabajo_py.html",
    processed_filename: str = "codigo_trabajo_articulos.json",
    use_local_credentials: bool = False,
    gcp_credentials_dir: str = None,
    skip_quality_validation: bool = False,
) -> str:
    """Processes the law in GCS mode, uploading files to raw/ and processed/ in the bucket"""
    with phoenix_span(
        "process_law_gcs",
        SpanKind.SERVER,
        {
            "url": url,
            "bucket_name": bucket_name,
            "raw_filename": raw_filename,
            "processed_filename": processed_filename,
            "use_local_credentials": use_local_credentials,
        },
    ):
        log_process("=== MODO GOOGLE CLOUD STORAGE ===", "step")
        if use_local_credentials:
            set_gcp_credentials(gcp_credentials_dir)
        raw_dir, _processed_dir = create_temp_directories()
        temp_dir = raw_dir.parent
        try:
            html_path = raw_dir / raw_filename
            download_law_page(url, str(html_path))
            # Always upload raw HTML
            try:
                upload_file_to_gcs(str(html_path), bucket_name, raw_filename)
            except Exception as e:
                log_process(f"No se pudo subir el HTML crudo a GCS: {e}", "warning")
            try:
                texto_limpio = extract_text_from_html(str(html_path))
            except ValueError as e:
                log_process(f"Error: {e}", "error")
                raise
            parsed = parse_law_text(texto_limpio)

            # Data quality validation (optional)
            if not skip_quality_validation:
                log_process("=== QUALITY VALIDATION ===", "step")
                quality_report = generate_quality_report(parsed["articulos"])
                print(quality_report)  # Mostrar reporte completo
            else:
                log_process("Quality validation skipped", "step")

            # Always upload processed JSON
            gcs_path = save_parsed_json_gcs(parsed, bucket_name, processed_filename)

            return gcs_path
        finally:
            cleanup_temp_directories(temp_dir)


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
    with phoenix_span("extract_text_from_html", SpanKind.INTERNAL, {"html_path": html_path}):
        with open(html_path, encoding="latin-1") as archivo:
            contenido_html = archivo.read()

        # Parse HTML
        soup = BeautifulSoup(contenido_html, "html.parser")
        contenido_ley = soup.find("div", class_="entry-content")

        if not contenido_ley:
            raise ValueError("No se pudo encontrar el contenedor del contenido de la ley.")

        # Extract clean text
        texto_limpio = contenido_ley.get_text(separator="\n", strip=True)

        log_process("Law content extracted successfully", "success")

        return texto_limpio


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extracts and processes the text of Paraguay's Labor Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Usage examples:
        # Local mode (default) with quality validation
        python extract_law_text.py
        # GCS mode with quality validation
        python extract_law_text.py --mode gcs --bucket-name mi-bucket
        # Skip quality validation for faster processing
        python extract_law_text.py --skip-quality-validation
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
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["local", "gcs"],
        default="local",
        help="Execution mode: local (local files) or gcs (Google Cloud Storage)",
    )

    parser.add_argument(
        "--url",
        default="https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo",
        help="URL of the law page",
    )

    parser.add_argument("--bucket-name", help="GCS bucket name (required for gcs mode)")

    parser.add_argument(
        "--raw-filename",
        default="codigo_trabajo_py.html",
        help="Raw HTML filename (default: codigo_trabajo_py.html)",
    )

    parser.add_argument(
        "--processed-filename",
        default="codigo_trabajo_articulos.json",
        help="Processed JSON filename (default: codigo_trabajo_articulos.json)",
    )

    parser.add_argument(
        "--use-local-credentials",
        action="store_true",
        help="Force use of credentials from local file (for local development).",
    )

    parser.add_argument(
        "--gcp-credentials-dir",
        default=None,
        help="Path to folder where to search for GCP .json credential file (optional, defaults to project root).",
    )

    parser.add_argument(
        "--output-root",
        default=None,
        help="Root where data/raw and data/processed folders will be created in local mode (optional).",
    )

    parser.add_argument(
        "--phoenix-endpoint",
        default=None,
        help="Phoenix endpoint URL for tracing (default: http://localhost:6006/v1/traces)",
    )

    parser.add_argument(
        "--phoenix-project-name",
        default=None,
        help="Phoenix project name for tracing (default: lus-laboris-processing)",
    )

    parser.add_argument(
        "--phoenix-log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Phoenix logging level (default: INFO)",
    )

    parser.add_argument(
        "--skip-quality-validation",
        action="store_true",
        help="Skip quality validation and reporting (default: False)",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    # Setup logging system
    setup_logging(args.phoenix_log_level)

    # Initialize Phoenix tracing (doesn't fail if not available)
    setup_phoenix_tracing(args.phoenix_endpoint, args.phoenix_project_name)

    # Initialize Phoenix tracing
    initialize_phoenix_tracing()

    # Create execution session
    session_span = create_session()

    log_process(f"Iniciando procesamiento en modo: {args.mode.upper()}", "step")
    log_process(f"URL: {args.url}", "info")
    log_process(f"Session ID: {_session_id}", "info")

    try:
        # Main span for the entire operation (now as child of session)
        with phoenix_span(
            "main_process",
            SpanKind.SERVER,
            {
                "mode": args.mode,
                "url": args.url,
                "bucket_name": args.bucket_name,
                "execution.args": str(vars(args)),
            },
        ):
            if args.mode == "local":
                output_path = process_law_local(
                    args.url,
                    args.raw_filename,
                    args.processed_filename,
                    output_root=args.output_root,
                    skip_quality_validation=args.skip_quality_validation,
                )
                log_process("Proceso completado exitosamente!", "success")
                log_process(f"Archivo guardado en: {output_path}", "result")
                log_process(f"Session: {_session_id}", "info")
            elif args.mode == "gcs":
                if not args.bucket_name:
                    log_process("--bucket-name es requerido para el modo GCS", "error")
                    return 1
                gcs_path = process_law_gcs(
                    args.url,
                    args.bucket_name,
                    raw_filename=args.raw_filename,
                    processed_filename=args.processed_filename,
                    use_local_credentials=args.use_local_credentials,
                    gcp_credentials_dir=args.gcp_credentials_dir,
                    skip_quality_validation=args.skip_quality_validation,
                )
                log_process("Proceso completado exitosamente!", "success")
                log_process(f"Archivo guardado en GCS: {gcs_path}", "result")
                log_process(f"Session: {_session_id}", "info")

            return 0

    except Exception as e:
        log_process(f"Error durante el procesamiento: {e}", "error")
        return 1
    finally:
        # End session
        end_session()


if __name__ == "__main__":
    sys.exit(main())
