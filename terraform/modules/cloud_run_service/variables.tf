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

variable "log_level" {
  description = "Log level for the API"
  type        = string
  default     = "info"
}

# Qdrant Configuration
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

# GCP Configuration
variable "gcp_credentials_path" {
  description = "Path to GCP credentials file"
  type        = string
}

# Embedding Configuration
variable "embedding_model" {
  description = "Default embedding model"
  type        = string
}

variable "embedding_batch_size" {
  description = "Batch size for embedding generation"
  type        = number
}

# JWT Configuration
variable "jwt_public_key_path" {
  description = "Path to JWT public key"
  type        = string
}

# Security Configuration
variable "allowed_origins" {
  description = "Allowed CORS origins"
  type        = list(string)
  default     = ["*"]
}

variable "allowed_hosts" {
  description = "Allowed hosts"
  type        = list(string)
  default     = ["*"]
}

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

