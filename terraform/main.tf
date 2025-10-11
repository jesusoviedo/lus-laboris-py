# Modules
module "gcs" {
  source      = "./modules/gcs"
  project_id  = var.project_id
  region      = var.region
  bucket_name = var.bucket_name
}

module "cloud_run_job" {
  source     = "./modules/cloud_run_job"
  project_id = var.project_id
  region     = var.region
  job_name   = var.job_name
  image      = var.image
  args       = var.args
  schedule   = var.schedule
  notify_email = var.notify_email
}

module "compute_engine" {
  source = "./modules/compute_engine"

  vm_name      = var.qdrant_vm_name
  machine_type = var.qdrant_vm_machine_type
  zone        = var.qdrant_vm_zone
  disk_size   = var.qdrant_vm_disk_size
}

# Secret Manager module - Required for Cloud Run deployment
# Must be created BEFORE Cloud Run service
module "secret_manager" {
  source = "./modules/secret_manager"

  project_id                = var.project_id
  cloud_run_service_account = var.project_number
}

# Cloud Run service - Uses secrets from Secret Manager
module "cloud_run_service" {
  source = "./modules/cloud_run_service"

  project_id              = var.project_id
  region                  = var.region
  service_name            = var.api_service_name
  image                   = var.api_image
  container_port          = var.api_container_port
  cpu                     = var.api_cpu
  memory                  = var.api_memory
  min_instance_count      = var.api_min_instance_count
  max_instance_count      = var.api_max_instance_count
  timeout                 = var.api_timeout
  env_secret_name         = module.secret_manager.env_secret_name
  jwt_secret_name         = module.secret_manager.jwt_secret_name

  depends_on = [module.secret_manager]
}

# Outputs
output "bucket_name" {
  value = module.gcs.bucket_name
}

output "job_name" {
  value = module.cloud_run_job.job_name
}

output "scheduler_name" {
  value = module.cloud_run_job.scheduler_name
}

output "qdrant_vm_name" {
  value = module.compute_engine.vm_name
}

output "qdrant_vm_external_ip" {
  value = module.compute_engine.vm_external_ip
}

output "qdrant_vm_internal_ip" {
  value = module.compute_engine.vm_internal_ip
}

output "qdrant_vm_zone" {
  value = module.compute_engine.vm_zone
}

# Cloud Run Service outputs
output "api_service_name" {
  value = module.cloud_run_service.service_name
}

output "api_service_url" {
  value = module.cloud_run_service.service_url
}

output "api_service_location" {
  value = module.cloud_run_service.service_location
}

output "api_service_id" {
  value = module.cloud_run_service.service_id
}

# Secret Manager outputs
output "secret_manager_env_secret_name" {
  value       = module.secret_manager.env_secret_name
  description = "Name of the .env secret in Secret Manager"
}

output "secret_manager_jwt_secret_name" {
  value       = module.secret_manager.jwt_secret_name
  description = "Name of the JWT public key secret in Secret Manager"
}
