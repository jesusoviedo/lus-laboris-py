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
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Services Management Script${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
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
    
    print_status "Starting $service_name..."
    
    if [ ! -f "$service_dir/docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in $service_dir"
        return 1
    fi
    
    cd "$service_dir"
    
    if is_service_running "$service_dir" "$service_name"; then
        print_warning "$service_name is already running"
        return 0
    fi
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_status "$service_name started successfully"
        
        # Show service-specific information
        case $service_name in
            "Qdrant")
                echo "  - Vector Database: http://localhost:6333"
                echo "  - Dashboard: http://localhost:6333/dashboard"
                ;;
            "Phoenix")
                echo "  - UI: http://localhost:6006"
                echo "  - Collector: http://localhost:6006/v1/traces"
                echo "  - gRPC: localhost:4317"
                ;;
        esac
    else
        print_error "Failed to start $service_name"
        return 1
    fi
}

# Function to stop a service
stop_service() {
    local service_dir=$1
    local service_name=$2
    
    print_status "Stopping $service_name..."
    
    if [ ! -f "$service_dir/docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in $service_dir"
        return 1
    fi
    
    cd "$service_dir"
    
    if ! is_service_running "$service_dir" "$service_name"; then
        print_warning "$service_name is not running"
        return 0
    fi
    
    docker-compose down
    
    if [ $? -eq 0 ]; then
        print_status "$service_name stopped successfully"
    else
        print_error "Failed to stop $service_name"
        return 1
    fi
}

# Function to restart a service
restart_service() {
    local service_dir=$1
    local service_name=$2
    
    print_status "Restarting $service_name..."
    stop_service "$service_dir" "$service_name"
    sleep 2
    start_service "$service_dir" "$service_name"
}

# Function to show service status
show_status() {
    local service_dir=$1
    local service_name=$2
    
    if is_service_running "$service_dir" "$service_name"; then
        echo -e "  ${GREEN}●${NC} $service_name: Running"
    else
        echo -e "  ${RED}●${NC} $service_name: Stopped"
    fi
}

# Function to show logs
show_logs() {
    local service_dir=$1
    local service_name=$2
    
    print_status "Showing logs for $service_name (Press Ctrl+C to exit)..."
    
    if [ ! -f "$service_dir/docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in $service_dir"
        return 1
    fi
    
    cd "$service_dir"
    docker-compose logs -f
}

# Main menu function
show_menu() {
    print_header
    
    echo "Available services:"
    echo "  1. Qdrant (Vector Database)"
    echo "  2. Phoenix (Monitoring & Observability)"
    echo "  3. All Services"
    echo
    echo "Actions:"
    echo "  s) Start service"
    echo "  t) Stop service"
    echo "  r) Restart service"
    echo "  l) Show logs"
    echo "  k) Show status"
    echo "  q) Quit"
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
        echo "Current status:"
        show_status "$QDRANT_DIR" "Qdrant"
        show_status "$PHOENIX_DIR" "Phoenix"
        echo
        
        read -p "Select action: " action
        
        case $action in
            s)
                echo
                echo "Select service to start:"
                echo "  1) Qdrant"
                echo "  2) Phoenix"
                echo "  3) All Services"
                read -p "Enter choice (1-3): " service_choice
                
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
                        print_error "Invalid choice"
                        ;;
                esac
                ;;
            t)
                echo
                echo "Select service to stop:"
                echo "  1) Qdrant"
                echo "  2) Phoenix"
                echo "  3) All Services"
                read -p "Enter choice (1-3): " service_choice
                
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
                        print_error "Invalid choice"
                        ;;
                esac
                ;;
            r)
                echo
                echo "Select service to restart:"
                echo "  1) Qdrant"
                echo "  2) Phoenix"
                echo "  3) All Services"
                read -p "Enter choice (1-3): " service_choice
                
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
                        print_error "Invalid choice"
                        ;;
                esac
                ;;
            l)
                echo
                echo "Select service to show logs:"
                echo "  1) Qdrant"
                echo "  2) Phoenix"
                read -p "Enter choice (1-2): " service_choice
                
                case $service_choice in
                    1)
                        show_logs "$QDRANT_DIR" "Qdrant"
                        ;;
                    2)
                        show_logs "$PHOENIX_DIR" "Phoenix"
                        ;;
                    *)
                        print_error "Invalid choice"
                        ;;
                esac
                ;;
            k)
                echo
                echo "Service Status:"
                show_status "$QDRANT_DIR" "Qdrant"
                show_status "$PHOENIX_DIR" "Phoenix"
                echo
                read -p "Press Enter to continue..."
                ;;
            q)
                print_status "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please try again."
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
        clear
    done
}

# Run main function
main "$@"
