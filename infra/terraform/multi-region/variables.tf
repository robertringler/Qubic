variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS clusters"
  type        = string
  default     = "1.29"
}

variable "gpu_instance_type" {
  description = "EC2 instance type for GPU nodes (NVIDIA)"
  type        = string
  default     = "p3.2xlarge"  # V100 GPU
  
  validation {
    condition = can(regex("^(p3|p4|g4dn|g5)\\.", var.gpu_instance_type))
    error_message = "GPU instance type must be a valid AWS GPU instance (p3, p4, g4dn, or g5 family)."
  }
}

variable "general_instance_type" {
  description = "EC2 instance type for general compute nodes"
  type        = string
  default     = "m5.2xlarge"
}

variable "domain_name" {
  description = "Domain name for QuASIM services"
  type        = string
  default     = "quasim.sybernix.io"
}

variable "enable_cuda_12" {
  description = "Enable CUDA 12.x support"
  type        = bool
  default     = true
}

variable "enable_hip_6" {
  description = "Enable HIP/ROCm 6.x support for AMD GPUs"
  type        = bool
  default     = false
}

variable "enable_monitoring" {
  description = "Enable Prometheus/Grafana monitoring stack"
  type        = bool
  default     = true
}

variable "enable_vault" {
  description = "Enable HashiCorp Vault for secrets management"
  type        = bool
  default     = true
}

variable "enable_gatekeeper" {
  description = "Enable OPA Gatekeeper for policy enforcement"
  type        = bool
  default     = true
}

variable "max_gpu_nodes_per_region" {
  description = "Maximum number of GPU nodes per region"
  type        = number
  default     = 10
}

variable "enable_spot_instances" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = false
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}
