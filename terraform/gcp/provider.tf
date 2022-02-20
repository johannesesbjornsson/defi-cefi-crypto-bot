provider "google" {
  project     = "robotic-sphere-309608"
  region      = "europe-west2"
}
terraform {
  backend "gcs" {
    bucket  = "johannes-terraform-state"
    prefix  = "terraform/state"
  }
}