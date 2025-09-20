variable "project_id" {
  description = "GCP Project ID"
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
}

variable "api_log_level" {
  description = "Log level for the API"
  type        = string
  default     = "info"
}

# Qdrant Configuration for API
variable "qdrant_url" {
  description = "Qdrant vector database URL"
  type        = string
}

variable "qdrant_api_key" {
  description = "Qdrant API key"
  type        = string
  sensitive   = true
}

variable "qdrant_collection_name" {
  description = "Qdrant collection name"
  type        = string
}

# API Configuration
variable "api_gcp_credentials_path" {
  description = "Path to GCP credentials file in the container"
  type        = string
}

variable "api_embedding_model" {
  description = "Default embedding model for the API"
  type        = string
}

variable "api_embedding_batch_size" {
  description = "Batch size for embedding generation"
  type        = number
}

variable "api_jwt_public_key_path" {
  description = "Path to JWT public key in the container"
  type        = string
}

variable "api_allowed_origins" {
  description = "Allowed CORS origins for the API"
  type        = list(string)
  default     = ["*"]
}

variable "api_allowed_hosts" {
  description = "Allowed hosts for the API"
  type        = list(string)
  default     = ["*"]
}

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
