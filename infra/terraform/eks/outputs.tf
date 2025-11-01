output "cluster_name" {
  value = module.eks.cluster_name
}
output "region" {
  value = var.region
}
output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}
