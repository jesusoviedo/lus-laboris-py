# Raw Data

<div align="center">

**Language / Idioma:**
[🇺🇸 English](#raw-data) | [🇪🇸 Español](#datos-crudos)

</div>

---

## Raw Data

This folder stores the original, unprocessed data as downloaded from external sources.

## Contents

- `codigo_trabajo_py.html` - HTML file of Paraguay's Labor Code (Ley Nº 213) downloaded from the official government website

## Processing

For information about data processing and usage, see the main [Data README](../README.md).

## Download

To manually download the raw content:

```bash
wget -O ./codigo_trabajo_py.html https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo
```

Or use the automated script: `python ../../src/processing/extract_law_text.py`

---

## Datos Crudos

Esta carpeta almacena los datos originales sin procesar, tal como fueron descargados de fuentes externas.

## Contenido

- `codigo_trabajo_py.html` - Archivo HTML del Código Laboral de Paraguay (Ley Nº 213) descargado del sitio oficial del gobierno

## Procesamiento

Para información sobre el procesamiento y uso de datos, consulta el [README principal de Datos](../README.md).

## Descarga

Para descargar manualmente el contenido crudo:

```bash
wget -O ./codigo_trabajo_py.html https://www.bacn.gov.py/leyes-paraguayas/2608/ley-n-213-establece-el-codigo-del-trabajo
```

O usa el script automatizado: `python ../../src/processing/extract_law_text.py`
