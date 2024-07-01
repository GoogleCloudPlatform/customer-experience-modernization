terraform {
#  backend "gcs" {
#    bucket  = "csm_automation"
#    prefix  = "terraform/state/secretmanager/"
#  }
  backend "local" {
    path = "./terraform.tfstate"
  }
}