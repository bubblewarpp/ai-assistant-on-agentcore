# Deployment Error Troubleshooting Guide

## Common Errors & Solutions

### 1. Permission Denied

**Error:**
```
bash: ./deployment.sh: Permission denied
```

**Solution:**
```bash
chmod +x deployment.sh
chmod +x destroy.sh
./deployment.sh
```

---

### 2. Command Not Found (jq)

**Error:**
```
jq: command not found
```

**Solution:**
```bash
# Install jq
# Windows (Git Bash):
curl -L -o /usr/bin/jq.exe https://github.com/stedolan/jq/releases/latest/download/jq-win64.exe

# Or use Chocolatey:
choco install jq

# Or use Scoop:
scoop install jq
```

---

### 3. Docker Not Running

**Error:**
```
Cannot connect to the Docker daemon
```

**Solution:**
```bash
# Start Docker Desktop
# Then verify:
docker ps
```

---

### 4. AWS Credentials Not Found

**Error:**
```
Unable to locate credentials
```

**Solution:**
```bash
# Configure AWS CLI
aws configure

# Or check current credentials:
aws sts get-caller-identity
```

---

### 5. Terraform Not Found

**Error:**
```
terraform: command not found
```

**Solution:**
```bash
# Install Terraform
# Download from: https://www.terraform.io/downloads

# Or use Chocolatey:
choco install terraform

# Verify:
terraform version
```

---

### 6. Node.js Version Too Old

**Error:**
```
Error: Node.js v20+ is required
```

**Solution:**
```bash
# Check current version:
node --version

# Install Node 20+ from: https://nodejs.org/

# Or use nvm:
nvm install 20
nvm use 20
```

---

### 7. Terraform Init Failed

**Error:**
```
Error: Failed to query available provider packages
```

**Solution:**
```bash
cd infra
rm -rf .terraform .terraform.lock.hcl
terraform init
```

---

### 8. Docker Build Failed

**Error:**
```
Error building Docker image
```

**Solution:**
```bash
# Check Docker is running:
docker ps

# Check disk space:
df -h

# Clean Docker cache:
docker system prune -a
```

---

### 9. Terraform Apply Failed - Resource Already Exists

**Error:**
```
Error: Resource already exists
```

**Solution:**
```bash
# Import existing resource or destroy first:
cd infra
terraform destroy -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

---

### 10. Amplify Deployment Failed

**Error:**
```
Failed to create Amplify deployment
```

**Solution:**
```bash
# Check AWS region:
aws configure get region

# Verify Amplify app exists:
aws amplify list-apps --region ap-southeast-1

# Check .deployment.config file:
cat .deployment.config
```

---

## Quick Diagnostic Commands

Run these to check your environment:

```bash
# 1. Check AWS credentials
echo "=== AWS Credentials ==="
aws sts get-caller-identity

# 2. Check Docker
echo "=== Docker ==="
docker --version
docker ps

# 3. Check Terraform
echo "=== Terraform ==="
terraform version

# 4. Check Node.js
echo "=== Node.js ==="
node --version
npm --version

# 5. Check jq
echo "=== jq ==="
jq --version

# 6. Check Git Bash
echo "=== Git Bash ==="
bash --version

# 7. Check current directory
echo "=== Current Directory ==="
pwd
ls -la

# 8. Check terraform.tfvars
echo "=== Terraform Variables ==="
cat infra/terraform.tfvars
```

---

## Step-by-Step Manual Deployment

If `./deployment.sh` fails, try manual deployment:

### Step 1: Backend Deployment

```bash
cd infra

# Initialize Terraform
terraform init

# Plan (review changes)
terraform plan -var-file=terraform.tfvars

# Apply (deploy)
terraform apply -var-file=terraform.tfvars

# Get outputs
terraform output
```

### Step 2: Create .env File

```bash
cd ..

# Get values from Terraform
cd infra
SPARKY_ARN=$(terraform output -raw agent_runtime_arn_escaped)
CORE_ARN=$(terraform output -raw core_services_runtime_arn_escaped)
COGNITO_REGION=$(terraform output -raw region)
USER_POOL_ID=$(terraform output -raw user_pool_id)
APP_CLIENT_ID=$(terraform output -raw app_client_id)
COGNITO_DOMAIN=$(terraform output -raw cognito_domain)
APP_ID=$(terraform output -raw amplify_app_id)
MODEL_CONFIG=$(terraform output -raw sparky_model_config_frontend)
cd ..

# Create .env
cat > .env << EOF
VITE_APP_SPARKY=$SPARKY_ARN
VITE_CORE_SERVICES_ENDPOINT=$CORE_ARN
VITE_COGNITO_REGION=$COGNITO_REGION
VITE_USER_POOL_ID=$USER_POOL_ID
VITE_APP_CLIENT_ID=$APP_CLIENT_ID
VITE_COGNITO_DOMAIN=$COGNITO_DOMAIN
VITE_REDIRECT_SIGN_IN=https://dev.$APP_ID.amplifyapp.com
VITE_REDIRECT_SIGN_OUT=https://dev.$APP_ID.amplifyapp.com
VITE_SPARKY_MODEL_CONFIG=$MODEL_CONFIG
EOF
```

### Step 3: Frontend Deployment

```bash
# Install dependencies
npm install

# Build
npm run build

# Deploy to Amplify (manual)
cd dist
zip -r ../build.zip .
cd ..

# Upload to Amplify
aws amplify create-deployment \
  --app-id $APP_ID \
  --branch-name dev \
  --region $COGNITO_REGION
```

---

## Specific Error Messages

### Error: "No such file or directory"

**Check:**
```bash
# Are you in the right directory?
pwd
# Should be: /d/ACode/ai-assistant-on-agentcore

# List files:
ls -la
# Should see: deployment.sh, destroy.sh, infra/, src/, etc.
```

### Error: "Invalid choice"

**Check:**
- Are you entering numbers correctly? (1, 2, or 3)
- Press Enter after typing

### Error: "Email validation failed"

**Check:**
- Email format: `user@domain.com`
- No spaces
- Valid domain

### Error: "Terraform state locked"

**Solution:**
```bash
cd infra
terraform force-unlock <LOCK_ID>
```

---

## Debug Mode

Run deployment with debug output:

```bash
# Enable debug
set -x
./deployment.sh

# Or run commands manually to see errors
bash -x ./deployment.sh
```

---

## Clean Start

If everything fails, start fresh:

```bash
# 1. Clean Terraform
cd infra
rm -rf .terraform .terraform.lock.hcl terraform.tfstate*
cd ..

# 2. Clean Node modules
rm -rf node_modules package-lock.json

# 3. Clean build artifacts
rm -rf dist build.zip

# 4. Clean deployment config
rm -f .deployment.config .env

# 5. Start over
./deployment.sh
```

---

## Get Help

If still stuck, provide these details:

1. **Error message** (full text)
2. **Command you ran**
3. **Output of diagnostic commands** (above)
4. **Operating system** (Windows + Git Bash)
5. **AWS region** (ap-southeast-1)

---

## Contact

- Check logs in: `infra/terraform.log`
- Check CloudWatch logs in AWS Console
- Check Amplify build logs in AWS Console

---

**Most Common Fix:**

```bash
# 90% of errors are fixed by:
chmod +x deployment.sh
./deployment.sh
```

**Second Most Common Fix:**

```bash
# Install jq:
curl -L -o /usr/bin/jq.exe https://github.com/stedolan/jq/releases/latest/download/jq-win64.exe
```

**Third Most Common Fix:**

```bash
# Start Docker Desktop
docker ps
```

---

**Share your error message and I'll help you fix it!** 🔧
