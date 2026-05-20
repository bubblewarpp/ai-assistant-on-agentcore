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
  description = "Centralized Sparky AI assistant model configuration. Single source of truth for backend and frontend."
  type = object({
    default_model_id = string
    models = list(object({
      id             = string
      model_id       = string
      label          = string
      description    = string
      max_tokens     = number
      reasoning_type = string
      budget_mapping = optional(map(number), {})
      effort_mapping = optional(map(string), {})
      beta_flags     = optional(list(string), [])
    }))
  })

  validation {
    condition = alltrue([
      for m in var.sparky_models.models :
      contains(["budget", "effort", "none"], m.reasoning_type)
    ])
    error_message = "Each model's reasoning_type must be 'budget', 'effort', or 'none'."
  }


  validation {
    condition = contains(
      [for m in var.sparky_models.models : m.id],
      var.sparky_models.default_model_id
    )
    error_message = "default_model_id must reference one of the defined model IDs."
  }

  default = {
    default_model_id = "claude-haiku-4.5"
    models = [
      {
        id             = "claude-haiku-4.5"
        model_id       = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
        label          = "Claude Haiku 4.5"
        description    = "Default balanced model"
        max_tokens     = 64000
        reasoning_type = "budget"
        budget_mapping = { "1" = 16000, "2" = 30000, "3" = 42000, "4" = 63999 }
        effort_mapping = {}
        beta_flags     = ["interleaved-thinking-2025-05-14", "fine-grained-tool-streaming-2025-05-14"]
      },
      {
        id             = "amazon-nova-2-lite"
        model_id       = "us.amazon.nova-2-lite-v1:0"
        label          = "Amazon Nova 2 Lite"
        description    = "Low-cost Amazon model"
        max_tokens     = 64000
        reasoning_type = "none"
        budget_mapping = {}
        effort_mapping = {}
        beta_flags     = []
      },
      {
        id             = "kimi-k2.5"
        model_id       = "moonshotai.kimi-k2.5"
        label          = "Kimi K2.5"
        description    = "Balanced low-cost model"
        max_tokens     = 16000
        reasoning_type = "none"
        budget_mapping = {}
        effort_mapping = {}
        beta_flags     = []
      },
      {
        id             = "mistral-large-3"
        model_id       = "mistral.mistral-large-3-675b-instruct"
        label          = "Mistral Large 3"
        description    = "Balanced low-cost model"
        max_tokens     = 32000
        reasoning_type = "none"
        budget_mapping = {}
        effort_mapping = {}
        beta_flags     = []
      },
      {
        id             = "deepseek-v3.2"
        model_id       = "deepseek.v3.2"
        label          = "DeepSeek V3.2"
        description    = "Low-cost reasoning and coding model"
        max_tokens     = 8000
        reasoning_type = "none"
        budget_mapping = {}
        effort_mapping = {}
        beta_flags     = []
      }
    ]
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
