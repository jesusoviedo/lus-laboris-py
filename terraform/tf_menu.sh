#!/bin/bash

# Determinar la raiz del proyecto (un nivel arriba de la ubicacion de este script)
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR/..")"
CRED_DIR="$PROJECT_ROOT/.gcpcredentials"

# === NUEVO: Cargar variables del .env y generar terraform.tfvars ===
ENV_FILE="$PROJECT_ROOT/.env"
TFVARS_FILE="$SCRIPT_DIR/terraform.tfvars"

if [ -f "$ENV_FILE" ]; then
  # Extraer variables del .env
  GCP_PROJECT_ID=$(grep '^GCP_PROJECT_ID=' "$ENV_FILE" | cut -d '=' -f2-)
  GCP_REGION=$(grep '^GCP_REGION=' "$ENV_FILE" | cut -d '=' -f2-)
  GCP_BUCKET_NAME=$(grep '^GCP_BUCKET_NAME=' "$ENV_FILE" | cut -d '=' -f2-)

  # Validar que existan
  if [[ -z "$GCP_PROJECT_ID" || -z "$GCP_REGION" || -z "$GCP_BUCKET_NAME" ]]; then
    echo "❌ ERROR: Faltan variables en $ENV_FILE. Se requieren GCP_PROJECT_ID, GCP_REGION y GCP_BUCKET_NAME."
  else
    # Crear el archivo terraform.tfvars
    cat > "$TFVARS_FILE" <<EOF
project_id   = "$GCP_PROJECT_ID"
region       = "$GCP_REGION"
bucket_name  = "$GCP_BUCKET_NAME"
EOF
    echo "✅ Archivo terraform.tfvars generado correctamente"
  fi
else
  echo "⚠️  No se encontró el archivo .env en $PROJECT_ROOT. No se generó terraform.tfvars."
fi

# Buscar archivo .json de credenciales
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

# Menu interactivo
while true; do
  echo "========= Terraform Menu ========="
  echo "1) terraform init"
  echo "2) terraform plan"
  echo "3) terraform apply"
  echo "4) terraform destroy"
  echo "5) Salir"
  read -p "Seleccione una opción: " opt
  case $opt in
    1)
      terraform init
      ;;
    2)
      terraform plan
      ;;
    3)
      terraform apply
      ;;
    4)
      terraform destroy
      ;;
    5)
      echo "Saliendo..."
      break
      ;;
    *)
      echo "Opción inválida. Intente de nuevo."
      ;;
  esac
done
