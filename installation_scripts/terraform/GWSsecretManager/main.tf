provider "google" {
  # Define your project, credentials and region here
  project = var.project_id
  region  = "us-central1"
}

resource "google_secret_manager_secret" "gws-sa-secret" {
  secret_id = var.gws_sa_secret_name

  labels = {
    app = "csm"
  }
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "gws-sa-secret-version" {
  secret  = google_secret_manager_secret.gws-sa-secret.id
  secret_data = var.gws_sa_secret_data
}


resource "google_secret_manager_secret" "gws-user-secret" {
  secret_id = var.gws_user_secret_name

  labels = {
    app = "csm"
  }
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "gws-user-secret-version" {
  secret  = google_secret_manager_secret.gws-user-secret.id
  secret_data = var.gws_user_secret_data
}

output "gws_sa_secret_version_id" {
  value = google_secret_manager_secret_version.gws-sa-secret-version.id
}

output "gws_user_secret_version_id" {
  value = google_secret_manager_secret_version.gws-user-secret-version.id
}
