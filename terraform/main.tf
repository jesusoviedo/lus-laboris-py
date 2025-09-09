module "gcs" {
  source      = "./modules/gcs"
  project_id  = var.project_id
  region      = var.region
  bucket_name = var.bucket_name
}

output "bucket_name" {
  value = module.gcs.bucket_name
}
