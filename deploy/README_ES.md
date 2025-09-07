# Guía de Despliegue en Google Cloud (ES)

## 1. Qdrant en Google Compute Engine (VM)

### a) Crear la VM
```bash
gcloud compute instances create qdrant-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --tags=qdrant-server
```

### b) Instalar Qdrant
```bash
sudo apt update && sudo apt install -y docker.io
sudo systemctl start docker && sudo systemctl enable docker
sudo docker run -d --name qdrant -p 6333:6333 -v /qdrant_data:/qdrant/storage qdrant/qdrant
```

### c) Abrir el puerto en el firewall
```bash
gcloud compute firewall-rules create allow-qdrant \
  --allow=tcp:6333 \
  --target-tags=qdrant-server
```

---

## 2. FastAPI y dlt en Google Cloud Run (usando Docker)

### a) Crear Dockerfile para FastAPI o dlt
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### b) Construir y subir la imagen a Google Container Registry
```bash
gcloud builds submit --tag gcr.io/PROYECTO_ID/fastapi-app
```

### c) Desplegar en Cloud Run
```bash
gcloud run deploy fastapi-app \
  --image gcr.io/PROYECTO_ID/fastapi-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 3. Google Cloud Storage (GCS)

### a) Crear un bucket
```bash
gsutil mb -l us-central1 gs://NOMBRE_BUCKET
```

### b) Subir archivos procesados
```bash
gsutil cp data/processed/ley_procesada.json gs://NOMBRE_BUCKET/
```

---

## 4. Habilitar APIs y crear servicios con gcloud CLI

```bash
gcloud services enable compute.googleapis.com run.googleapis.com storage.googleapis.com artifactregistry.googleapis.com
```

---

## 5. Recursos útiles
- [Documentación Qdrant](https://qdrant.tech/documentation/)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [Google Compute Engine](https://cloud.google.com/compute/docs)
- [Google Cloud Storage](https://cloud.google.com/storage/docs)
- [gcloud CLI](https://cloud.google.com/sdk/gcloud)

---

## 6. Ejemplos incluidos en este proyecto

- `deploy/Dockerfile.fastapi`: Dockerfile de ejemplo para desplegar FastAPI en Cloud Run.
- `deploy/Dockerfile.dlt`: Dockerfile de ejemplo para ejecutar procesos batch con dlt en Cloud Run.
- `.github/workflows/ci.yml`: Ejemplo de workflow de GitHub Actions para pruebas y build/push de imagen Docker a Google Container Registry.

---

## 7. Configuración de secretos para despliegue automático desde GitHub Actions

Para que el workflow de GitHub Actions pueda desplegar automáticamente en Google Cloud Run, debes configurar los siguientes secretos en tu repositorio de GitHub:

- `GCP_SA_KEY`: El contenido (JSON) de una clave de cuenta de servicio de Google Cloud con permisos para Cloud Run, Artifact Registry y Cloud Build.
- `GCP_PROJECT_ID`: El ID de tu proyecto de Google Cloud.

### Pasos para obtener y agregar los secretos:

1. **Crear una cuenta de servicio en Google Cloud Console** con los permisos necesarios (Cloud Run Admin, Storage Admin, Artifact Registry Admin, Service Account User).
2. **Generar una clave JSON** para esa cuenta de servicio y descargarla.
3. **Ir a tu repositorio en GitHub > Settings > Secrets and variables > Actions > New repository secret**.
4. **Agregar un secreto llamado `GCP_SA_KEY`** y pegar el contenido del archivo JSON.
5. **Agregar un secreto llamado `GCP_PROJECT_ID`** con el ID de tu proyecto.

Con esto, el workflow podrá autenticarse y desplegar automáticamente tu aplicación en Cloud Run.

### Permisos mínimos recomendados para la cuenta de servicio

La cuenta de servicio debe tener los siguientes roles:
- `Cloud Run Admin` (roles/run.admin)
- `Storage Admin` (roles/storage.admin)
- `Artifact Registry Admin` (roles/artifactregistry.admin)
- `Cloud Build Editor` (roles/cloudbuild.builds.editor)
- `Service Account User` (roles/iam.serviceAccountUser)

Puedes asignar estos roles desde la consola de Google Cloud o usando el siguiente comando:

```bash
gcloud projects add-iam-policy-binding TU_PROYECTO \
  --member="serviceAccount:TU_CUENTA@TU_PROYECTO.iam.gserviceaccount.com" \
  --role="roles/run.admin"
gcloud projects add-iam-policy-binding TU_PROYECTO \
  --member="serviceAccount:TU_CUENTA@TU_PROYECTO.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
gcloud projects add-iam-policy-binding TU_PROYECTO \
  --member="serviceAccount:TU_CUENTA@TU_PROYECTO.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"
gcloud projects add-iam-policy-binding TU_PROYECTO \
  --member="serviceAccount:TU_CUENTA@TU_PROYECTO.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"
gcloud projects add-iam-policy-binding TU_PROYECTO \
  --member="serviceAccount:TU_CUENTA@TU_PROYECTO.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```
