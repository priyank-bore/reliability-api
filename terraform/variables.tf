variable "aws_region" {
  default = "us-east-1"
}

variable "cluster_name" {
  default = "reliability-api-cluster"
}

variable "environment" {
  default = "dev"
}

variable "availability_zones" {
  default = ["us-east-1a", "us-east-1b"]
}

variable "private_subnet_cidrs" {
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnet_cidrs" {
  default = ["10.0.101.0/24", "10.0.102.0/24"]
}
