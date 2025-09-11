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