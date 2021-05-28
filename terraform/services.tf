
resource "google_project_service" "project" {
  for_each = var.services
  project = var.project_id
  service   = each.value
}

resource "google_container_registry" "registry" {
  project  = var.project_id
  location = "EU"

  depends_on = [
    google_project_service.project
  ]
}