variable "region" { type = string }
variable "cluster_name" { type = string }
variable "vpc_cidr" { type = string  default = "10.42.0.0/16" }
variable "public_subnets" { type = list(string) }
variable "private_subnets" { type = list(string) }
variable "kubernetes_version" { type = string default = "1.29" }

# Node group sizes
variable "ng_general_size" { type = string default = "m6i.4xlarge" }
variable "ng_nvidia_gpu_size" { type = string default = "p5.2xlarge" }
variable "ng_amd_gpu_size"    { type = string default = "g5g.4xlarge" }

variable "desired_capacity_general" { type = number default = 3 }
variable "desired_capacity_nvidia"  { type = number default = 2 }
variable "desired_capacity_amd"     { type = number default = 0 }
