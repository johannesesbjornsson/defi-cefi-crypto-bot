variable "project_id" {default = "robotic-sphere-309608"}
variable "zone" {default = "europe-west2-b"}

variable "services" {
  type = set(string)
  default = [
    "iam.googleapis.com", 
    "compute.googleapis.com",
    "containerregistry.googleapis.com"
  ]
}

variable "my_ip" {}