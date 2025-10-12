# Cloud Run Service for FastAPI
resource "google_cloud_run_v2_service" "api_service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  # Allow destruction without manual intervention
  deletion_protection = false

  template {
    containers {
      image = var.image

      ports {
        container_port = var.container_port
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
