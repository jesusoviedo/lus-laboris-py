#!/bin/bash

# Interactive script to run GitHub Actions workflows with act
# Must be run from .github/workflows/
# The .env file is assumed to be at the repo root (two levels up)
# The GSA_KEY credentials file is automatically searched in ../../.gcpcredentials/*.json

set -e

# Required variables per workflow
WORKFLOW1="docker-processing-build-publish.yml"
WORKFLOW2="docker-api-build-publish.yml"
WORKFLOW3="terraform-apply-on-tf-change.yml"
WORKFLOW4="deploy-qdrant.yml"

REQUIRED_VARS_WORKFLOW1=(
  "DOCKER_HUB_USERNAME"
  "DOCKER_HUB_PASSWORD"
  "DOCKER_IMAGE_NAME_PROCESSING"
)
REQUIRED_VARS_WORKFLOW2=(
  "DOCKER_HUB_USERNAME"
  "DOCKER_HUB_PASSWORD"
  "DOCKER_IMAGE_NAME_RAG_API"
)
REQUIRED_VARS_WORKFLOW3=(
  "GCP_PROJECT_ID"
  "GCP_REGION"
  "GSA_KEY"
  "GCP_BUCKET_NAME"
  "GCP_CLOUD_RUN_BATCH_JOB_NAME"
  "GCP_CLOUD_RUN_BATCH_SCHEDULE"
  "GCP_CLOUD_RUN_BATCH_IMAGE"
  "GCP_CLOUD_RUN_BATCH_ARGS"
  "GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL"
  "QDRANT_VM_NAME"
  "QDRANT_VM_MACHINE_TYPE"
  "QDRANT_VM_ZONE"
  "QDRANT_VM_DISK_SIZE"
  "GCP_CLOUD_RUN_API_SERVICE_NAME"
  "GCP_CLOUD_RUN_API_IMAGE"
  "GCP_CLOUD_RUN_API_CONTAINER_PORT"
  "GCP_CLOUD_RUN_API_LOG_LEVEL"
  "GCP_CLOUD_RUN_API_QDRANT_URL"
  "GCP_CLOUD_RUN_API_QDRANT_API_KEY"
  "GCP_CLOUD_RUN_API_QDRANT_COLLECTION_NAME"
  "GCP_CLOUD_RUN_API_EMBEDDING_MODEL"
  "GCP_CLOUD_RUN_API_GCP_CREDENTIALS_PATH"
  "GCP_CLOUD_RUN_API_EMBEDDING_BATCH_SIZE"
  "GCP_CLOUD_RUN_API_JWT_PUBLIC_KEY_PATH"
  "GCP_CLOUD_RUN_API_ALLOWED_ORIGINS"
  "GCP_CLOUD_RUN_API_ALLOWED_HOSTS"
  "GCP_CLOUD_RUN_API_CPU"
  "GCP_CLOUD_RUN_API_MEMORY"
  "GCP_CLOUD_RUN_API_MIN_INSTANCES"
  "GCP_CLOUD_RUN_API_MAX_INSTANCES"
  "GCP_CLOUD_RUN_API_TIMEOUT"
)
REQUIRED_VARS_WORKFLOW4=(
  "GCP_PROJECT_ID"
  "GCP_REGION"
  "GSA_KEY"
  "QDRANT_API_KEY"
)

# List of variables that should be treated as secrets (use -s instead of --var)
SECRET_VARS=(
  "DOCKER_HUB_USERNAME"
  "DOCKER_HUB_PASSWORD"
  "GSA_KEY"
  "GCP_PROJECT_ID"
  "GCP_REGION"
  "QDRANT_API_KEY"
  "GCP_CLOUD_RUN_API_QDRANT_API_KEY"
  # Add more secret variables here as needed
)

# Paths
ENV_FILE="../../.env"
GCP_CREDENTIALS_DIR="../../.gcpcredentials"

if [ ! -f "$ENV_FILE" ]; then
  echo "\n[ERROR] No se encontró el archivo .env en $ENV_FILE.\n"
  exit 1
fi

# Find the first .json file in .gcpcredentials
find_gsa_key_file() {
  local file=$(find "$GCP_CREDENTIALS_DIR" -maxdepth 1 -type f -name '*.json' | head -n 1)
  echo "$file"
}

# Function to get the value of a variable from .env
get_env_var() {
  local var="$1"
  grep -E "^$var=" "$ENV_FILE" | tail -n1 | cut -d'=' -f2-
}

# Function to check if a variable is in the secrets list
is_secret() {
  local var="$1"
  for secret in "${SECRET_VARS[@]}"; do
    if [ "$var" = "$secret" ]; then
      return 0
    fi
  done
  return 1
}

