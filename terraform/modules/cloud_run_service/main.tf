# Cloud Run Service for FastAPI
resource "google_cloud_run_v2_service" "api_service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = var.image

      ports {
        container_port = var.container_port
      }

      env {
        name  = "API_HOST"
        value = "0.0.0.0"
      }

      env {
        name  = "API_PORT"
        value = tostring(var.container_port)
      }

      env {
        name  = "API_RELOAD"
        value = "false"
      }

      env {
        name  = "API_LOG_LEVEL"
        value = var.log_level
      }

      # Qdrant Configuration
      env {
        name  = "API_QDRANT_URL"
        value = var.qdrant_url
      }

      env {
        name  = "API_QDRANT_API_KEY"
        value = var.qdrant_api_key
      }

      env {
        name  = "API_QDRANT_COLLECTION_NAME"
        value = var.qdrant_collection_name
      }

      # GCP Configuration
      env {
        name  = "API_GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "API_GOOGLE_APPLICATION_CREDENTIALS"
        value = var.gcp_credentials_path
      }

      env {
        name  = "API_GCP_USE_CREDENTIALS"
        value = "true"
      }

      # Embedding Configuration
      env {
        name  = "API_DEFAULT_EMBEDDING_MODEL"
        value = var.embedding_model
      }

      env {
        name  = "API_EMBEDDING_BATCH_SIZE"
        value = tostring(var.embedding_batch_size)
      }

      # JWT Configuration
      env {
        name  = "API_JWT_PUBLIC_KEY_PATH"
        value = var.jwt_public_key_path
      }

      # Security Configuration
      env {
        name  = "API_ALLOWED_ORIGINS"
        value = jsonencode(var.allowed_origins)
      }

      env {
        name  = "API_ALLOWED_HOSTS"
        value = jsonencode(var.allowed_hosts)
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }
    }

    scaling {
      min_instance_count = var.min_instance_count
      max_instance_count = var.max_instance_count
    }

    timeout = var.timeout
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# IAM policy to allow unauthenticated access
resource "google_cloud_run_service_iam_policy" "api_service_policy" {
  location = google_cloud_run_v2_service.api_service.location
  project  = google_cloud_run_v2_service.api_service.project
  service  = google_cloud_run_v2_service.api_service.name

  policy_data = data.google_iam_policy.api_service_policy.policy_data
}

data "google_iam_policy" "api_service_policy" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}
