output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "logs_policy_arn" {
  value = aws_iam_policy.reliability_api_logs_read.arn
}
