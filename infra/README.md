# Infrastructure Deployment Guide

## Prerequisites

Before deploying, ensure you have:

1. **AWS CLI** configured with appropriate credentials
   ```bash
   aws configure
   ```

2. **Terraform** >= 1.5 installed
   ```bash
   terraform version
   ```

3. **Docker** with buildx support
   ```bash
   docker --version
   docker buildx version
   ```

4. **Git Bash or WSL** (for Windows users) to run build scripts

5. **Python 3.12** (if using OpenSearch Serverless)
   ```bash
   pip install opensearch-py requests-aws4auth boto3
   ```

## Configuration

### 1. Create terraform.tfvars

Copy the example file and customize it:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
env          = "dev"
region       = "ap-southeast-1"  # Your preferred AWS region
username     = "admin"
email        = "your-email@example.com"
given_name   = "Your"
family_name  = "Name"
```

**Important:** `terraform.tfvars` is gitignored and contains sensitive information. Never commit it to version control.

### 2. Key Configuration Options

#### Region Selection
Choose a region where Bedrock models are available:
- `us-east-1` - US East (N. Virginia)
- `us-west-2` - US West (Oregon)
- `ap-southeast-1` - Asia Pacific (Singapore)
- `eu-west-1` - Europe (Ireland)

#### Vector Store Type
- `S3_VECTORS` (recommended) - Simpler, lower cost
- `OPENSEARCH_SERVERLESS` - More features, higher cost

#### Expiry Duration
Set data retention period (30-365 days):
```hcl
expiry_duration_days = 365
```

#### Deletion Protection
For production environments:
```hcl
deletion_protection_enabled = true
```

## Deployment

### Option 1: Using Deployment Script (Recommended)

```bash
# From project root
./deployment.sh
```

Follow the interactive prompts to deploy backend, frontend, or both.

### Option 2: Manual Terraform Deployment

```bash
# Navigate to infra directory
cd infra

# Initialize Terraform
terraform init

# Review the deployment plan
terraform plan -var-file=terraform.tfvars

# Apply the configuration
terraform apply -var-file=terraform.tfvars
```

## Post-Deployment

### 1. Get Outputs

```bash
terraform output
```

Important outputs:
- `sparky_runtime_arn` - AgentCore runtime ARN
- `core_services_runtime_arn` - Core Services runtime ARN
- `cognito_user_pool_id` - Cognito User Pool ID
- `cognito_app_client_id` - Cognito App Client ID
- `amplify_app_url` - Frontend URL

### 2. Configure Frontend

The deployment script automatically creates `.env` file in the project root with:
```env
VITE_APP_SPARKY=<sparky_runtime_arn>
VITE_COGNITO_DOMAIN=<cognito_domain>
VITE_COGNITO_REGION=<region>
VITE_USER_POOL_ID=<user_pool_id>
VITE_APP_CLIENT_ID=<app_client_id>
VITE_REDIRECT_SIGN_IN=<amplify_url>
VITE_REDIRECT_SIGN_OUT=<amplify_url>
VITE_SPARKY_MODEL_CONFIG=<model_config_json>
```

### 3. Access the Application

1. Navigate to the Amplify URL from outputs
2. Sign in with the username/email configured in `terraform.tfvars`
3. Use the temporary password sent to your email
4. Set a new permanent password

## Troubleshooting

### Docker Build Fails

Ensure Docker daemon is running and buildx is available:
```bash
docker buildx create --use --name multiarch
```

### Build Script Fails on Windows

Install Git Bash or WSL, or convert `build.sh` to PowerShell:
```powershell
# Alternative: Run build commands manually
mkdir -p build/kb_indexer_code
mkdir -p build/expiry_cleanup_code
mkdir -p build/task_executor_code
# ... copy files as per build.sh
```

### Terraform State Lock

If deployment is interrupted:
```bash
terraform force-unlock <lock-id>
```

### OpenSearch Index Creation Fails

Ensure Python dependencies are installed:
```bash
pip install opensearch-py requests-aws4auth boto3
```

## Cleanup

To destroy all resources:

```bash
# Using destroy script
./destroy.sh

# Or manually
cd infra
terraform destroy -var-file=terraform.tfvars
```

**Warning:** This will delete all data. Ensure you have backups if needed.

## Security Notes

1. **Never commit** `terraform.tfvars` to version control
2. **Enable deletion protection** for production environments
3. **Use strong passwords** for Cognito users
4. **Review IAM policies** before deployment
5. **Enable MFA** for production Cognito users
6. **Rotate credentials** regularly

## Architecture Overview

The infrastructure deploys:

- **2 AgentCore Runtimes** (Sparky + Core Services)
- **3 Lambda Functions** (KB Indexer, Expiry Cleanup, Task Executor)
- **DynamoDB Tables** (Chat History, Tool Config, Skills, Projects, etc.)
- **S3 Buckets** (Artifacts, Skills, Projects, Checkpoints)
- **Bedrock Knowledge Bases** (Chat KB, Projects KB)
- **Cognito** (User Pool, App Clients)
- **Amplify** (Frontend Hosting)
- **AgentCore Memory** (Conversation Memory)
- **EventBridge Scheduler** (Scheduled Tasks)

## Cost Estimation

Approximate monthly costs (us-east-1, light usage):

- AgentCore Runtimes: $50-100
- DynamoDB: $5-20
- S3: $5-15
- Lambda: $1-5
- Bedrock KB (S3 Vectors): $10-30
- Cognito: Free tier
- Amplify: Free tier or $5-10

**Total: ~$75-180/month** (varies by usage)

For production workloads, costs will be higher.

## Support

For issues or questions:
1. Check CloudWatch Logs for runtime errors
2. Review Terraform plan output
3. Verify AWS service quotas
4. Check Bedrock model availability in your region
