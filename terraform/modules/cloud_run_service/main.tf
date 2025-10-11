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

      # All other configuration comes from .env file in Secret Manager
      # JWT Configuration - Path to mounted secret
      env {
        name  = "API_JWT_PUBLIC_KEY_PATH"
        value = "/secrets/public_key.pem"
      }

      # Env file path - Always from Secret Manager
      env {
        name  = "API_ENV_FILE_PATH"
        value = "/secrets/.env"
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }

      # Mount secrets as volumes
      volume_mounts {
        name       = "env-secrets"
        mount_path = "/secrets"
      }
    }

    # Volume for .env secret
    volumes {
      name = "env-secrets"
      secret {
        secret       = var.env_secret_name
        default_mode = 0444
        items {
          version = "latest"
          path    = ".env"
        }
      }
    }

    # Volume for JWT public key secret
    volumes {
      name = "jwt-secrets"
      secret {
        secret       = var.jwt_secret_name
        default_mode = 0444
        items {
          version = "latest"
          path    = "public_key.pem"
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
