# Secret Manager Module
# Creates and manages secrets for Cloud Run API service

# Secret for .env file
resource "google_secret_manager_secret" "api_env_file" {
  secret_id = var.api_env_secret_id
  project   = var.project_id

  replication {
    auto {}
  }

  labels = {
    service     = "lus-laboris-api"
    managed_by  = "terraform"
    environment = "production"
  }
}

# Initial version (empty placeholder)
# Real content will be uploaded via GitHub Actions workflow
resource "google_secret_manager_secret_version" "api_env_file_initial" {
  secret      = google_secret_manager_secret.api_env_file.id
  secret_data = "# Placeholder - will be updated by GitHub Actions workflow"

  lifecycle {
    ignore_changes = [secret_data]
  }
}

# Secret for JWT public key
resource "google_secret_manager_secret" "jwt_public_key" {
  secret_id = var.jwt_public_key_secret_id
  project   = var.project_id

  replication {
    auto {}
  }

  labels = {
    service     = "lus-laboris-api"
    managed_by  = "terraform"
    environment = "production"
  }
}

# Initial version (placeholder)
resource "google_secret_manager_secret_version" "jwt_public_key_initial" {
  secret      = google_secret_manager_secret.jwt_public_key.id
  secret_data = "# Placeholder - will be updated by GitHub Actions workflow"

  lifecycle {
    ignore_changes = [secret_data]
  }
}

# IAM binding to allow Cloud Run service account to access .env secret
# Cloud Run v2 uses default compute service account
resource "google_secret_manager_secret_iam_member" "api_env_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.api_env_file.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account}-compute@developer.gserviceaccount.com"
}

# IAM binding to allow Cloud Run service account to access JWT key secret
resource "google_secret_manager_secret_iam_member" "jwt_key_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.jwt_public_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.cloud_run_service_account}-compute@developer.gserviceaccount.com"
}
