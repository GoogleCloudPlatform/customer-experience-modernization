
variable "region" {
  type        = string
  description = "region"
}

variable "project_id" {
  type        = string
  description = "project_id"
}

variable "service_account_email" {
  type        = string
  description = "service_account_email."
}

variable "sql_instance_name" {
  type        = string
  description = "sql_instance_name"
}

variable "gcs_bucket" {
  type        = string
  default = "csm_automation"
  description = "gcs_bucket"
}
