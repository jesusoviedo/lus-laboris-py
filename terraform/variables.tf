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