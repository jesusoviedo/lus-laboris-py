#!/bin/bash
set -e

# Load variables from .env (two levels up)
if [[ -f "../../.env" ]]; then
    set -o allexport
    source ../../.env
    set +o allexport
else
    echo "⚠️  WARNING: No se encontró .env, usando variables de entorno del sistema"
fi

# Validate that the required variables exist
if [[ -z "$DOCKER_HUB_USERNAME" || -z "$DOCKER_HUB_PASSWORD" || -z "$DOCKER_IMAGE_NAME_PROCESSING" ]]; then
  echo "❌ ERROR: Asegurate de definir DOCKER_HUB_USERNAME, DOCKER_HUB_PASSWORD e DOCKER_IMAGE_NAME_PROCESSING en .env"
  echo "   Puedes definirlas como variables de entorno o en el archivo .env"
  exit 1
fi

# Login to Docker Hub
echo "$DOCKER_HUB_PASSWORD" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin

# Define tags
DATE_TAG=$(date +%Y%m%d)
LATEST_TAG="latest"

# Build image
docker build -t "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$DATE_TAG" .
docker tag "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$DATE_TAG" "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$LATEST_TAG"

# Push both images
docker push "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$DATE_TAG"
docker push "$DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$LATEST_TAG"

echo "✅ Imagenes subidas a Docker Hub:"
echo "   $DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$DATE_TAG"
echo "   $DOCKER_HUB_USERNAME/$DOCKER_IMAGE_NAME_PROCESSING:$LATEST_TAG"
