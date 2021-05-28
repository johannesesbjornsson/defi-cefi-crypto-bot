resource "google_service_account" "vm" {
  account_id   = "vm-svc-acc"
  display_name = "VM Service Account"
}
resource "google_storage_bucket_iam_binding" "viewer" {
  bucket = google_container_registry.registry.id
  role = "roles/storage.objectViewer"
  members = [
      "serviceAccount:${google_service_account.vm.email}"
  ]
}

resource "google_compute_address" "external_ip" {
  name         = "external-ip"
  address_type = "EXTERNAL"
  lifecycle {
    create_before_destroy = true
  }
}

resource "google_compute_instance" "default" {
  name         = "crypt-server"
  machine_type = "e2-small"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "centos-cloud/centos-7"
    }
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.external_ip.address
    }
  }
  metadata_startup_script = "curl -fsSL https://get.docker.com/ | sh; sudo systemctl start docker; sudo systemctl enable docker"
  service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = google_service_account.vm.email
    scopes = ["cloud-platform"]
  }
}

resource "google_compute_firewall" "deny_all" {
  name    = "deny-all-ingress"
  network = "default"

  source_ranges = [
      "0.0.0.0/0"
  ]
  deny {
    protocol = "all"
  }
  priority = 1000

}

resource "google_compute_firewall" "allow_me" {
  name    = "allow-me-ingress"
  network = "default"

  source_ranges = [
      "217.155.28.165/32"
  ]
  allow {
    ports = ["22"]
    protocol = "TCP"
  } 
  target_service_accounts = [google_service_account.vm.email]
  priority = 500

}