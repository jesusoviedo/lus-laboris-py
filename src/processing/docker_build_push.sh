#!/bin/bash
set -e

# Cargar variables desde .env (dos niveles arriba)
set -o allexport
source ../../.env
set +o allexport

# Validar que existan las variables necesarias
if [[ -z "$DOCKER_HUB_USERNAME" || -z "$DOCKER_HUB_PASSWORD" || -z "$IMAGE_NAME_PROCESSING" ]]; then
  echo "❌ ERROR: Asegurate de definir DOCKER_HUB_USERNAME, DOCKER_HUB_PASSWORD e IMAGE_NAME_PROCESSING en .env"
  exit 1
fi

# Login en Docker Hub
echo "$DOCKER_HUB_PASSWORD" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin

# Definir tags
DATE_TAG=$(date +%Y%m%d)
LATEST_TAG="latest"

# Construir imagen
docker build -t "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$DATE_TAG" .
docker tag "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$DATE_TAG" "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$LATEST_TAG"

# Push de ambas imagenes
docker push "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$DATE_TAG"
docker push "$DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$LATEST_TAG"

echo "✅ Imagenes subidas a Docker Hub:"
echo "   $DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$DATE_TAG"
echo "   $DOCKER_HUB_USERNAME/$IMAGE_NAME_PROCESSING:$LATEST_TAG"
