terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.45"
    }
  }
  required_version = ">= 1.0.5"
}

# Configure the AWS Provider
provider "aws" {
  profile = "default"
  region  = "us-east-1"
}