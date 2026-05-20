variable "env" {
  type    = string
  default = "dev"
}

variable "deletion_protection_enabled" {
  type    = bool
  default = false
}
variable "region" {
  type    = string
  default = "ap-southeast-1"

  validation {
    condition     = can(regex("^(us|eu|ap|sa|ca|me|af|il)-(east|west|north|south|central|northeast|southeast|northwest|southwest)-[1-9]$", var.region))
    error_message = "region must be a valid AWS region (e.g. us-east-1, eu-west-2, ap-southeast-1)."
  }
}

variable "sparky_models" {
  description = "Available Sparky model configuration."
  type = object({
    default_model_id = string
    models = list(object({
      id               = string
      label            = string
      description      = string
      model_id         = string
      max_tokens       = number
      reasoning_type   = string
      reasoning_levels = list(string)
      reasoning_labels = list(string)
      budget_mapping   = map(number)
      effort_mapping   = map(string)
    }))
  })

  default = {
    default_model_id = "amazon-nova-lite"
    models = [
      {
        id               = "amazon-nova-lite"
        label            = "Amazon Nova Lite"
        description      = "Default low-cost Amazon Nova model"
        model_id         = "apac.amazon.nova-lite-v1:0"
        max_tokens       = 8000
        reasoning_type   = "none"
        reasoning_levels = []
        reasoning_labels = []
        budget_mapping   = {}
        effort_mapping   = {}
      },
      {
        id               = "amazon-nova-pro"
        label            = "Amazon Nova Pro"
        description      = "Stronger Amazon Nova model"
        model_id         = "apac.amazon.nova-pro-v1:0"
        max_tokens       = 8000
        reasoning_type   = "none"
        reasoning_levels = []
        reasoning_labels = []
        budget_mapping   = {}
        effort_mapping   = {}
      },
      {
        id               = "claude-haiku-4.5"
        label            = "Claude Haiku 4.5"
        description      = "Optional Claude fallback model"
        model_id         = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
        max_tokens       = 64000
        reasoning_type   = "budget"
        reasoning_levels = ["Low", "Medium", "High", "Max"]
        reasoning_labels = []
        budget_mapping = {
          "1" = 16000
          "2" = 30000
          "3" = 42000
          "4" = 63999
        }
        effort_mapping = {}
      }
    ]
  }

  validation {
    condition     = contains([for model in var.sparky_models.models : model.id], var.sparky_models.default_model_id)
    error_message = "default_model_id must reference one of the defined model IDs."
  }
}

variable "model_core_services" {
  type        = string
  description = "Bedrock model ID for the core services runtime"
  default     = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
}

variable "username" {
  type        = string
  description = "Cognito username"
}

variable "email" {
  type        = string
  description = "Cognito user email"
}

variable "given_name" {
  type        = string
  description = "Cognito user given name"
}

variable "family_name" {
  type        = string
  description = "Cognito user family name"
}

variable "enable_core_services" {
  type        = bool
  default     = true
  description = "Enable or disable Core-Services API runtime for synchronous operations"
}

variable "expiry_duration_days" {
  type        = number
  default     = 365
  description = "Number of days before data expires across DynamoDB TTL, S3 lifecycle, and AgentCore Memory"

  validation {
    condition     = var.expiry_duration_days >= 30 && var.expiry_duration_days <= 365
    error_message = "expiry_duration_days must be between 30 and 365 inclusive."
  }
}

variable "use_express_checkpoint_bucket" {
  type        = bool
  default     = false
  description = "Use S3 Express One Zone directory bucket for checkpoint offloading instead of standard S3"
}

variable "express_az_id" {
  type        = string
  default     = "use1-az4"
  description = "Availability Zone ID for S3 Express One Zone bucket (only used when use_express_checkpoint_bucket = true)"
}

variable "rerank_model_arn" {
  type        = string
  default     = "arn:aws:bedrock:us-east-1::foundation-model/amazon.rerank-v1:0"
  description = "ARN of the Bedrock rerank model for KB search result reranking"
}

variable "project_memory_extraction_model_id" {
  type        = string
  default     = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
  description = "Bedrock model ID used for project memory extraction and consolidation (override strategy)"
}

variable "kb_vector_store_type" {
  type        = string
  default     = "S3_VECTORS"
  description = "Vector store backend for the Bedrock Knowledge Base. Use OPENSEARCH_SERVERLESS or S3_VECTORS."

  validation {
    condition     = contains(["OPENSEARCH_SERVERLESS", "S3_VECTORS"], var.kb_vector_store_type)
    error_message = "kb_vector_store_type must be OPENSEARCH_SERVERLESS or S3_VECTORS."
  }
}
