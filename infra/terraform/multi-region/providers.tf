# Primary region provider (us-west-2)
provider "aws" {
  alias  = "us-west-2"
  region = "us-west-2"
  
  default_tags {
    tags = {
      Project     = "QuASIM"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}

# Secondary region provider (us-east-1)
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
  
  default_tags {
    tags = {
      Project     = "QuASIM"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}

# European region provider (eu-west-1)
provider "aws" {
  alias  = "eu-west-1"
  region = "eu-west-1"
  
  default_tags {
    tags = {
      Project     = "QuASIM"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}

# Asia Pacific region provider (ap-southeast-1)
provider "aws" {
  alias  = "ap-southeast-1"
  region = "ap-southeast-1"
  
  default_tags {
    tags = {
      Project     = "QuASIM"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}

# Kubernetes provider configured for each cluster
provider "kubernetes" {
  alias = "us-west-2"
  
  host                   = module.eks_clusters["us-west-2"].endpoint
  cluster_ca_certificate = base64decode(module.eks_clusters["us-west-2"].certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks_clusters["us-west-2"].cluster_name,
      "--region",
      "us-west-2"
    ]
  }
}

provider "kubernetes" {
  alias = "us-east-1"
  
  host                   = module.eks_clusters["us-east-1"].endpoint
  cluster_ca_certificate = base64decode(module.eks_clusters["us-east-1"].certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks_clusters["us-east-1"].cluster_name,
      "--region",
      "us-east-1"
    ]
  }
}

provider "helm" {
  alias = "us-west-2"
  
  kubernetes {
    host                   = module.eks_clusters["us-west-2"].endpoint
    cluster_ca_certificate = base64decode(module.eks_clusters["us-west-2"].certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        module.eks_clusters["us-west-2"].cluster_name,
        "--region",
        "us-west-2"
      ]
    }
  }
}
