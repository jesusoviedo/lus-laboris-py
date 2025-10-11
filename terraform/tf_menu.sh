#!/bin/bash

# Determine the project root (one level above the location of this script)
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR/..")"
CRED_DIR="$PROJECT_ROOT/.gcpcredentials"
ENV_FILE="$PROJECT_ROOT/.env"
TFVARS_FILE="$SCRIPT_DIR/terraform.tfvars"

set_gac() {
  CRED_FILE=$(find "$CRED_DIR" -maxdepth 1 -name '*.json' | head -n 1)
  if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    if [ -n "$CRED_FILE" ]; then
      export GOOGLE_APPLICATION_CREDENTIALS="$CRED_FILE"
      echo "✅ Variable GOOGLE_APPLICATION_CREDENTIALS seteada"
    else
      echo "⚠️  No se encontró archivo .json en $CRED_DIR. Terraform puede fallar si requiere autenticación."
    fi
  else
    echo "ℹ️  GOOGLE_APPLICATION_CREDENTIALS ya está seteada: $GOOGLE_APPLICATION_CREDENTIALS"
  fi
}

# Helper function to read environment variables safely
read_env_var() {
  local var_name="$1"
  local file_path="$2"
  # Use grep with regex to handle whitespace and ignore comments
  # Extract only the value after the = sign, trimming whitespace
  grep -E "^[[:space:]]*${var_name}[[:space:]]*=" "$file_path" | head -1 | sed "s/^[[:space:]]*${var_name}[[:space:]]*=[[:space:]]*//"
}

