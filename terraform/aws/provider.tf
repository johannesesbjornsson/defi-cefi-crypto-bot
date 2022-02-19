provider "aws" {
  region = "eu-west-2"
}
terraform {
  backend "s3" {
    bucket  = "johannes-terraform-state"
    key  = "terraform/state"
    region = "eu-west-2"
  }
}