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
    # Read existing variables
    GCP_PROJECT_ID=$(grep '^GCP_PROJECT_ID=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_REGION=$(grep '^GCP_REGION=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_BUCKET_NAME=$(grep '^GCP_BUCKET_NAME=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_JOB_NAME=$(grep '^GCP_CLOUD_RUN_BATCH_JOB_NAME=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_IMAGE=$(grep '^GCP_CLOUD_RUN_BATCH_IMAGE=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_ARGS=$(grep '^GCP_CLOUD_RUN_BATCH_ARGS=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_SCHEDULE=$(grep '^GCP_CLOUD_RUN_BATCH_SCHEDULE=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL=$(grep '^GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL=' "$ENV_FILE" | cut -d '=' -f2-)
    
    # Read new Qdrant VM variables
    GCP_COMPUTE_ENGINE_VM_NAME=$(grep '^GCP_COMPUTE_ENGINE_VM_NAME=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE=$(grep '^GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_COMPUTE_ENGINE_VM_ZONE=$(grep '^GCP_COMPUTE_ENGINE_VM_ZONE=' "$ENV_FILE" | cut -d '=' -f2-)
    GCP_COMPUTE_ENGINE_VM_DISK_SIZE=$(grep '^GCP_COMPUTE_ENGINE_VM_DISK_SIZE=' "$ENV_FILE" | cut -d '=' -f2-)

    # Validate that all required variables exist
    MISSING_VARS=()
    
    # Check existing variables
    [[ -z "$GCP_PROJECT_ID" ]] && MISSING_VARS+=("GCP_PROJECT_ID")
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

    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
      echo "❌ ERROR: Faltan variables en $ENV_FILE:"
      printf "  %s\n" "${MISSING_VARS[@]}"
      return 1
    fi

    # Validate Qdrant VM values
    validate_qdrant_vm_vars

    cat > "$TFVARS_FILE" <<EOF
project_id   = "$GCP_PROJECT_ID"
region       = "$GCP_REGION"
bucket_name  = "$GCP_BUCKET_NAME"

job_name   = "$GCP_CLOUD_RUN_BATCH_JOB_NAME"
image      = "$GCP_CLOUD_RUN_BATCH_IMAGE"
schedule   = "$GCP_CLOUD_RUN_BATCH_SCHEDULE"
notify_email = "$GCP_CLOUD_RUN_BATCH_NOTIFY_EMAIL"

qdrant_vm_name         = "$GCP_COMPUTE_ENGINE_VM_NAME"
qdrant_vm_machine_type = "$GCP_COMPUTE_ENGINE_VM_MACHINE_TYPE"
qdrant_vm_zone        = "$GCP_COMPUTE_ENGINE_VM_ZONE"
qdrant_vm_disk_size   = $GCP_COMPUTE_ENGINE_VM_DISK_SIZE
EOF
    ARGS_LIST=$(echo $GCP_CLOUD_RUN_BATCH_ARGS | awk '{for(i=1;i<=NF;i++) printf "\"%s\"%s", $i, (i<NF?", ":"") }')
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

  echo "✅ Validación de variables de VM exitosa"
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
