#!/bin/bash

# Script para generar claves RSA pública y privada para JWT
# Uso: ./generate_jwt_keys.sh [directorio_destino] [tamaño_clave]

set -e  # Salir si hay algún error

# Configuración por defecto
DEFAULT_KEY_SIZE=2048
DEFAULT_PRIVATE_KEY="private_key.pem"
DEFAULT_PUBLIC_KEY="public_key.pem"

# Detectar la raíz del proyecto (donde está el script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEFAULT_OUTPUT_DIR="$PROJECT_ROOT/keys"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Generador de Claves RSA para JWT${NC}"
    echo ""
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  -d, --directory DIR    Directorio de salida (default: $DEFAULT_OUTPUT_DIR)"
    echo "  -s, --size SIZE        Tamaño de la clave en bits (default: $DEFAULT_KEY_SIZE)"
    echo "  -p, --private FILE     Nombre del archivo de clave privada (default: $DEFAULT_PRIVATE_KEY)"
    echo "  -u, --public FILE      Nombre del archivo de clave pública (default: $DEFAULT_PUBLIC_KEY)"
    echo "  -f, --force            Sobrescribir archivos existentes"
    echo "  -h, --help             Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0                                    # Generar claves con configuración por defecto"
    echo "  $0 -d /path/to/keys -s 4096          # Generar claves de 4096 bits en directorio específico"
    echo "  $0 -f                                # Sobrescribir archivos existentes"
    echo ""
}

# Función para mostrar mensajes de información
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Función para mostrar mensajes de éxito
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Función para mostrar mensajes de advertencia
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Función para mostrar mensajes de error
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar si openssl está instalado
check_openssl() {
    if ! command -v openssl &> /dev/null; then
        error "OpenSSL no está instalado. Por favor instálalo primero:"
        echo "  Ubuntu/Debian: sudo apt-get install openssl"
        echo "  CentOS/RHEL: sudo yum install openssl"
        echo "  macOS: brew install openssl"
        exit 1
    fi
}

# Función para verificar si los archivos ya existen
check_existing_files() {
    local private_path="$1"
    local public_path="$2"
    local force="$3"
    
    if [[ -f "$private_path" && -f "$public_path" ]]; then
        if [[ "$force" == "true" ]]; then
            warning "Los archivos existentes serán sobrescritos"
        else
            error "Los archivos ya existen:"
            [[ -f "$private_path" ]] && echo "  - $private_path"
            [[ -f "$public_path" ]] && echo "  - $public_path"
            echo ""
            echo "Usa -f o --force para sobrescribir los archivos existentes"
            exit 1
        fi
    fi
}

# Función para generar las claves
generate_keys() {
    local output_dir="$1"
    local key_size="$2"
    local private_key="$3"
    local public_key="$4"
    local force="$5"
    
    local private_path="$output_dir/$private_key"
    local public_path="$output_dir/$public_key"
    
    # Verificar si los archivos ya existen
    check_existing_files "$private_path" "$public_path" "$force"
    
    # Crear directorio si no existe
    mkdir -p "$output_dir"
    
    info "Generando clave privada RSA de $key_size bits..."
    openssl genrsa -out "$private_path" "$key_size"
    
    if [[ $? -eq 0 ]]; then
        success "Clave privada generada: $private_path"
    else
        error "Error al generar la clave privada"
        exit 1
    fi
    
    info "Generando clave pública RSA..."
    openssl rsa -pubout -in "$private_path" -out "$public_path"
    
    if [[ $? -eq 0 ]]; then
        success "Clave pública generada: $public_path"
    else
        error "Error al generar la clave pública"
        exit 1
    fi
    
    # Establecer permisos seguros
    chmod 600 "$private_path"  # Solo lectura para el propietario
    chmod 644 "$public_path"   # Lectura para todos
    
    success "Permisos de archivos configurados correctamente"
}

# Función para mostrar información de las claves generadas
show_key_info() {
    local private_path="$1"
    local public_path="$2"
    
    echo ""
    echo -e "${BLUE}Información de las claves generadas:${NC}"
    echo "=================================="
    
    # Información de la clave privada
    echo -e "${YELLOW}Clave Privada:${NC}"
    echo "  Archivo: $private_path"
    echo "  Tamaño: $(ls -lh "$private_path" | awk '{print $5}')"
    echo "  Permisos: $(ls -l "$private_path" | awk '{print $1}')"
    echo "  Fingerprint: $(openssl rsa -in "$private_path" -pubout -outform DER 2>/dev/null | openssl dgst -sha256 -binary | openssl enc -base64)"
    
    echo ""
    
    # Información de la clave pública
    echo -e "${YELLOW}Clave Pública:${NC}"
    echo "  Archivo: $public_path"
    echo "  Tamaño: $(ls -lh "$public_path" | awk '{print $5}')"
    echo "  Permisos: $(ls -l "$public_path" | awk '{print $1}')"
    echo "  Fingerprint: $(openssl rsa -in "$public_path" -pubin -outform DER 2>/dev/null | openssl dgst -sha256 -binary | openssl enc -base64)"
    
    echo ""
    echo -e "${GREEN}¡Claves generadas exitosamente!${NC}"
    echo ""
    echo -e "${YELLOW}Notas importantes:${NC}"
    echo "  - La clave privada debe mantenerse segura y no compartirse"
    echo "  - La clave pública puede ser compartida para validación de tokens"
    echo "  - Estas claves son compatibles con la API Lus Laboris"
    echo "  - Para usar en la generacion de token, configura las variables de entorno:"
    echo "    JWT_PRIVATE_KEY_PATH=$private_path"
    echo "    JWT_PUBLIC_KEY_PATH=$public_path"
    echo "    JWT_TOKEN_EXPIRY_MINUTES=60"
}


# Variables por defecto
OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"
KEY_SIZE="$DEFAULT_KEY_SIZE"
PRIVATE_KEY="$DEFAULT_PRIVATE_KEY"
PUBLIC_KEY="$DEFAULT_PUBLIC_KEY"
FORCE="false"

# Parsear argumentos de línea de comandos
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--directory)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -s|--size)
            KEY_SIZE="$2"
            shift 2
            ;;
        -p|--private)
            PRIVATE_KEY="$2"
            shift 2
            ;;
        -u|--public)
            PUBLIC_KEY="$2"
            shift 2
            ;;
        -f|--force)
            FORCE="true"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validar tamaño de clave
if ! [[ "$KEY_SIZE" =~ ^[0-9]+$ ]] || [[ "$KEY_SIZE" -lt 1024 ]]; then
    error "El tamaño de la clave debe ser un número entero mayor o igual a 1024"
    exit 1
fi

# Mostrar información de inicio
echo -e "${BLUE}Generador de Claves RSA para JWT - Lus Laboris${NC}"
echo "=================================================="
echo "Directorio de salida: $OUTPUT_DIR"
echo "Tamaño de clave: $KEY_SIZE bits"
echo "Clave privada: $PRIVATE_KEY"
echo "Clave pública: $PUBLIC_KEY"
echo ""

# Verificar dependencias
check_openssl

# Generar claves
generate_keys "$OUTPUT_DIR" "$KEY_SIZE" "$PRIVATE_KEY" "$PUBLIC_KEY" "$FORCE"

# Mostrar información de las claves
show_key_info "$OUTPUT_DIR/$PRIVATE_KEY" "$OUTPUT_DIR/$PUBLIC_KEY"

echo -e "${GREEN}Proceso completado exitosamente!${NC}"
