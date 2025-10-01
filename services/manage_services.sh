#!/bin/bash

# Services Management Script
# Script para gestionar servicios de Qdrant y Phoenix

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ADVERTENCIA]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Script de Gestión de Servicios${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker no está ejecutándose. Por favor inicia Docker primero."
        exit 1
    fi
}

# Function to check if service is running
is_service_running() {
    local service_dir=$1
    local service_name=$2
    
    if [ -f "$service_dir/docker-compose.yml" ]; then
        cd "$service_dir"
        if docker-compose ps | grep -q "Up"; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# Function to start a service
start_service() {
    local service_dir=$1
    local service_name=$2
    
    print_status "Iniciando $service_name..."
    
    if [ ! -f "$service_dir/docker-compose.yml" ]; then
        print_error "docker-compose.yml no encontrado en $service_dir"
        return 1
    fi
    
    cd "$service_dir"
    
    if is_service_running "$service_dir" "$service_name"; then
        print_warning "$service_name ya está ejecutándose"
        return 0
    fi
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_status "$service_name iniciado exitosamente"
        
        # Mostrar información específica del servicio
        case $service_name in
            "Qdrant")
                echo "  - Base de Datos Vectorial: http://localhost:6333"
                echo "  - Dashboard: http://localhost:6333/dashboard"
                ;;
            "Phoenix")
                echo "  - UI: http://localhost:6006"
                echo "  - Collector: http://localhost:6006/v1/traces"
                echo "  - gRPC: localhost:4317"
                ;;
        esac
    else
        print_error "Error al iniciar $service_name"
        return 1
    fi
}

# Function to stop a service
stop_service() {
    local service_dir=$1
    local service_name=$2
    
    print_status "Deteniendo $service_name..."
    
    if [ ! -f "$service_dir/docker-compose.yml" ]; then
        print_error "docker-compose.yml no encontrado en $service_dir"
        return 1
    fi
    
    cd "$service_dir"
    
    if ! is_service_running "$service_dir" "$service_name"; then
        print_warning "$service_name no está ejecutándose"
        return 0
    fi
    
    docker-compose down
    
    if [ $? -eq 0 ]; then
        print_status "$service_name detenido exitosamente"
    else
        print_error "Error al detener $service_name"
        return 1
    fi
}

# Function to restart a service
restart_service() {
    local service_dir=$1
    local service_name=$2
    
    print_status "Reiniciando $service_name..."
    stop_service "$service_dir" "$service_name"
    sleep 2
    start_service "$service_dir" "$service_name"
}

# Function to show service status
show_status() {
    local service_dir=$1
    local service_name=$2
    
    if is_service_running "$service_dir" "$service_name"; then
        echo -e "  ${GREEN}●${NC} $service_name: Ejecutándose"
    else
        echo -e "  ${RED}●${NC} $service_name: Detenido"
    fi
}

# Function to show logs
show_logs() {
    local service_dir=$1
    local service_name=$2
    
    print_status "Mostrando logs para $service_name (Presiona Ctrl+C para salir)..."
    
    if [ ! -f "$service_dir/docker-compose.yml" ]; then
        print_error "docker-compose.yml no encontrado en $service_dir"
        return 1
    fi
    
    cd "$service_dir"
    docker-compose logs -f
}

# Main menu function
show_menu() {
    print_header
    
    echo "Servicios disponibles:"
    echo "  1. Qdrant (Base de Datos Vectorial)"
    echo "  2. Phoenix (Monitoreo y Observabilidad)"
    echo "  3. Todos los Servicios"
    echo
    echo "Acciones:"
    echo "  s) Iniciar servicio"
    echo "  t) Detener servicio"
    echo "  r) Reiniciar servicio"
    echo "  l) Mostrar logs"
    echo "  k) Mostrar estado"
    echo "  q) Salir"
    echo
}

# Main script logic
main() {
    # Check if Docker is running
    check_docker
    
    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    QDRANT_DIR="$SCRIPT_DIR/vectordb"
    PHOENIX_DIR="$SCRIPT_DIR/monitoring"
    
    while true; do
        show_menu
        
        # Show current status
        echo "Estado actual:"
        show_status "$QDRANT_DIR" "Qdrant"
        show_status "$PHOENIX_DIR" "Phoenix"
        echo
        
        read -p "Selecciona una acción: " action
        
        case $action in
            s)
                echo
                echo "Selecciona el servicio a iniciar:"
                echo "  1) Qdrant"
                echo "  2) Phoenix"
                echo "  3) Todos los Servicios"
                read -p "Ingresa tu opción (1-3): " service_choice
                
                case $service_choice in
                    1)
                        start_service "$QDRANT_DIR" "Qdrant"
                        ;;
                    2)
                        start_service "$PHOENIX_DIR" "Phoenix"
                        ;;
                    3)
                        start_service "$QDRANT_DIR" "Qdrant"
                        start_service "$PHOENIX_DIR" "Phoenix"
                        ;;
                    *)
                        print_error "Opción inválida"
                        ;;
                esac
                ;;
            t)
                echo
                echo "Selecciona el servicio a detener:"
                echo "  1) Qdrant"
                echo "  2) Phoenix"
                echo "  3) Todos los Servicios"
                read -p "Ingresa tu opción (1-3): " service_choice
                
                case $service_choice in
                    1)
                        stop_service "$QDRANT_DIR" "Qdrant"
                        ;;
                    2)
                        stop_service "$PHOENIX_DIR" "Phoenix"
                        ;;
                    3)
                        stop_service "$QDRANT_DIR" "Qdrant"
                        stop_service "$PHOENIX_DIR" "Phoenix"
                        ;;
                    *)
                        print_error "Opción inválida"
                        ;;
                esac
                ;;
            r)
                echo
                echo "Selecciona el servicio a reiniciar:"
                echo "  1) Qdrant"
                echo "  2) Phoenix"
                echo "  3) Todos los Servicios"
                read -p "Ingresa tu opción (1-3): " service_choice
                
                case $service_choice in
                    1)
                        restart_service "$QDRANT_DIR" "Qdrant"
                        ;;
                    2)
                        restart_service "$PHOENIX_DIR" "Phoenix"
                        ;;
                    3)
                        restart_service "$QDRANT_DIR" "Qdrant"
                        restart_service "$PHOENIX_DIR" "Phoenix"
                        ;;
                    *)
                        print_error "Opción inválida"
                        ;;
                esac
                ;;
            l)
                echo
                echo "Selecciona el servicio para mostrar logs:"
                echo "  1) Qdrant"
                echo "  2) Phoenix"
                read -p "Ingresa tu opción (1-2): " service_choice
                
                case $service_choice in
                    1)
                        show_logs "$QDRANT_DIR" "Qdrant"
                        ;;
                    2)
                        show_logs "$PHOENIX_DIR" "Phoenix"
                        ;;
                    *)
                        print_error "Opción inválida"
                        ;;
                esac
                ;;
            k)
                echo
                echo "Estado de los Servicios:"
                show_status "$QDRANT_DIR" "Qdrant"
                show_status "$PHOENIX_DIR" "Phoenix"
                echo
                read -p "Presiona Enter para continuar..."
                ;;
            q)
                print_status "¡Hasta luego!"
                exit 0
                ;;
            *)
                print_error "Opción inválida. Por favor intenta de nuevo."
                ;;
        esac
        
        echo
        read -p "Presiona Enter para continuar..."
        clear
    done
}

# Run main function
main "$@"
