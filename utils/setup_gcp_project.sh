#!/bin/bash

# =============================================================================
# GCP Project Setup Script
# =============================================================================
# This script automates the setup of a Google Cloud Platform project
# with all necessary APIs, service accounts, and permissions for the
# Py Labor Law RAG project.
# =============================================================================

set -e  # Exit on any error

# =============================================================================
# CONFIGURATION
# =============================================================================

# Default values
DEFAULT_PROJECT_NAME="Py Labor Law RAG"
DEFAULT_PROJECT_ID="py-labor-law-rag"
DEFAULT_REGION="southamerica-east1"
DEFAULT_ZONE="southamerica-east1-a"
DEFAULT_SERVICE_ACCOUNT_NAME="lus-laboris-py-service-account"
DEFAULT_DISPLAY_NAME="Lus Laboris Py Service Account"
DEFAULT_DESCRIPTION="Service account for Py Labor Law RAG project"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_success() {
    echo -e "${CYAN}[SUCCESS]${NC} $1"
}

# Function to check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first:"
        echo "  https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    log_info "gcloud CLI found: $(gcloud version --format='value(Google Cloud SDK)')"
}

# Function to check if user is authenticated
check_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_warn "No active authentication found. Please run: gcloud auth login"
        exit 1
    fi
    log_info "Authenticated as: $(gcloud auth list --filter=status:ACTIVE --format="value(account)")"
}

# Function to prompt for user input with default
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"

    echo -n "$prompt [$default]: "
    read -r input
    eval "$var_name=\"\${input:-$default}\""
}

