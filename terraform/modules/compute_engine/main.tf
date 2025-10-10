resource "google_compute_instance" "qdrant_vm" {
  name         = var.vm_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = var.disk_size
    }
  }

  network_interface {
    network = "default"
    access_config {
      # Ephemeral public IP
    }
  }

  tags = ["qdrant-server", "http-server", "https-server"]

  # Preemptible instance configuration for cost optimization
  scheduling {
    preemptible       = true
    automatic_restart = false
    provisioning_model = "SPOT"
  }
}

# Firewall rule for Qdrant
resource "google_compute_firewall" "qdrant_firewall" {
  name    = "${var.vm_name}-firewall"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["6333", "6334", "22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["qdrant-server"]
}
