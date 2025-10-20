#!/bin/bash

# ============================================================================
# End-to-End Integration Test Script
# Script de Pruebas de Integración Completas
# ============================================================================
#
# Este script ejecuta un flujo completo de pruebas de integración:
# 1. Inicio de servicios (Qdrant + Phoenix)
# 2. Extracción de datos legales (ingesta local con tracing a Phoenix)
# 3. Inicio de la API
# 4. Generación de token JWT
# 5. Vectorización de datos en Qdrant
# 6. Consulta al endpoint público
# 7. Verificación de resultados
# 8. Cleanup
#
# Uso:
#   ./tests/integration/integration_test_e2e.sh
#
# ============================================================================

set -e  # Exit on error

# ============================================================================
# CONFIGURATION / CONFIGURACIÓN
# ============================================================================

# Directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Script is now in tests/integration/, so we need to go up two levels to get to project root
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
PROCESSING_DIR="$PROJECT_ROOT/src/processing"
API_DIR="$PROJECT_ROOT/src/lus_laboris_api"
SERVICES_DIR="$PROJECT_ROOT/services"
UTILS_DIR="$PROJECT_ROOT/utils"
DATA_DIR="$PROJECT_ROOT/data"
TEMP_DIR="$PROJECT_ROOT/.integration_test_temp"

# Test configuration
TEST_OUTPUT_FILE="$TEMP_DIR/articulos_test.json"
TEST_COLLECTION_NAME="legal_articles_test"
TEST_QUESTION="¿Cuántos días de vacaciones corresponden al trabajador?"
API_BASE_URL="http://localhost:8000"
WAIT_TIMEOUT=60  # seconds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# State tracking
SERVICES_STARTED=false
API_STARTED=false
CLEANUP_NEEDED=false

# ============================================================================
# HELPER FUNCTIONS / FUNCIONES DE AYUDA
# ============================================================================

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                  ║"
    echo "║          🧪 END-TO-END INTEGRATION TEST                         ║"
    echo "║                                                                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}${BOLD}▶ $1${NC}"
    echo -e "${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Cleanup function
cleanup() {
    local exit_code=$?

    if [ "$CLEANUP_NEEDED" = true ]; then
        echo ""
        print_step "🧹 CLEANUP - Limpiando recursos"

        # Stop API
        if [ "$API_STARTED" = true ]; then
            print_info "Deteniendo API..."
            cd "$API_DIR"
            docker compose down > /dev/null 2>&1 || true
        fi

        # Stop services (Qdrant + Phoenix)
        if [ "$SERVICES_STARTED" = true ]; then
            print_info "Deteniendo servicios (Qdrant + Phoenix)..."
            cd "$SERVICES_DIR/vectordb"
            docker compose down > /dev/null 2>&1 || true
            cd "$SERVICES_DIR/monitoring"
            docker compose down > /dev/null 2>&1 || true
        fi

        # Remove temp directory
        if [ -d "$TEMP_DIR" ]; then
            print_info "Removiendo archivos temporales..."
            rm -rf "$TEMP_DIR"
        fi

        print_success "Cleanup completado"
    fi

    # Final status
    echo ""
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}${BOLD}✅ INTEGRATION TEST PASSED - Todas las pruebas exitosas${NC}"
    else
        echo -e "${RED}${BOLD}❌ INTEGRATION TEST FAILED - Falló en algún paso${NC}"
    fi
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    exit $exit_code
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=$((WAIT_TIMEOUT / 2))
    local attempt=1

    print_info "Esperando que $service_name esté listo (max ${WAIT_TIMEOUT}s)..."

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_success "$service_name está listo (${attempt}s)"
            return 0
        fi

        echo -ne "   Intento $attempt/$max_attempts...\r"
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "$service_name no respondió después de ${WAIT_TIMEOUT}s"
    return 1
}

# Check prerequisites
check_prerequisites() {
    print_step "1️⃣  VERIFICANDO PREREQUISITOS"

    # Check Docker
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker no está ejecutándose"
        exit 1
    fi
    print_success "Docker: OK"

    # Check .env file
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        print_error "Archivo .env no encontrado en $PROJECT_ROOT"
        exit 1
    fi
    print_success ".env: OK"

    # Check JWT keys
    if [ ! -f "$PROJECT_ROOT/keys/private_key.pem" ] || [ ! -f "$PROJECT_ROOT/keys/public_key.pem" ]; then
        print_warning "Claves JWT no encontradas, generando..."
        cd "$UTILS_DIR"
        ./generate_jwt_keys.sh
        cd "$PROJECT_ROOT"
    else
        print_success "JWT Keys: OK"
    fi

    # Create temp directory
    mkdir -p "$TEMP_DIR"
    CLEANUP_NEEDED=true

    print_success "Prerequisitos verificados"
}

