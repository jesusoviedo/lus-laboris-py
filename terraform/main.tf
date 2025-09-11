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
}

output "bucket_name" {
  value = module.gcs.bucket_name
}
