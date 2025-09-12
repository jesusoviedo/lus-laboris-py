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

create_tfvars() {
  if [ -f "$ENV_FILE" ]; then
    GCP_PROJECT_ID=$(grep '^GCP_PROJECT_ID=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_REGION=$(grep '^GCP_REGION=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_BUCKET_NAME=$(grep '^GCP_BUCKET_NAME=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_JOB_NAME=$(grep '^GCP_CLOUD_RUN_BATCH_JOB_NAME=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_IMAGE=$(grep '^GCP_CLOUD_RUN_BATCH_IMAGE=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_ARGS=$(grep '^GCP_CLOUD_RUN_BATCH_ARGS=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_SCHEDULE=$(grep '^GCP_CLOUD_RUN_BATCH_SCHEDULE=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL=$(grep '^GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL=' "$ENV_FILE" | cut -d '=' -f2-)

    # Validate that all required variables exist
    if [[ -z "$GCP_PROJECT_ID" || -z "$GCP_REGION" || -z "$GCP_BUCKET_NAME" || -z "$GCP_CLOUD_RUN_BATCH_JOB_NAME" || -z "$GCP_CLOUD_RUN_BATCH_SCHEDULE" || -z "$GCP_CLOUD_RUN_BATCH_IMAGE" || -z "$GCP_CLOUD_RUN_BATCH_ARGS" || -z "$GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL" ]]; then
      echo "❌ ERROR: Faltan variables en $ENV_FILE. Se requieren:"
      echo "  GCP_PROJECT_ID, GCP_REGION, GCP_BUCKET_NAME, GCP_CLOUD_RUN_BATCH_JOB_NAME, GCP_CLOUD_RUN_BATCH_SCHEDULE, GCP_CLOUD_RUN_BATCH_IMAGE, GCP_CLOUD_RUN_BATCH_ARGS, GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL"
      return 1
    fi
    cat > "$TFVARS_FILE" <<EOF
project_id   = "$GCP_PROJECT_ID"
region       = "$GCP_REGION"
bucket_name  = "$GCP_BUCKET_NAME"
job_name     = "$GCP_CLOUD_RUN_BATCH_JOB_NAME"
schedule     = "$GCP_CLOUD_RUN_BATCH_SCHEDULE"
image        = "$GCP_CLOUD_RUN_BATCH_IMAGE"
EOF
    ARGS_LIST=$(echo $GCP_CLOUD_RUN_BATCH_ARGS | awk '{for(i=1;i<=NF;i++) printf "\"%s\"%s", $i, (i<NF?", ":"") }')
    echo "args         = [$ARGS_LIST]" >> "$TFVARS_FILE"
    echo "notify_email = \"$GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL\"" >> "$TFVARS_FILE"
    echo "✅ Archivo terraform.tfvars generado correctamente"
  else
    echo "⚠️  No se encontró el archivo .env en $PROJECT_ROOT. No se generó terraform.tfvars."
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
