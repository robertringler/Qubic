output "cluster_endpoints" {
  description = "EKS cluster endpoints for all regions"
  value = {
    for region, cluster in module.eks_clusters :
    region => cluster.endpoint
  }
}

output "cluster_names" {
  description = "EKS cluster names for all regions"
  value = {
    for region, cluster in module.eks_clusters :
    region => cluster.cluster_name
  }
}

output "vpc_ids" {
  description = "VPC IDs for all regions"
  value = {
    for region, cluster in module.eks_clusters :
    region => cluster.vpc_id
  }
}

output "api_endpoint" {
  description = "Global API endpoint with latency-based routing"
  value       = "https://api.${var.domain_name}"
}

output "s3_artifacts_bucket" {
  description = "S3 bucket for model artifacts and data"
  value       = aws_s3_bucket.quasim_artifacts.id
}

output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = aws_route53_zone.quasim.zone_id
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for centralized logging"
  value       = aws_cloudwatch_log_group.quasim.name
}

output "kubeconfig_commands" {
  description = "Commands to configure kubectl for each cluster"
  value = {
    for region in keys(local.regions) :
    region => "aws eks update-kubeconfig --name ${module.eks_clusters[region].cluster_name} --region ${region}"
  }
}

output "gpu_node_groups" {
  description = "GPU node group configurations"
  value = {
    for region, cluster in module.eks_clusters :
    region => {
      instance_type = var.gpu_instance_type
      desired_size  = local.regions[region].gpu_node_count
      max_size      = var.max_gpu_nodes_per_region
    }
  }
}
