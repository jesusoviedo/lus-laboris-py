#!/bin/bash
# Development script to start the Lus Laboris API
# Usage: ./start_api_dev.sh

set -e  # Exit on any error

echo "🚀 Iniciando Lus Laboris API en modo DESARROLLO..."
echo "=================================================="

# Check that we are in the correct directory
if [ ! -f "api/main.py" ]; then
    echo "❌ Error: No se encontró api/main.py"
    echo "   Asegúrate de ejecutar este script desde src/lus_laboris_api/"
    exit 1
fi

# Check that .env file exists in project root
if [ ! -f "../../.env" ]; then
    echo "⚠️  Advertencia: No se encontró el archivo .env en la raíz del proyecto"
    echo "   La API usará valores por defecto"
else
    echo "✅ Cargando variables de entorno desde ../../.env"
    # Load environment variables using dotenv-style parsing
    # This correctly handles values with spaces, quotes, etc.
    set -a  # Automatically export variables
    # Use grep and eval to correctly handle values with spaces and quotes
    eval "$(grep -v '^#' ../../.env | grep -v '^[[:space:]]*$' | sed 's/^/export /')"
    set +a  # Disable automatic export
fi

# Check that uv is installed
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
echo "   - Log Level: ${API_LOG_LEVEL:-info}"

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

# Start the API with uvicorn
uv run uvicorn api.main:app \
    --host ${API_HOST:-0.0.0.0} \
    --port ${API_PORT:-8000} \
    --reload \
    --log-level ${API_LOG_LEVEL:-info} \
    --access-log
