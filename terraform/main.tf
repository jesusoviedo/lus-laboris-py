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