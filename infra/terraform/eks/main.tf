module "vpc" {
  source = "../modules/vpc"
  vpc_cidr        = var.vpc_cidr
  public_subnets  = var.public_subnets
  private_subnets = var.private_subnets
}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "~> 20.8"
  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version
  subnet_ids      = module.vpc.private_subnet_ids

  vpc_id = module.vpc.vpc_id

  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    general = {
      instance_types = [var.ng_general_size]
      desired_size   = var.desired_capacity_general
      min_size       = 2
      max_size       = 10
      labels = { role = "general" }
      tags   = { Name = "${var.cluster_name}-general" }
    }

    nvidia_gpu = {
      instance_types = [var.ng_nvidia_gpu_size]
      desired_size   = var.desired_capacity_nvidia
      min_size       = 0
      max_size       = 10
      labels = {
        role        = "gpu"
        accelerator = "nvidia"
      }
      taints = [{ key = "accelerator", value = "nvidia", effect = "NO_SCHEDULE" }]
      ami_type = "AL2_x86_64_GPU"
      tags    = { Name = "${var.cluster_name}-nvidia" }
    }

    amd_gpu = {
      instance_types = [var.ng_amd_gpu_size]
      desired_size   = var.desired_capacity_amd
      min_size       = 0
      max_size       = 10
      labels = {
        role        = "gpu"
        accelerator = "amd"
      }
      taints = [{ key = "accelerator", value = "amd", effect = "NO_SCHEDULE" }]
      ami_type = "AL2_x86_64"
      tags    = { Name = "${var.cluster_name}-amd" }
    }
  }
}

resource "kubernetes_namespace" "core"        { metadata { name = "core" } }
resource "kubernetes_namespace" "mlops"       { metadata { name = "mlops" } }
resource "kubernetes_namespace" "inference"   { metadata { name = "inference" } }
resource "kubernetes_namespace" "monitoring"  { metadata { name = "monitoring" } }
resource "kubernetes_namespace" "security"    { metadata { name = "security" } }
