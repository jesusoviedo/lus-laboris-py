output "job_name" {
  value = google_cloud_run_v2_job.job.name
}

output "scheduler_name" {
  value = google_cloud_scheduler_job.job_schedule.name
}
