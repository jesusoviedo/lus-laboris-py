# Terraform Configuration
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.1.1"
    }
  }

  backend "gcs" {
    bucket = "py-labor-law-rag-terraform-state"
    prefix = "terraform/state"
  }

}

# Providers for Google Cloud
provider "google" {
  # Use GOOGLE_APPLICATION_CREDENTIALS env var if set (GitHub Actions, CI/CD)
  project = var.project_id
  region  = var.region
}
