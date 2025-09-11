resource "google_cloud_run_v2_job" "job" {
  name     = var.job_name
  location = var.region
  project  = var.project_id

  template {
    template {
      containers {
        image = var.image
        args  = var.args
      }
    }
  }
}

resource "google_cloud_scheduler_job" "job_schedule" {
  name             = "${var.job_name}-schedule"
  description      = "Scheduled execution for Cloud Run Job ${var.job_name}"
  schedule         = var.schedule
  time_zone        = "America/Asuncion"
  project          = var.project_id
  region           = var.region

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${var.job_name}:run"
    oauth_token {
      service_account_email = "${var.project_id}@appspot.gserviceaccount.com"
    }
  }
}
