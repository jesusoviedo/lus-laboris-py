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
      max_retries = 3
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

resource "google_monitoring_notification_channel" "email" {
  display_name = "Cloud Run Batch Email Notification"
  type         = "email"
  labels = {
    email_address = var.notify_email
  }
}

resource "google_monitoring_alert_policy" "job_failed" {
  display_name = "Cloud Run Batch Job Failed"
  combiner     = "OR"
  notification_channels = [google_monitoring_notification_channel.email.id]

  conditions {
    display_name = "Cloud Run Batch Job Failed Condition"
    condition_matched_log {
      filter = "resource.type=\"cloud_run_job\" resource.labels.job_name=\"${var.job_name}\" severity=\"ERROR\""
    }
  }
}

resource "google_monitoring_alert_policy" "job_succeeded" {
  display_name = "Cloud Run Batch Job Succeeded"
  combiner     = "OR"
  notification_channels = [google_monitoring_notification_channel.email.id]

  conditions {
    display_name = "Cloud Run Batch Job Succeeded Condition"
    condition_matched_log {
      filter = "resource.type=\"cloud_run_job\" resource.labels.job_name=\"${var.job_name}\" severity=\"INFO\""
    }
  }
}
