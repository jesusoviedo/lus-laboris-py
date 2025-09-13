variable "vm_name" {
  description = "Name of the VM instance"
  type        = string
  default     = "qdrant-vm"
}

variable "machine_type" {
  description = "Machine type for the VM"
  type        = string
  default     = "e2-medium"
}

variable "zone" {
  description = "GCP zone for the VM"
  type        = string
  default     = "southamerica-east1-a"
}

variable "disk_size" {
  description = "Size of the boot disk in GB"
  type        = number
  default     = 50
}
