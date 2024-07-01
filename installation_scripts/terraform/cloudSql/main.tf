provider "google" {
  # Define your project, credentials and region here
  project = var.project_id
  region  = "us-central1"
}

resource "google_sql_database_instance" "primary" {
  name             = var.sql_instance_name
  region           = var.region
  database_version = "MYSQL_8_0"
  settings {
    tier = "db-f1-micro"
    database_flags {
      name  = "cloudsql_iam_authentication"
      value = "on"
    }
  }
  deletion_protection = false
}



# Specify the email address of the IAM service account to add to the instance

resource "google_sql_user" "iam_service_account_user" {
  name     = var.service_account_email
  instance = google_sql_database_instance.primary.name
  type     = "CLOUD_IAM_SERVICE_ACCOUNT"
}