# Function to validate variables
validar_vars() {
  local missing=()
  for var in "$@"; do
    if [ "$var" = "GSA_KEY" ]; then
      GSA_KEY_FILE=$(find_gsa_key_file)
      if [ -z "$GSA_KEY_FILE" ] || [ ! -f "$GSA_KEY_FILE" ]; then
        missing+=("GSA_KEY (no se encontró archivo .json en $GCP_CREDENTIALS_DIR)")
      fi
    else
      local value=$(get_env_var "$var")
      if [ -z "$value" ]; then
        missing+=("$var")
      fi
    fi
  done
  if [ ${#missing[@]} -ne 0 ]; then
    echo "\n[ERROR] Faltan las siguientes variables o archivos requeridos:"
    for var in "${missing[@]}"; do
      echo "  - $var"
    done
    echo "\nPor favor, agréguelas antes de continuar."
    exit 2
  fi
}

# Menu
echo "\nSeleccione el workflow a ejecutar:\n"
echo "1) Build & Publish Docker Image (processing)"
echo "2) Build & Publish Docker Image (API)"
echo "3) Terraform Apply on .tf Change"
echo "4) Deploy Qdrant to VM"
echo "0) Salir"
read -p $'\nOpción: ' opcion

case $opcion in
  1)
    WORKFLOW="$WORKFLOW1"
    VARS=("${REQUIRED_VARS_WORKFLOW1[@]}")
    ;;
  2)
    WORKFLOW="$WORKFLOW2"
    VARS=("${REQUIRED_VARS_WORKFLOW2[@]}")
    ;;
  3)
    WORKFLOW="$WORKFLOW3"
    VARS=("${REQUIRED_VARS_WORKFLOW3[@]}")
    ;;
  4)
    WORKFLOW="$WORKFLOW4"
    VARS=("${REQUIRED_VARS_WORKFLOW4[@]}")
    ;;
  0)
    echo "Saliendo."
    exit 0
    ;;
  *)
    echo "Opción no válida."
    exit 1
    ;;
esac

# Validate variables
validar_vars "${VARS[@]}"

# Always try Docker login if credentials are present in .env
DOCKER_HUB_USERNAME=$(grep '^DOCKER_HUB_USERNAME=' "$ENV_FILE" | cut -d'=' -f2-)
DOCKER_HUB_PASSWORD=$(grep '^DOCKER_HUB_PASSWORD=' "$ENV_FILE" | cut -d'=' -f2-)
if [[ -n "$DOCKER_HUB_USERNAME" && -n "$DOCKER_HUB_PASSWORD" ]]; then
  echo "$DOCKER_HUB_PASSWORD" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin > /dev/null 2>&1 || {
    echo "⚠️  Docker login failed. You may not be able to pull/push images.";
  }
else
  echo "⚠️  Docker Hub credentials not found in .env. Skipping docker login."
fi

# Build arguments
declare -a ACT_SECRETS=()
declare -a ACT_VARS=()
for var in "${VARS[@]}"; do
  if [ "$var" = "GSA_KEY" ]; then
    GSA_KEY_FILE=$(find_gsa_key_file)
    value=$(cat "$GSA_KEY_FILE" | tr -d '\n' | sed 's/"/\\"/g')
    ACT_SECRETS+=("-s" "GSA_KEY=$value")
  else
    value=$(get_env_var "$var")
    # Check if variable is in the secrets list
    if is_secret "$var"; then
      ACT_SECRETS+=("-s" "$var=$value")
    else
      # Use --var for environment variables
      ACT_VARS+=("--var" "$var=$value")
    fi
  fi
done

# Show and run command (hiding values)
CMD="cd ../../ && act -W \".github/workflows/$WORKFLOW\" ${ACT_VARS[@]} ${ACT_SECRETS[@]}"

# Build hidden version of the command to display
ACT_VARS_HIDDEN=()
ACT_SECRETS_HIDDEN=()
for var in "${VARS[@]}"; do
  if [ "$var" = "GSA_KEY" ]; then
    ACT_SECRETS_HIDDEN+=("-s" "$var=****")
  else
    # Check if variable is in the secrets list
    if is_secret "$var"; then
      ACT_SECRETS_HIDDEN+=("-s" "$var=****")
    else
      ACT_VARS_HIDDEN+=("--var" "$var=****")
    fi
  fi
done


CMD_HIDDEN="cd ../../ && act -W \".github/workflows/$WORKFLOW\" ${ACT_VARS_HIDDEN[@]} ${ACT_SECRETS_HIDDEN[@]}"

echo -e "\nComando a ejecutar (valores ocultos):\n$CMD_HIDDEN\n"
read -p "¿Desea continuar? (s/n): " confirm
if [[ "$confirm" =~ ^[sS]$ ]]; then
  eval $CMD
else
  echo "Cancelado."
fi
