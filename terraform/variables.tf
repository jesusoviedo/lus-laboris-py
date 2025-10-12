variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "project_number" {
  description = "GCP Project Number (used for service account construction)"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "bucket_name" {
  description = "Nombre del bucket a crear"
  type        = string
}

variable "job_name" {
  description = "Nombre del Cloud Run Job"
  type        = string
}

variable "image" {
  description = "Imagen de Docker Hub a usar (incluyendo tag)"
  type        = string
}

variable "args" {
  description = "Argumentos para el contenedor"
  type        = list(string)
}

variable "schedule" {
  description = "Schedule en formato cron para el job"
  type        = string
}

variable "notify_email" {
  description = "Correo para notificaciones de estado del Cloud Run Batch (éxito o error)"
  type        = string
}

variable "qdrant_vm_name" {
  description = "Name of the Qdrant VM"
  type        = string
}

variable "qdrant_vm_machine_type" {
  description = "Machine type for Qdrant VM"
  type        = string
}

variable "qdrant_vm_zone" {
  description = "Zone for Qdrant VM"
  type        = string
}

variable "qdrant_vm_disk_size" {
  description = "Disk size for Qdrant VM in GB"
  type        = number
}

# Cloud Run Service variables
variable "api_service_name" {
  description = "Name of the Cloud Run API service"
  type        = string
}

variable "api_image" {
  description = "Docker image URL for the API service"
  type        = string
}

variable "api_container_port" {
  description = "Port that the API container listens on"
  type        = number
  default     = 8080  # Default for gcr.io/cloudrun/hello dummy image
}

# All other API configuration (Qdrant, GCP, Embedding, JWT, Security, etc.)
# comes from .env file mounted from Secret Manager

# Resource Configuration
variable "api_cpu" {
  description = "CPU allocation for the Cloud Run API service"
  type        = string
}

variable "api_memory" {
  description = "Memory allocation for the Cloud Run API service"
  type        = string
}

variable "api_min_instance_count" {
  description = "Minimum number of instances for the Cloud Run API service"
  type        = number
  default     = 0
}

variable "api_max_instance_count" {
  description = "Maximum number of instances for the Cloud Run API service"
  type        = number
  default     = 3
}

variable "api_timeout" {
  description = "Request timeout for the Cloud Run API service"
  type        = string
  default     = "300s"
}

# Secret Manager Configuration
variable "api_env_secret_id" {
  description = "Secret ID for API .env file in Secret Manager"
  type        = string
}

variable "jwt_public_key_secret_id" {
  description = "Secret ID for JWT public key in Secret Manager"
  type        = string
}
