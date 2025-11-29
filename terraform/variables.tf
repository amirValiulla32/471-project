# ============================================
# Terraform Variables for FTP Server Deployment
# ============================================

variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type (t2.micro for free tier)"
  type        = string
  default     = "t2.micro"
}

variable "key_name" {
  description = "Name of the SSH key pair for EC2 access (must exist in AWS)"
  type        = string
  # No default - user must provide this
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH into the instance (0.0.0.0/0 for anywhere)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "ftp-server"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}