# ============================================================================
# TEST STEPS / PASOS DE PRUEBA
# ============================================================================

# Step 1: Start Services (Qdrant + Phoenix)
step_start_services() {
    print_step "2️⃣  INICIANDO SERVICIOS - Qdrant & Phoenix"

    # Start Qdrant
    print_info "Iniciando Qdrant..."
    cd "$SERVICES_DIR/vectordb"
    docker compose up -d

    # Start Phoenix
    print_info "Iniciando Phoenix..."
    cd "$SERVICES_DIR/monitoring"
    docker compose up -d

    SERVICES_STARTED=true

    # Wait for services to be ready
    wait_for_service "http://localhost:6333" "Qdrant"
    wait_for_service "http://localhost:6006" "Phoenix"

    print_success "Servicios iniciados correctamente"
}

# Step 2: Data Extraction (Local) - After Phoenix is running for tracing
step_data_extraction() {
    print_step "3️⃣  EXTRACCIÓN DE DATOS - Ingesta Local (con tracing a Phoenix)"

    # The output file is in the project root data/processed directory
    local expected_output="$PROJECT_ROOT/data/processed/codigo_trabajo_articulos.json"

    # Check if file already exists to skip extraction (faster + avoids 523 errors)
    if [ -f "$expected_output" ]; then
        print_info "Archivo ya existe, saltando extracción..."
        print_info "Usando: $expected_output"

        # Copy to temp dir for the test
        cp "$expected_output" "$TEST_OUTPUT_FILE"

        # Count articles
        local article_count=$(jq '.articulos | length' "$TEST_OUTPUT_FILE")
        print_success "Archivo reutilizado: $article_count artículos"
        return 0
    fi

    # If file doesn't exist, run extraction
    cd "$PROCESSING_DIR"

    print_info "Archivo no existe, ejecutando extract_law_text.py..."
    print_info "Output: data/processed/codigo_trabajo_articulos.json"

    # Run extraction in local mode with quality validation skipped for faster testing
    # The script will save to PROJECT_ROOT/data/processed/codigo_trabajo_articulos.json by default
    uv run extract_law_text.py --skip-quality-validation

    if [ ! -f "$expected_output" ]; then
        print_error "Archivo de salida no fue creado en $expected_output"
        exit 1
    fi

    # Copy to temp dir for the test
    cp "$expected_output" "$TEST_OUTPUT_FILE"

    # Count articles (they're in an array under "articulos" key)
    local article_count=$(jq '.articulos | length' "$TEST_OUTPUT_FILE")
    print_success "Extracción completada: $article_count artículos"
    print_info "Archivo guardado en: $expected_output"
}

# Step 3: Start API
step_start_api() {
    print_step "4️⃣  INICIANDO API - FastAPI"

    cd "$API_DIR"

    print_info "Construyendo e iniciando API con Docker Compose..."
    docker compose up -d --build

    API_STARTED=true

    # Wait for API to be ready
    wait_for_service "$API_BASE_URL/api/health" "API"

    # Verify health check
    local health_response=$(curl -s "$API_BASE_URL/api/health")
    print_info "Health check: $health_response"

    print_success "API iniciada correctamente"
}

# Step 4: Generate JWT Token
step_generate_token() {
    print_step "5️⃣  GENERANDO TOKEN JWT"

    cd "$PROJECT_ROOT"  # generate_jwt_token.py needs to run from project root

    print_info "Generando token para usuario 'admin'..."

    # Generate token and capture output
    # The script outputs the token directly, so we capture it
    local token_output=$(cd "$UTILS_DIR" && uv run python generate_jwt_token.py --username admin --expiry 60 2>/dev/null | grep -v "^🔑\|^═\|^Token válido\|^Expira" | tr -d '\n' | xargs)

    if [ -z "$token_output" ]; then
        print_error "Token no fue generado"
        print_info "Intentando generar con output a archivo..."
        cd "$UTILS_DIR"
        uv run python generate_jwt_token.py --username admin --expiry 60 --output "$TEMP_DIR/jwt_token.txt" > /dev/null 2>&1

        if [ -f "$TEMP_DIR/jwt_token.txt" ]; then
            JWT_TOKEN=$(cat "$TEMP_DIR/jwt_token.txt" | tr -d '\n' | xargs)
        fi
    else
        JWT_TOKEN="$token_output"
    fi

    if [ -z "$JWT_TOKEN" ]; then
        print_error "Token está vacío después de todos los intentos"
        exit 1
    fi

    print_success "Token generado (${#JWT_TOKEN} caracteres)"
    print_info "Token (primeros 50 chars): ${JWT_TOKEN:0:50}..."
}

