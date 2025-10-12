# Variables for Secret Manager module

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "cloud_run_service_account" {
  description = "GCP project number (used to construct default compute service account)"
  type        = string
}

variable "api_env_secret_id" {
  description = "Secret ID for API .env file in Secret Manager"
  type        = string
}

variable "jwt_public_key_secret_id" {
  description = "Secret ID for JWT public key in Secret Manager"
  type        = string
}
