#!/bin/bash

# Interactive script to run GitHub Actions workflows with act
# Must be run from .github/workflows/
# The .env file is assumed to be at the repo root (two levels up)
# The GSA_KEY credentials file is automatically searched in ../../.gcpcredentials/*.json

set -e

# login en docker hub
echo "$DOCKER_HUB_PASSWORD" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin

# Required variables per workflow
WORKFLOW1="docker-processing-build-publish.yml"
WORKFLOW2="terraform-apply-on-tf-change.yml"

REQUIRED_VARS_WORKFLOW1=(
  "DOCKER_HUB_USERNAME"
  "DOCKER_HUB_PASSWORD"
  "DOCKER_IMAGE_NAME_PROCESSING"
)
REQUIRED_VARS_WORKFLOW2=(
  "GCP_PROJECT_ID"
  "GCP_REGION"
  "GSA_KEY"
  "GCP_CLOUD_RUN_BATCH_JOB_NAME"
  "GCP_CLOUD_RUN_BATCH_ARGS"
  "GCP_BUCKET_NAME"
  "GCP_CLOUD_RUN_BATCH_IMAGE"
  "GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL"
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
echo "2) Terraform Apply on .tf Change"
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

# Build arguments
ENV_PREFIX=""
declare -a ACT_SECRETS=()
for var in "${VARS[@]}"; do
  if [ "$var" = "GSA_KEY" ]; then
    GSA_KEY_FILE=$(find_gsa_key_file)
    value=$(cat "$GSA_KEY_FILE" | tr -d '\n' | sed 's/"/\\"/g')
    ACT_SECRETS+=("-s" "GSA_KEY=$value")
  else
    value=$(get_env_var "$var")
    # If the name contains PASSWORD, SECRET, KEY, USERNAME, TOKEN => -s, else => env
    if [[ "$var" =~ (PASSWORD|SECRET|KEY|TOKEN|USERNAME) ]]; then
      ACT_SECRETS+=("-s" "$var=$value")
    else
      # Concatenate to environment prefix
      ENV_PREFIX+="$var='$value' "
    fi
  fi
done

# Show and run command (hiding values)
CMD="${ENV_PREFIX}act -W \"$WORKFLOW\" ${ACT_SECRETS[@]}"

# Build hidden version of the command to display
ENV_PREFIX_HIDDEN=""
ACT_SECRETS_HIDDEN=()
for var in "${VARS[@]}"; do
  if [ "$var" = "GSA_KEY" ]; then
    ACT_SECRETS_HIDDEN+=("-s" "$var=****")
  else
    # If the name contains PASSWORD, SECRET, KEY, USERNAME, TOKEN => -s, else => env
    if [[ "$var" =~ (PASSWORD|SECRET|KEY|TOKEN|USERNAME) ]]; then
      ACT_SECRETS_HIDDEN+=("-s" "$var=****")
    else
      ENV_PREFIX_HIDDEN+="$var='****' "
    fi
  fi
done
CMD_HIDDEN="${ENV_PREFIX_HIDDEN}act -W \"$WORKFLOW\" ${ACT_SECRETS_HIDDEN[@]}"

echo -e "\nComando a ejecutar (valores ocultos):\n$CMD_HIDDEN\n"
read -p "¿Desea continuar? (s/n): " confirm
if [[ "$confirm" =~ ^[sS]$ ]]; then
  eval $CMD
else
  echo "Cancelado."
fi
