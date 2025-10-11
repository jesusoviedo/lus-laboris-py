# Outputs for Secret Manager module

output "env_secret_name" {
  description = "Name of the .env file secret"
  value       = google_secret_manager_secret.api_env_file.secret_id
}

output "env_secret_id" {
  description = "Full ID of the .env file secret"
  value       = google_secret_manager_secret.api_env_file.id
}

output "jwt_secret_name" {
  description = "Name of the JWT public key secret"
  value       = google_secret_manager_secret.jwt_public_key.secret_id
}

output "jwt_secret_id" {
  description = "Full ID of the JWT public key secret"
  value       = google_secret_manager_secret.jwt_public_key.id
}
