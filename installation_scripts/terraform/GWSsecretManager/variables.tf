
variable "project_id" {
  type        = string
  description = "project_id"
}

variable "gws_sa_secret_name" {
  type        = string
  description = "GWS User secret_name."
}

variable "gws_sa_secret_data" {
  type        = string
  description = "GWS User secret_data"
}

variable "gws_user_secret_name" {
  type        = string
  description = "GWS User secret_name."
}

variable "gws_user_secret_data" {
  type        = string
  description = "GWS User secret_data"
}

variable "terraform_state" {
  type        = string
  default = "csm_automation"
  description = "terraform_state"
}

