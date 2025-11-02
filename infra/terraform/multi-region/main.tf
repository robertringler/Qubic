terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.12"
    }
  }
}

# Multi-region configuration for QuASIM
# Deploys EKS clusters with GPU node groups across multiple AWS regions

locals {
  project = "quasim-platform"
  
  # Define regions and their configurations
  regions = {
    us-west-2 = {
      primary           = true
      vpc_cidr          = "10.0.0.0/16"
      availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
      gpu_node_count    = 6
      general_node_count = 5
    }
    us-east-1 = {
      primary           = false
      vpc_cidr          = "10.1.0.0/16"
      availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
      gpu_node_count    = 4
      general_node_count = 3
    }
    eu-west-1 = {
      primary           = false
      vpc_cidr          = "10.2.0.0/16"
      availability_zones = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
      gpu_node_count    = 4
      general_node_count = 3
    }
    ap-southeast-1 = {
      primary           = false
      vpc_cidr          = "10.3.0.0/16"
      availability_zones = ["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"]
      gpu_node_count    = 2
      general_node_count = 2
    }
  }
  
  common_tags = {
    Project     = "QuASIM"
    ManagedBy   = "Terraform"
    Environment = var.environment
  }
}

# Deploy EKS cluster in each region
module "eks_clusters" {
  source   = "./modules/eks-cluster"
  for_each = local.regions

  region             = each.key
  vpc_cidr           = each.value.vpc_cidr
  availability_zones = each.value.availability_zones
  is_primary         = each.value.primary
  
  # Node group configuration
  gpu_node_count     = each.value.gpu_node_count
  general_node_count = each.value.general_node_count
  gpu_instance_type  = var.gpu_instance_type
  general_instance_type = var.general_instance_type
  
  # Kubernetes version
  kubernetes_version = var.kubernetes_version
  
  # Tags
  tags = merge(local.common_tags, {
    Region = each.key
    Primary = each.value.primary
  })
}

# VPC Peering between regions for Ray cluster communication
resource "aws_vpc_peering_connection" "cross_region" {
  for_each = {
    for pair in setproduct(keys(local.regions), keys(local.regions)) :
    "${pair[0]}-${pair[1]}" => {
      source = pair[0]
      target = pair[1]
    }
    if pair[0] < pair[1]  # Avoid duplicates and self-peering
  }
  
  provider = aws.us-west-2  # Requester region
  
  vpc_id      = module.eks_clusters[each.value.source].vpc_id
  peer_vpc_id = module.eks_clusters[each.value.target].vpc_id
  peer_region = each.value.target
  
  auto_accept = false
  
  tags = merge(local.common_tags, {
    Name = "quasim-peering-${each.value.source}-${each.value.target}"
  })
}

# Global S3 bucket for model artifacts and data
resource "aws_s3_bucket" "quasim_artifacts" {
  bucket = "${local.project}-artifacts-${var.environment}"
  
  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "quasim_artifacts" {
  bucket = aws_s3_bucket.quasim_artifacts.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "quasim_artifacts" {
  bucket = aws_s3_bucket.quasim_artifacts.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Cross-region replication for high availability
resource "aws_s3_bucket_replication_configuration" "quasim_artifacts" {
  depends_on = [aws_s3_bucket_versioning.quasim_artifacts]
  
  role   = aws_iam_role.s3_replication.arn
  bucket = aws_s3_bucket.quasim_artifacts.id
  
  rule {
    id     = "replicate-all"
    status = "Enabled"
    
    destination {
      bucket        = aws_s3_bucket.quasim_artifacts_replica.arn
      storage_class = "STANDARD_IA"
    }
  }
}

resource "aws_s3_bucket" "quasim_artifacts_replica" {
  provider = aws.us-east-1
  bucket   = "${local.project}-artifacts-replica-${var.environment}"
  
  tags = local.common_tags
}

# IAM role for S3 replication
resource "aws_iam_role" "s3_replication" {
  name = "${local.project}-s3-replication"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "s3.amazonaws.com"
      }
    }]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy" "s3_replication" {
  role = aws_iam_role.s3_replication.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetReplicationConfiguration",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.quasim_artifacts.arn
        ]
      },
      {
        Action = [
          "s3:GetObjectVersionForReplication",
          "s3:GetObjectVersionAcl"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.quasim_artifacts.arn}/*"
        ]
      },
      {
        Action = [
          "s3:ReplicateObject",
          "s3:ReplicateDelete"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.quasim_artifacts_replica.arn}/*"
        ]
      }
    ]
  })
}

# Route53 for global DNS with latency-based routing
resource "aws_route53_zone" "quasim" {
  name = var.domain_name
  
  tags = local.common_tags
}

resource "aws_route53_record" "api_latency" {
  for_each = local.regions
  
  zone_id = aws_route53_zone.quasim.zone_id
  name    = "api.${var.domain_name}"
  type    = "A"
  
  set_identifier = each.key
  latency_routing_policy {
    region = each.key
  }
  
  alias {
    name                   = module.eks_clusters[each.key].api_endpoint
    zone_id                = module.eks_clusters[each.key].load_balancer_zone_id
    evaluate_target_health = true
  }
}

# CloudWatch log group for centralized logging
resource "aws_cloudwatch_log_group" "quasim" {
  name              = "/aws/quasim/${var.environment}"
  retention_in_days = 30
  
  tags = local.common_tags
}
