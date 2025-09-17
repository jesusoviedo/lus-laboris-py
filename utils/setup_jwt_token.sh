#!/bin/bash

# JWT Token Setup Script - Simplified Version
# This script automates the process of generating RSA keys and JWT tokens

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
USERNAME="admin"
EXPIRY_MINUTES="60"
KEY_SIZE="2048"
OUTPUT_FILE=""
FORCE="false"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BOLD}${PURPLE}$1${NC}"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--username)
            USERNAME="$2"
            shift 2
            ;;
        -e|--expiry)
            EXPIRY_MINUTES="$2"
            shift 2
            ;;
        -k|--key-size)
            KEY_SIZE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -f|--force)
            FORCE="true"
            shift
            ;;
        -h|--help)
            echo "Uso: $0 [OPCIONES]"
            echo "Opciones:"
            echo "  -u, --username USERNAME    Nombre de usuario (default: admin)"
            echo "  -e, --expiry MINUTES       Expiración en minutos (default: 60)"
            echo "  -k, --key-size SIZE        Tamaño de clave en bits (default: 2048)"
            echo "  -o, --output FILE          Archivo de salida (opcional)"
            echo "  -f, --force                Sobrescribir claves existentes"
            echo "  -h, --help                 Mostrar ayuda"
            exit 0
            ;;
        *)
            print_error "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

# Main execution
print_header "🔐 Configuración de JWT Token para Lus Laboris API"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Step 1: Generate keys
print_info "Verificando claves RSA..."
if [[ -f "keys/private_key.pem" && -f "keys/public_key.pem" ]]; then
    if [[ "$FORCE" == "true" ]]; then
        print_warning "Claves existentes serán sobrescritas"
    else
        print_warning "Claves RSA ya existen"
        echo -n "¿Sobrescribir? (y/N): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_info "Reutilizando claves existentes"
        else
            FORCE="true"
        fi
    fi
fi

if [[ "$FORCE" == "true" || ! -f "keys/private_key.pem" ]]; then
    print_info "Generando claves RSA de $KEY_SIZE bits..."
    bash "$SCRIPT_DIR/generate_jwt_keys.sh" --size "$KEY_SIZE" --force
    print_success "Claves RSA generadas"
fi

# Step 2: Generate token
print_info "Generando token JWT para usuario: $USERNAME"

# Check if uv is available
if ! command -v uv >/dev/null 2>&1; then
    print_error "uv no está instalado en el sistema"
    print_error "Por favor instala uv para continuar:"
    print_error "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    print_error "  o visita: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Change to project root for uv run to work properly
cd "$SCRIPT_DIR"
TOKEN=$(uv run "generate_jwt_token.py" --username "$USERNAME" --expiry "$EXPIRY_MINUTES" 2>/dev/null | sed -n '/^eyJ[A-Za-z0-9+/=]\+\./p')

if [[ -z "$TOKEN" ]]; then
    print_error "Error al generar el token"
    exit 1
fi

print_success "Token JWT generado exitosamente"

# Step 3: Validate token
print_info "Validando token JWT..."

# Change to project root for uv run to work properly
cd "$SCRIPT_DIR"
if uv run "generate_jwt_token.py" --validate --token "$TOKEN" > /dev/null 2>&1; then
    print_success "Token JWT validado exitosamente"
else
    print_error "Error al validar el token"
    exit 1
fi

# Step 4: Save to file if requested
if [[ -n "$OUTPUT_FILE" ]]; then
    echo "$TOKEN" > "$OUTPUT_FILE"
    print_success "Token guardado en: $OUTPUT_FILE"
fi

# Step 5: Show final instructions
print_header "🎉 ¡Configuración JWT Completada!"
echo ""
print_info "Tu token JWT está listo para usar:"
echo ""
echo -e "${CYAN}JWT_TOKEN=\"$TOKEN\"${NC}"
echo ""
print_info "Para usar este token en tu terminal:"
echo -e "${YELLOW}export JWT_TOKEN=\"$TOKEN\"${NC}"
echo ""
print_info "Para usar en scripts o aplicaciones:"
echo -e "${YELLOW}curl -H \"Authorization: Bearer \$JWT_TOKEN\"${NC}"
echo -e "${YELLOW}     -H \"Content-Type: application/json\"${NC}"
echo -e "${YELLOW}     -X POST http://localhost:8000/api/data/load-to-vectorstore${NC}"
echo ""
print_info "Para validar el token en cualquier momento:"
echo -e "${YELLOW}uv run $SCRIPT_DIR/generate_jwt_token.py --validate --token \"\$JWT_TOKEN\"${NC}"
echo ""
print_success "¡Configuración completada exitosamente!"
