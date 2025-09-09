output "bucket_name" {
  description = "Nombre del bucket creado"
  value       = google_storage_bucket.bucket.name
}
