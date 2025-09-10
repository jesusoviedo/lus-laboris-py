#!/bin/bash

# Determinar la raiz del proyecto (dos niveles arriba de la ubicacion de este script)
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR/..")"
CRED_DIR="$PROJECT_ROOT/.gcpcredentials"

# Buscar archivo .json de credenciales
CRED_FILE=$(find "$CRED_DIR" -maxdepth 1 -name '*.json' | head -n 1)

if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
  if [ -n "$CRED_FILE" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="$CRED_FILE"
    echo "✅ Variable GOOGLE_APPLICATION_CREDENTIALS seteada a: $CRED_FILE"
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
