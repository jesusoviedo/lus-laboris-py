<div align="center">

**Language / Idioma:**
[🇺🇸 English](#source-code) | [🇪🇸 Español](#código-fuente)

</div>

---
# Source Code

This directory contains the core source code of the project, including the RAG API and data preprocessing scripts.

## Contents

- `lus_laboris_api/` - FastAPI-based RAG system API
- `processing/` - Data preprocessing and text extraction scripts
- `README.md` - This documentation file

## Overview

### lus_laboris_api/

Production-ready RAG (Retrieval-Augmented Generation) API built with FastAPI. Provides endpoints for question answering, document management, and system health monitoring with support for multiple LLM providers.

**Documentation**: [lus_laboris_api/README.md](lus_laboris_api/README.md)

### processing/

Utilities for extracting and preprocessing text from legal documents before loading them into the vector database.

**Documentation**: [processing/README.md](processing/README.md)

## Development Notes

- Both projects use `uv` as the package manager
- Python 3.11 or higher is required
- Each subdirectory is a self-contained project with its own `pyproject.toml` and `Dockerfile`
- Configuration is managed through environment variables (see root `.env` file)

## Quick Links

- [API Documentation](lus_laboris_api/README.md)
- [Processing Documentation](processing/README.md)
- [Services Documentation](../services/README.md)
- [Project Documentation](../docs/README.md)

---

# Código Fuente

Este directorio contiene el código fuente principal del proyecto, incluyendo la API RAG y scripts de preprocesamiento de datos.

## Contenidos

- `lus_laboris_api/` - API del sistema RAG basada en FastAPI
- `processing/` - Scripts de preprocesamiento y extracción de texto
- `README.md` - Este archivo de documentación

## Descripción General

### lus_laboris_api/

API RAG (Retrieval-Augmented Generation) lista para producción construida con FastAPI. Proporciona endpoints para responder preguntas, gestionar documentos y monitorear la salud del sistema con soporte para múltiples proveedores de LLM.

**Documentación**: [lus_laboris_api/README.md](lus_laboris_api/README.md)

### processing/

Utilidades para extraer y preprocesar texto de documentos legales antes de cargarlos en la base de datos vectorial.

**Documentación**: [processing/README.md](processing/README.md)

## Notas de Desarrollo

- Ambos proyectos usan `uv` como gestor de paquetes
- Se requiere Python 3.11 o superior
- Cada subdirectorio es un proyecto autocontenido con su propio `pyproject.toml` y `Dockerfile`
- La configuración se gestiona a través de variables de entorno (ver archivo `.env` raíz)

## Enlaces Rápidos

- [Documentación de API](lus_laboris_api/README.md)
- [Documentación de Procesamiento](processing/README.md)
- [Documentación de Servicios](../services/README.md)
- [Documentación del Proyecto](../docs/README.md)