# Step 5: Vectorize Data to Qdrant
step_vectorize_data() {
    print_step "6️⃣  VECTORIZANDO DATOS - Carga a Qdrant"

    print_info "Endpoint: POST $API_BASE_URL/api/data/load-to-vectorstore-local"

    # The endpoint expects filename (without path) and local_data_path (directory)
    # We need to use the default data/processed path and the default filename
    # Since we copied the file to that location, we use the default filename
    local payload=$(cat <<EOF
{
  "filename": "codigo_trabajo_articulos.json",
  "local_data_path": "data/processed",
  "collection_name": "$TEST_COLLECTION_NAME",
  "replace_collection": true
}
EOF
)

    print_info "Payload:"
    echo "$payload" | jq '.'

    # Make request (expects 202 Accepted for async job)
    local response=$(curl -s -w "\n%{http_code}" \
        -X POST "$API_BASE_URL/api/data/load-to-vectorstore-local" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$payload")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    print_info "HTTP Status: $http_code"

    if [ "$http_code" != "202" ]; then
        print_error "Vectorización falló (esperaba 202, recibió $http_code)"
        echo "$body" | jq '.' || echo "$body"
        exit 1
    fi

    print_info "Response (job iniciado):"
    echo "$body" | jq '.'

    # Extract job ID
    local job_id=$(echo "$body" | jq -r '.job_id // ""')

    if [ -z "$job_id" ]; then
        print_error "No se recibió job_id"
        exit 1
    fi

    print_success "Job de vectorización iniciado: $job_id"

    # Wait for job to complete (poll status endpoint)
    print_info "Esperando que el job complete (puede tomar 1-2 minutos)..."
    local max_wait=180  # 3 minutes max
    local elapsed=0

    while [ $elapsed -lt $max_wait ]; do
        sleep 5
        elapsed=$((elapsed + 5))

        # Get all jobs and filter by job_id (since there's no individual endpoint)
        local all_jobs=$(curl -s "$API_BASE_URL/api/data/jobs" \
            -H "Authorization: Bearer $JWT_TOKEN")

        # Filter for our specific job_id
        local job_status=$(echo "$all_jobs" | jq -r --arg jid "$job_id" '.jobs[] | select(.job_id == $jid)')

        if [ -z "$job_status" ]; then
            print_warning "Job $job_id no encontrado en la lista"
            continue
        fi

        local status=$(echo "$job_status" | jq -r '.status // "unknown"')

        if [ "$status" = "completed" ]; then
            print_success "Job completado exitosamente"

            # Extract and show results
            local docs_processed=$(echo "$job_status" | jq -r '.result.documents_processed // 0')
            local docs_inserted=$(echo "$job_status" | jq -r '.result.documents_inserted // 0')
            local proc_time=$(echo "$job_status" | jq -r '.result.processing_time_seconds // 0')

            print_info "  - Documentos procesados: $docs_processed"
            print_info "  - Documentos insertados: $docs_inserted"
            print_info "  - Tiempo de procesamiento: ${proc_time}s"
            return 0
        elif [ "$status" = "failed" ]; then
            print_error "Job falló"
            echo "$job_status" | jq '.'
            exit 1
        fi

        echo -ne "   Esperando... ${elapsed}s/${max_wait}s (status: $status)\r"
    done

    print_error "Job no completó en ${max_wait}s"
    exit 1
}

# Step 6: Query RAG Endpoint
step_query_rag() {
    print_step "7️⃣  CONSULTANDO RAG ENDPOINT"

    print_info "Endpoint: POST $API_BASE_URL/api/rag/ask"
    print_info "Pregunta: \"$TEST_QUESTION\""

    # Prepare request payload - QuestionRequest only has 'question' field
    local payload=$(cat <<EOF
{
  "question": "$TEST_QUESTION"
}
EOF
)

    print_info "Payload:"
    echo "$payload" | jq '.'

    # Make request
    local response=$(curl -s -w "\n%{http_code}" \
        -X POST "$API_BASE_URL/api/rag/ask" \
        -H "Content-Type: application/json" \
        -d "$payload")

    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')

    print_info "HTTP Status: $http_code"

    if [ "$http_code" != "200" ]; then
        print_error "Consulta RAG falló"
        echo "$body" | jq '.' || echo "$body"
        exit 1
    fi

    # Save full response for inspection
    echo "$body" | jq '.' > "$TEMP_DIR/rag_response.json"

    # Extract key information
    local success=$(echo "$body" | jq -r '.success')
    local answer=$(echo "$body" | jq -r '.answer')
    local documents_count=$(echo "$body" | jq -r '.documents | length')
    local session_id=$(echo "$body" | jq -r '.session_id')
    local processing_time=$(echo "$body" | jq -r '.processing_time_seconds')

    print_info "Response guardado en: $TEMP_DIR/rag_response.json"
    echo ""
    print_info "━━━ RESPUESTA ━━━"
    echo -e "${MAGENTA}$answer${NC}"
    echo ""

    print_success "Consulta RAG exitosa"
    print_info "  - Success: $success"
    print_info "  - Documentos recuperados: $documents_count"
    print_info "  - Session ID: $session_id"
    print_info "  - Processing time: ${processing_time}s"
}

# Step 7: Verify Results
step_verify_results() {
    print_step "8️⃣  VERIFICANDO RESULTADOS"

    local response_file="$TEMP_DIR/rag_response.json"

    if [ ! -f "$response_file" ]; then
        print_error "Archivo de respuesta no encontrado"
        exit 1
    fi

    # Verification 1: Success flag
    local success=$(jq -r '.success' "$response_file")
    if [ "$success" != "true" ]; then
        print_error "Campo 'success' no es true"
        exit 1
    fi
    print_success "✓ Campo 'success': true"

    # Verification 2: Answer is not empty
    local answer=$(jq -r '.answer' "$response_file")
    if [ -z "$answer" ] || [ "$answer" = "null" ]; then
        print_error "Respuesta está vacía"
        exit 1
    fi
    print_success "✓ Respuesta no vacía (${#answer} caracteres)"

    # Verification 3: Documents retrieved
    local docs_count=$(jq -r '.documents | length' "$response_file")
    if [ "$docs_count" -lt 1 ]; then
        print_error "No se recuperaron documentos"
        exit 1
    fi
    print_success "✓ Documentos recuperados: $docs_count"

    # Verification 4: Documents have required fields
    local first_doc_has_content=$(jq -r '.documents[0] | has("content")' "$response_file")
    if [ "$first_doc_has_content" != "true" ]; then
        print_error "Documentos no tienen campo 'content'"
        exit 1
    fi
    print_success "✓ Documentos tienen estructura correcta"

    # Verification 5: Session ID exists
    local session_id=$(jq -r '.session_id' "$response_file")
    if [ -z "$session_id" ] || [ "$session_id" = "null" ]; then
        print_error "Session ID no existe"
        exit 1
    fi
    print_success "✓ Session ID: $session_id"

    # Verification 6: Answer mentions relevant keywords (vacaciones, días, etc)
    if echo "$answer" | grep -qi -e "vacaciones\|días\|artículo\|trabajador"; then
        print_success "✓ Respuesta contiene keywords relevantes"
    else
        print_warning "⚠️  Respuesta no contiene keywords esperados (puede ser válida igualmente)"
    fi

    print_success "Todas las verificaciones pasaron"
}

# ============================================================================
# MAIN EXECUTION / EJECUCIÓN PRINCIPAL
# ============================================================================

main() {
    print_header

    print_info "Directorio del proyecto: $PROJECT_ROOT"
    print_info "Directorio temporal: $TEMP_DIR"
    echo ""

    # Execute test steps
    check_prerequisites
    step_start_services      # Start Phoenix BEFORE data extraction (for tracing)
    step_data_extraction     # Extract data with Phoenix tracing enabled
    step_start_api
    step_generate_token
    step_vectorize_data
    step_query_rag
    step_verify_results

    # Success!
    exit 0
}

# Run main
main
