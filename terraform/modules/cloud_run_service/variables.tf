variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
}

variable "image" {
  description = "Docker image URL for the API service"
  type        = string
}

variable "container_port" {
  description = "Port that the container listens on"
  type        = number
}

# All other configuration (Qdrant, GCP, Embedding, JWT, Security, etc.)
# comes from .env file mounted from Secret Manager

# Resource Configuration
variable "cpu" {
  description = "CPU allocation for the Cloud Run service"
  type        = string
}

variable "memory" {
  description = "Memory allocation for the Cloud Run service"
  type        = string
}

variable "min_instance_count" {
  description = "Minimum number of instances for the Cloud Run service"
  type        = number
  default     = 0
}

variable "max_instance_count" {
  description = "Maximum number of instances for the Cloud Run service"
  type        = number
  default     = 3
}

variable "timeout" {
  description = "Request timeout for the Cloud Run service"
  type        = string
  default     = "300s"
}

# Secret Manager Configuration
variable "env_secret_name" {
  description = "Name of the Secret Manager secret containing .env file"
  type        = string
}

variable "jwt_secret_name" {
  description = "Name of the Secret Manager secret containing JWT public key"
  type        = string
}