create_tfvars() {
  if [ -f "$ENV_FILE" ]; then
    # Load all environment variables from .env file to make them available for envsubst
    set -a  # automatically export all variables
    source "$ENV_FILE"
    set +a  # stop automatically exporting

    # Read existing variables (ignore comments and handle whitespace)
    GCP_PROJECT_ID=$(read_env_var "GCP_PROJECT_ID" "$ENV_FILE")
    GCP_PROJECT_NUMBER=$(read_env_var "GCP_PROJECT_NUMBER" "$ENV_FILE")
    GCP_REGION=$(read_env_var "GCP_REGION" "$ENV_FILE")
    GCP_BUCKET_NAME=$(read_env_var "GCP_BUCKET_NAME" "$ENV_FILE")
    GCP_CLOUD_RUN_BATCH_JOB_NAME=$(read_env_var "GCP_CLOUD_RUN_BATCH_JOB_NAME" "$ENV_FILE")
    GCP_CLOUD_RUN_BATCH_IMAGE=$(read_env_var "GCP_CLOUD_RUN_BATCH_IMAGE" "$ENV_FILE")
    GCP_CLOUD_RUN_BATCH_ARGS=$(read_env_var "GCP_CLOUD_RUN_BATCH_ARGS" "$ENV_FILE" | sed 's/^"//' | sed 's/"$//')
    GCP_CLOUD_RUN_BATCH_SCHEDULE=$(read_env_var "GCP_CLOUD_RUN_BATCH_SCHEDULE" "$ENV_FILE" | sed 's/^"//' | sed 's/"$//')
    GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL=$(read_env_var "GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL" "$ENV_FILE")

    # Expand environment variables in GCP_CLOUD_RUN_BATCH_ARGS
    # This allows using ${VARIABLE_NAME} syntax in the args string
    if [ -n "$GCP_CLOUD_RUN_BATCH_ARGS" ]; then
        GCP_CLOUD_RUN_BATCH_ARGS=$(envsubst <<< "$GCP_CLOUD_RUN_BATCH_ARGS")
    fi

    # Read new Qdrant VM variables
    GCP_COMPUTE_ENGINE_VM_NAME=$(read_env_var "GCP_COMPUTE_ENGINE_VM_NAME" "$ENV_FILE")
    GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE=$(read_env_var "GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE" "$ENV_FILE")
    GCP_COMPUTE_ENGINE_VM_ZONE=$(read_env_var "GCP_COMPUTE_ENGINE_VM_ZONE" "$ENV_FILE")
    GCP_COMPUTE_ENGINE_VM_DISK_SIZE=$(read_env_var "GCP_COMPUTE_ENGINE_VM_DISK_SIZE" "$ENV_FILE")

    # Read Cloud Run API variables (only infrastructure-related)
    # Application configuration (Qdrant, JWT, etc.) comes from .env in Secret Manager
    GCP_CLOUD_RUN_API_SERVICE_NAME=$(read_env_var "GCP_CLOUD_RUN_API_SERVICE_NAME" "$ENV_FILE")
    GCP_CLOUD_RUN_API_IMAGE=$(read_env_var "GCP_CLOUD_RUN_API_IMAGE" "$ENV_FILE")
    GCP_CLOUD_RUN_API_CONTAINER_PORT=$(read_env_var "GCP_CLOUD_RUN_API_CONTAINER_PORT" "$ENV_FILE")
    GCP_CLOUD_RUN_API_CPU=$(read_env_var "GCP_CLOUD_RUN_API_CPU" "$ENV_FILE" | sed 's/^"//' | sed 's/"$//')
    GCP_CLOUD_RUN_API_MEMORY=$(read_env_var "GCP_CLOUD_RUN_API_MEMORY" "$ENV_FILE" | sed 's/^"//' | sed 's/"$//')
    GCP_CLOUD_RUN_API_MIN_INSTANCES=$(read_env_var "GCP_CLOUD_RUN_API_MIN_INSTANCES" "$ENV_FILE")
    GCP_CLOUD_RUN_API_MAX_INSTANCES=$(read_env_var "GCP_CLOUD_RUN_API_MAX_INSTANCES" "$ENV_FILE")
    GCP_CLOUD_RUN_API_TIMEOUT=$(read_env_var "GCP_CLOUD_RUN_API_TIMEOUT" "$ENV_FILE" | sed 's/^"//' | sed 's/"$//')
    # Validate that all required variables exist
    MISSING_VARS=()

    # Check existing variables
    [[ -z "$GCP_PROJECT_ID" ]] && MISSING_VARS+=("GCP_PROJECT_ID")
    [[ -z "$GCP_PROJECT_NUMBER" ]] && MISSING_VARS+=("GCP_PROJECT_NUMBER")
    [[ -z "$GCP_REGION" ]] && MISSING_VARS+=("GCP_REGION")
    [[ -z "$GCP_BUCKET_NAME" ]] && MISSING_VARS+=("GCP_BUCKET_NAME")
    [[ -z "$GCP_CLOUD_RUN_BATCH_JOB_NAME" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_BATCH_JOB_NAME")
    [[ -z "$GCP_CLOUD_RUN_BATCH_SCHEDULE" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_BATCH_SCHEDULE")
    [[ -z "$GCP_CLOUD_RUN_BATCH_IMAGE" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_BATCH_IMAGE")
    [[ -z "$GCP_CLOUD_RUN_BATCH_ARGS" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_BATCH_ARGS")
    [[ -z "$GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL")
    [[ -z "$GCP_COMPUTE_ENGINE_VM_NAME" ]] && MISSING_VARS+=("GCP_COMPUTE_ENGINE_VM_NAME")
    [[ -z "$GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE" ]] && MISSING_VARS+=("GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE")
    [[ -z "$GCP_COMPUTE_ENGINE_VM_ZONE" ]] && MISSING_VARS+=("GCP_COMPUTE_ENGINE_VM_ZONE")
    [[ -z "$GCP_COMPUTE_ENGINE_VM_DISK_SIZE" ]] && MISSING_VARS+=("GCP_COMPUTE_ENGINE_VM_DISK_SIZE")

    # Check Cloud Run API variables (only infrastructure-related)
    [[ -z "$GCP_CLOUD_RUN_API_SERVICE_NAME" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_API_SERVICE_NAME")
    [[ -z "$GCP_CLOUD_RUN_API_IMAGE" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_API_IMAGE")
    [[ -z "$GCP_CLOUD_RUN_API_CONTAINER_PORT" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_API_CONTAINER_PORT")
    [[ -z "$GCP_CLOUD_RUN_API_CPU" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_API_CPU")
    [[ -z "$GCP_CLOUD_RUN_API_MEMORY" ]] && MISSING_VARS+=("GCP_CLOUD_RUN_API_MEMORY")

    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
      echo "❌ ERROR: Faltan variables en $ENV_FILE:"
      printf "  %s\n" "${MISSING_VARS[@]}"
      return 1
    fi

    # Validate Qdrant VM values
    validate_qdrant_vm_vars

    cat > "$TFVARS_FILE" <<EOF
project_id     = "$GCP_PROJECT_ID"
project_number = "$GCP_PROJECT_NUMBER"
region         = "$GCP_REGION"
bucket_name    = "$GCP_BUCKET_NAME"

job_name   = "$GCP_CLOUD_RUN_BATCH_JOB_NAME"
image      = "$GCP_CLOUD_RUN_BATCH_IMAGE"
schedule   = "$GCP_CLOUD_RUN_BATCH_SCHEDULE"
notify_email = "$GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL"

qdrant_vm_name         = "$GCP_COMPUTE_ENGINE_VM_NAME"
qdrant_vm_machine_type = "$GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE"
qdrant_vm_zone        = "$GCP_COMPUTE_ENGINE_VM_ZONE"
qdrant_vm_disk_size   = $GCP_COMPUTE_ENGINE_VM_DISK_SIZE

# Cloud Run Service for API
# Application configuration (Qdrant, JWT, Embedding, etc.) comes from .env in Secret Manager
api_service_name = "$GCP_CLOUD_RUN_API_SERVICE_NAME"
api_image       = "$GCP_CLOUD_RUN_API_IMAGE"
api_container_port = $GCP_CLOUD_RUN_API_CONTAINER_PORT
api_cpu = "$GCP_CLOUD_RUN_API_CPU"
api_memory = "$GCP_CLOUD_RUN_API_MEMORY"
api_min_instance_count = ${GCP_CLOUD_RUN_API_MIN_INSTANCES:-0}
api_max_instance_count = ${GCP_CLOUD_RUN_API_MAX_INSTANCES:-3}
api_timeout = "${GCP_CLOUD_RUN_API_TIMEOUT:-300s}"
EOF
    # Parse args properly to avoid double quotes
    # Note: GCP_CLOUD_RUN_BATCH_ARGS has already been processed to expand environment variables
    ARGS_ARRAY=()
    IFS=' ' read -ra ARGS <<< "$GCP_CLOUD_RUN_BATCH_ARGS"
    for arg in "${ARGS[@]}"; do
        ARGS_ARRAY+=("\"$arg\"")
    done
    ARGS_LIST=$(IFS=', '; echo "${ARGS_ARRAY[*]}")
    echo "args         = [$ARGS_LIST]" >> "$TFVARS_FILE"

    echo "✅ Archivo terraform.tfvars generado correctamente"
  else
    echo "⚠️  No se encontró el archivo .env en $PROJECT_ROOT. No se generó terraform.tfvars."
    return 1
  fi
}

validate_qdrant_vm_vars() {
  # Validate VM name format
  if ! [[ "$GCP_COMPUTE_ENGINE_VM_NAME" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]]; then
    echo "❌ ERROR: GCP_COMPUTE_ENGINE_VM_NAME debe contener solo letras minúsculas, números y guiones, y empezar/terminar con letra/número"
    return 1
  fi

  # Validate machine type format
  if ! [[ "$GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE" =~ ^[a-z][0-9]-[a-z]+$ ]]; then
    echo "❌ ERROR: GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE debe tener formato válido (ej: e2-medium, n1-standard-1)"
    return 1
  fi

  # Validate zone format
  if ! [[ "$GCP_COMPUTE_ENGINE_VM_ZONE" =~ ^[a-z]+-[a-z]+[0-9]+-[a-z]$ ]]; then
    echo "❌ ERROR: GCP_COMPUTE_ENGINE_VM_ZONE debe tener formato válido (ej: southamerica-east1-a, us-central1-a)"
    return 1
  fi

  # Validate disk size is a positive integer
  if ! [[ "$GCP_COMPUTE_ENGINE_VM_DISK_SIZE" =~ ^[0-9]+$ ]] || [ "$GCP_COMPUTE_ENGINE_VM_DISK_SIZE" -lt 10 ]; then
    echo "❌ ERROR: GCP_COMPUTE_ENGINE_VM_DISK_SIZE debe ser un número entero mayor a 10 GB"
    return 1
  fi

  # Validate disk size is reasonable (max 2000 GB)
  if [ "$GCP_COMPUTE_ENGINE_VM_DISK_SIZE" -gt 2000 ]; then
    echo "❌ ERROR: GCP_COMPUTE_ENGINE_VM_DISK_SIZE no puede ser mayor a 2000 GB"
    return 1
  fi

}

validate_env() {
  if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ ERROR: La variable de entorno GOOGLE_APPLICATION_CREDENTIALS no está seteada. Usa la opción 1 del menú."
    return 1
  fi
  if [ ! -f "$TFVARS_FILE" ]; then
    echo "❌ ERROR: No existe el archivo terraform.tfvars. Usa la opción 2 del menú."
    return 1
  fi
  return 0
}

while true; do
  echo "========= Terraform Menu ========="
  echo "1) Setear GOOGLE_APPLICATION_CREDENTIALS"
  echo "2) Crear archivo terraform.tfvars"
  echo "3) terraform init"
  echo "4) terraform plan"
  echo "5) terraform apply"
  echo "6) terraform destroy"
  echo "7) Salir"
  read -p "Seleccione una opción: " opt
  case $opt in
    1)
      set_gac
      ;;
    2)
      create_tfvars
      ;;
    3)
      validate_env && terraform init
      ;;
    4)
      validate_env && terraform plan
      ;;
    5)
      validate_env && terraform apply
      ;;
    6)
      validate_env && terraform destroy
      ;;
    7)
      echo "Saliendo..."
      break
      ;;
    *)
      echo "Opción inválida. Intente de nuevo."
      ;;
  esac
done
