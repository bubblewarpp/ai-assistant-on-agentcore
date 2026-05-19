# Nightly Memory Consolidator

data "archive_file" "memory_consolidator" {
  type        = "zip"
  source_dir  = "${path.module}/build/memory_consolidator_code"
  output_path = "${path.module}/build/memory_consolidator.zip"

  depends_on = [null_resource.build]
}

resource "aws_iam_role" "memory_consolidator_role" {
  name = "${local.prefix}-memory-consolidator-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Name        = "${local.prefix}-memory-consolidator-role"
    Environment = var.env
  }
}

resource "aws_iam_role_policy" "memory_consolidator_policy" {
  name = "${local.prefix}-memory-consolidator-policy"
  role = aws_iam_role.memory_consolidator_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Logs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.region}:${data.aws_caller_identity.caller_identity.account_id}:log-group:/aws/lambda/${local.prefix}-memory-consolidator:*"
      },
      {
        Sid    = "ReadChatHistory"
        Effect = "Allow"
        Action = [
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:GetItem"
        ]
        Resource = [
          aws_dynamodb_table.sparky_chat_history.arn,
          "${aws_dynamodb_table.sparky_chat_history.arn}/index/*"
        ]
      },
      {
        Sid    = "InvokeBedrock"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/*",
          "arn:aws:bedrock:*:${data.aws_caller_identity.caller_identity.account_id}:*"
        ]
      },
      {
        Sid    = "WriteAgentCoreMemory"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:CreateEvent"
        ]
        Resource = aws_bedrockagentcore_memory.project_memory.arn
      }
    ]
  })
}

resource "aws_lambda_function" "memory_consolidator" {
  function_name = "${local.prefix}-memory-consolidator"
  description   = "Nightly memory recap and consolidation for Sparky"
  role          = aws_iam_role.memory_consolidator_role.arn

  filename         = data.archive_file.memory_consolidator.output_path
  source_code_hash = data.archive_file.memory_consolidator.output_base64sha256
  handler          = "handler.handler"
  runtime          = "python3.12"
  architectures    = ["x86_64"]

  memory_size = 512
  timeout     = 900

  environment {
    variables = {
      CHAT_HISTORY_TABLE        = aws_dynamodb_table.sparky_chat_history.id
      PROJECT_MEMORY_ID         = aws_bedrockagentcore_memory.project_memory.id
      MODEL_ID                  = var.project_memory_extraction_model_id
      REGION                    = var.region
      LOG_LEVEL                 = "INFO"
      MEMORY_RECAP_TIMEZONE     = "Asia/Jakarta"
      MEMORY_RECAP_MAX_SESSIONS = "200"
    }
  }

  depends_on = [aws_iam_role_policy.memory_consolidator_policy]

  tags = {
    Name        = "${local.prefix}-memory-consolidator"
    Environment = var.env
  }
}

resource "aws_cloudwatch_log_group" "memory_consolidator" {
  name              = "/aws/lambda/${local.prefix}-memory-consolidator"
  retention_in_days = 14

  tags = {
    Name        = "${local.prefix}-memory-consolidator-logs"
    Environment = var.env
  }
}

resource "aws_iam_role" "memory_consolidator_scheduler_role" {
  name = "${local.prefix}-memory-consolidator-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "scheduler.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "memory_consolidator_scheduler_policy" {
  name = "${local.prefix}-memory-consolidator-scheduler-policy"
  role = aws_iam_role.memory_consolidator_scheduler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "InvokeLambda"
      Effect   = "Allow"
      Action   = "lambda:InvokeFunction"
      Resource = aws_lambda_function.memory_consolidator.arn
    }]
  })
}

resource "aws_scheduler_schedule" "memory_consolidator_daily" {
  name                         = "${local.prefix}-memory-consolidator-daily"
  description                  = "Runs Sparky memory consolidation daily at midnight Jakarta time"
  schedule_expression          = "cron(0 0 * * ? *)"
  schedule_expression_timezone = "Asia/Jakarta"
  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.memory_consolidator.arn
    role_arn = aws_iam_role.memory_consolidator_scheduler_role.arn
    input    = jsonencode({ source = "scheduler" })
  }
}
