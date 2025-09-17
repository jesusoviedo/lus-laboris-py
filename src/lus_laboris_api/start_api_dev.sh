#!/bin/bash
# Script para levantar la API en modo desarrollo
# Uso: ./start_api_dev.sh

set -e  # Salir si hay algún error

echo "🚀 Iniciando Lus Laboris API en modo DESARROLLO..."
echo "=================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "api/main.py" ]; then
    echo "❌ Error: No se encontró api/main.py"
    echo "   Asegúrate de ejecutar este script desde src/lus_laboris_api/"
    exit 1
fi

# Verificar que existe el archivo .env en la raíz del proyecto
if [ ! -f "../../.env" ]; then
    echo "⚠️  Advertencia: No se encontró el archivo .env en la raíz del proyecto"
    echo "   La API usará valores por defecto"
else
    echo "✅ Cargando variables de entorno desde ../../.env"
    # Cargar variables de entorno de forma segura
    set -a  # Automáticamente exportar variables
    source ../../.env
    set +a  # Desactivar exportación automática
fi

# Verificar que uv está instalado
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv no está instalado"
    echo "   Instala uv con: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv encontrado"

echo "📁 Directorio de trabajo: $(pwd)"
echo "🔧 Configuración:"
echo "   - Host: ${API_HOST:-0.0.0.0}"
echo "   - Puerto: ${API_PORT:-8000}"
echo "   - Reload: ${API_RELOAD:-true}"
echo "   - Log Level: ${LOG_LEVEL:-info}"

echo ""
echo "🌐 La API estará disponible en:"
echo "   - API: http://localhost:${API_PORT:-8000}"
echo "   - Swagger UI: http://localhost:${API_PORT:-8000}/docs"
echo "   - ReDoc: http://localhost:${API_PORT:-8000}/redoc"
echo "   - Health Check: http://localhost:${API_PORT:-8000}/api/health"
echo ""

echo "🔄 Iniciando servidor con recarga automática..."
echo "   Presiona Ctrl+C para detener"
echo ""

# Levantar la API con uvicorn
uv run uvicorn api.main:app \
    --host ${API_HOST:-0.0.0.0} \
    --port ${API_PORT:-8000} \
    --reload \
    --log-level ${LOG_LEVEL:-info} \
    --access-log
