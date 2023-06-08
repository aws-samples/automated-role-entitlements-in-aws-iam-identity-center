###############################################
# IAM Identity Center Related Variables #
###############################################

variable "new_acnt_perms" {
  description = "List of all the Permission Sets that are applicable for a newly vended AWS Account"
  type        = list(any)
}