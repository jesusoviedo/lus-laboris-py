# Variables for Secret Manager module

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "cloud_run_service_account" {
  description = "GCP project number (used to construct default compute service account)"
  type        = string
}
