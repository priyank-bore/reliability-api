# Optional: only needed if/when you want to run this against a real AWS
# account instead of the free ephemeral kind cluster used in CI.
# NOTE: an EKS cluster + managed node group is NOT free tier — review
# AWS pricing before running `terraform apply`.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  tags = {
    Environment = var.environment
    Project     = "reliability-api"
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.29"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    default = {
      min_size       = 1
      max_size       = 4
      desired_size   = 2
      instance_types = ["t3.medium"]
    }
  }

  tags = {
    Environment = var.environment
    Project     = "reliability-api"
  }
}

# Minimal IAM policy example: read-only access to the app's own CloudWatch
# log group, scoped to just what the service needs (least privilege).
resource "aws_iam_policy" "reliability_api_logs_read" {
  name        = "${var.cluster_name}-logs-read"
  description = "Read-only CloudWatch Logs access for reliability-api"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:GetLogEvents",
          "logs:DescribeLogStreams",
          "logs:FilterLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/eks/${var.cluster_name}/*"
      }
    ]
  })
}