# Function to validate project ID format
validate_project_id() {
    local project_id="$1"
    if [[ ! "$project_id" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
        log_error "Invalid project ID format. Must contain only lowercase letters, numbers, and hyphens, and start/end with alphanumeric character."
        return 1
    fi
    return 0
}

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

# Step 1: Create Project
create_project() {
    log_step "Creating GCP Project..."

    prompt_with_default "Enter project name" "$DEFAULT_PROJECT_NAME" "PROJECT_NAME"
    prompt_with_default "Enter project ID" "$DEFAULT_PROJECT_ID" "PROJECT_ID"

    if ! validate_project_id "$PROJECT_ID"; then
        return 1
    fi

    # Check if project already exists
    if gcloud projects describe "$PROJECT_ID" &>/dev/null; then
        log_warn "Project $PROJECT_ID already exists. Using existing project."
    else
        log_info "Creating project: $PROJECT_NAME ($PROJECT_ID)"
        if gcloud projects create "$PROJECT_ID" --name="$PROJECT_NAME"; then
            log_success "Project created successfully"
        else
            log_error "Failed to create project"
            return 1
        fi
    fi

    # Set the project as active
    log_info "Setting project as active..."
    gcloud config set project "$PROJECT_ID"
    log_success "Project $PROJECT_ID is now active"
}

# Step 2: Enable Required APIs
enable_apis() {
    log_step "Enabling required APIs..."

    local apis=(
        "storage.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "compute.googleapis.com"
        "run.googleapis.com"
        "cloudscheduler.googleapis.com"
        "iam.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
        "secretmanager.googleapis.com"
    )

    for api in "${apis[@]}"; do
        log_info "Enabling $api..."
        if gcloud services enable "$api"; then
            log_success "$api enabled"
        else
            log_error "Failed to enable $api"
            return 1
        fi
    done

    log_success "All APIs enabled successfully"
}

# Step 2.5: Create App Engine Application
create_app_engine() {
    log_step "Creating App Engine application..."

    # Check if App Engine already exists
    if gcloud app describe --project="$PROJECT_ID" &>/dev/null; then
        log_warn "App Engine application already exists in project $PROJECT_ID"
        return 0
    fi

    log_info "Creating App Engine application in region: $REGION"
    log_warn "Note: App Engine is required by Cloud Scheduler in some regions"

    if gcloud app create --region="$REGION" --project="$PROJECT_ID"; then
        log_success "App Engine application created successfully"
    else
        log_error "Failed to create App Engine application"
        log_warn "This may cause issues with Cloud Scheduler"
        return 1
    fi
}

# Step 3: Create Service Account
create_service_account() {
    log_step "Creating Service Account..."

    prompt_with_default "Enter service account name" "$DEFAULT_SERVICE_ACCOUNT_NAME" "SERVICE_ACCOUNT_NAME"
    prompt_with_default "Enter display name" "$DEFAULT_DISPLAY_NAME" "DISPLAY_NAME"
    prompt_with_default "Enter description" "$DEFAULT_DESCRIPTION" "DESCRIPTION"

    local service_account_email="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

    # Check if service account already exists
    if gcloud iam service-accounts describe "$service_account_email" &>/dev/null; then
        log_warn "Service account $service_account_email already exists. Using existing service account."
    else
        log_info "Creating service account: $SERVICE_ACCOUNT_NAME"
        if gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
            --display-name="$DISPLAY_NAME" \
            --description="$DESCRIPTION"; then
            log_success "Service account created successfully"
        else
            log_error "Failed to create service account"
            return 1
        fi
    fi
}

# Step 4: Assign Roles
assign_roles() {
    log_step "Assigning roles to service account..."

    local service_account_email="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

    local roles=(
        "roles/storage.admin"
        "roles/storage.objectAdmin"
        "roles/run.admin"
        "roles/iam.serviceAccountUser"
        "roles/cloudscheduler.admin"
        "roles/compute.instanceAdmin"
        "roles/compute.networkAdmin"
        "roles/compute.securityAdmin"
        "roles/secretmanager.admin"
        "roles/logging.admin"
        "roles/monitoring.notificationChannelEditor"
        "roles/monitoring.alertPolicyEditor"
    )

    for role in "${roles[@]}"; do
        log_info "Assigning role: $role"
        if gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$service_account_email" \
            --role="$role"; then
            log_success "Role $role assigned successfully"
        else
            log_error "Failed to assign role $role"
            return 1
        fi
    done

    log_success "All roles assigned successfully"
}

# Step 5: Generate JSON Key
generate_key() {
    log_step "Generating JSON key..."

    local service_account_email="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
    local key_file=".gcpcredentials/$SERVICE_ACCOUNT_NAME.json"

    # Create credentials directory if it doesn't exist
    mkdir -p .gcpcredentials

    log_info "Generating JSON key for $service_account_email"
    if gcloud iam service-accounts keys create "$key_file" \
        --iam-account="$service_account_email"; then
        log_success "JSON key generated: $key_file"

        # Set proper permissions
        chmod 600 "$key_file"
        log_info "Key file permissions set to 600"
    else
        log_error "Failed to generate JSON key"
        return 1
    fi
}

# Step 6: Verify Setup
verify_setup() {
    log_step "Verifying setup..."

    local service_account_email="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

    # Verify project
    log_info "Verifying project..."
    if gcloud projects describe "$PROJECT_ID" &>/dev/null; then
        log_success "Project verification: OK"
    else
        log_error "Project verification: FAILED"
        return 1
    fi

    # Verify service account
    log_info "Verifying service account..."
    if gcloud iam service-accounts describe "$service_account_email" &>/dev/null; then
        log_success "Service account verification: OK"
    else
        log_error "Service account verification: FAILED"
        return 1
    fi

    # Verify roles
    log_info "Verifying assigned roles..."
    local roles_output
    roles_output=$(gcloud projects get-iam-policy "$PROJECT_ID" \
        --flatten="bindings[].members" \
        --format="table(bindings.role)" \
        --filter="bindings.members:$service_account_email" 2>/dev/null)

    if [[ -n "$roles_output" ]]; then
        log_success "Roles verification: OK"
        echo "$roles_output"
    else
        log_error "Roles verification: FAILED"
        return 1
    fi

    # Test authentication
    log_info "Testing authentication with service account..."
    local key_file=".gcpcredentials/$SERVICE_ACCOUNT_NAME.json"
    if [[ -f "$key_file" ]]; then
        if gcloud auth activate-service-account \
            --key-file="$key_file" &>/dev/null; then
            log_success "Authentication test: OK"
            # Restore original authentication
            gcloud auth login --no-launch-browser &>/dev/null || true
        else
            log_error "Authentication test: FAILED"
            return 1
        fi
    else
        log_error "JSON key file not found: $key_file"
        return 1
    fi

    log_success "All verifications passed!"
}

# =============================================================================
# MENU SYSTEM
# =============================================================================

show_menu() {
    echo
    echo "=========================================="
    echo "    GCP Project Setup Script"
    echo "=========================================="
    echo
    echo "Current configuration:"
    echo "  Project ID: ${PROJECT_ID:-'Not set'}"
    echo "  Service Account: ${SERVICE_ACCOUNT_NAME:-'Not set'}"
    echo
    echo "Available options:"
    echo "  1) Create Project"
    echo "  2) Enable APIs"
    echo "  3) Create App Engine Application"
    echo "  4) Create Service Account"
    echo "  5) Assign Roles"
    echo "  6) Generate JSON Key"
    echo "  7) Verify Setup"
    echo "  8) Full Setup (all steps)"
    echo "  9) Show Configuration"
    echo "  10) Exit"
    echo
}

show_configuration() {
    echo
    echo "=========================================="
    echo "    Current Configuration"
    echo "=========================================="
    echo
    echo "Project Settings:"
    echo "  Project ID: ${PROJECT_ID:-'Not set'}"
    echo "  Project Name: ${PROJECT_NAME:-'Not set'}"
    echo
    echo "Service Account Settings:"
    echo "  Service Account Name: ${SERVICE_ACCOUNT_NAME:-'Not set'}"
    echo "  Display Name: ${DISPLAY_NAME:-'Not set'}"
    echo "  Description: ${DESCRIPTION:-'Not set'}"
    echo
    echo "Files:"
    echo "  JSON Key: .gcpcredentials/${SERVICE_ACCOUNT_NAME:-'service-account'}.json"
    echo
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    echo "=========================================="
    echo "    GCP Project Setup Script"
    echo "    Py Labor Law RAG Project"
    echo "=========================================="
    echo

    # Initial checks
    check_gcloud
    check_auth

    while true; do
        show_menu
        echo -n "Select an option (1-10): "
        read -r choice

        case $choice in
            1)
                create_project
                ;;
            2)
                enable_apis
                ;;
            3)
                create_app_engine
                ;;
            4)
                create_service_account
                ;;
            5)
                assign_roles
                ;;
            6)
                generate_key
                ;;
            7)
                verify_setup
                ;;
            8)
                log_step "Starting full setup..."
                create_project && \
                enable_apis && \
                create_app_engine && \
                create_service_account && \
                assign_roles && \
                generate_key && \
                verify_setup && \
                log_success "Full setup completed successfully!"
                ;;
            9)
                show_configuration
                ;;
            10)
                log_info "Exiting..."
                exit 0
                ;;
            *)
                log_error "Invalid option. Please select 1-10."
                ;;
        esac

        echo
        echo -n "Press Enter to continue..."
        read -r
    done
}

# Run main function
main "$@"
