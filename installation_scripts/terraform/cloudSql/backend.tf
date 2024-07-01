terraform {
#  backend "gcs" {
#    bucket  = "csm_automation"
#    prefix  = "terraform/state/cloudSql"
#  }
  backend "local" {
    path = "./terraform.tfstate"
  }
}