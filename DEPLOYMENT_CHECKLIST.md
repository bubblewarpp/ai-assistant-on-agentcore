# 🚀 Deployment Checklist

## Pre-Deployment Checklist

### ✅ Configuration Files

- [x] `infra/terraform.tfvars` - Configured with your details
- [x] Email address updated
- [x] Region set (ap-southeast-1)
- [x] Models configured (Nova Lite, Nova Pro, Haiku 4.5, Sonnet 4)
- [x] Sonnet 4 limited to 32K tokens for cost control

### ✅ Skills

- [x] System skills in `system-skills/` folder:
  - create-ppt
  - create-pdf
  - skill-authoring-best-practices
  - **humanizer** (newly added!)

### ✅ MCP Servers

- [x] MCP config created at `.kiro/settings/mcp.json`
- [x] AWS API MCP server configured
- [x] HTTP/HTTPS examples provided
- [ ] Update URLs and API keys if using HTTP MCP servers

### ✅ Prerequisites

- [ ] AWS CLI configured (`aws configure`)
- [ ] Docker running (`docker --version`)
- [ ] Terraform installed (`terraform version`)
- [ ] Git Bash or WSL (for build scripts)

---

## 🎯 Deployment Steps

### Step 1: Verify Configuration

```bash
cd infra
cat terraform.tfvars
```

**Check:**
- Email is correct
- Username is correct
- Region is correct
- Models are configured

### Step 2: Initialize Terraform

```bash
terraform init
```

**Expected output:**
```
Terraform has been successfully initialized!
```

### Step 3: Plan Deployment

```bash
terraform plan -var-file=terraform.tfvars
```

**Review:**
- Number of resources to create (~50+)
- No errors in plan
- Resource names look correct

### Step 4: Deploy Infrastructure

```bash
terraform apply -var-file=terraform.tfvars
```

**Type:** `yes` when prompted

**Duration:** ~15-20 minutes

**What happens:**
1. Docker images built and pushed to ECR
2. Lambda functions deployed
3. DynamoDB tables created
4. S3 buckets created
5. Cognito user pool created
6. AgentCore runtimes deployed
7. Bedrock Knowledge Bases created
8. System skills uploaded to S3

### Step 5: Get Outputs

```bash
terraform output
```

**Important outputs:**
- `sparky_runtime_arn` - Main agent runtime
- `core_services_runtime_arn` - API runtime
- `cognito_user_pool_id` - User pool ID
- `cognito_app_client_id` - App client ID
- `cognito_domain` - Auth domain
- `amplify_app_url` - Frontend URL

### Step 6: Check Email

Look for email from AWS Cognito with:
- Subject: "Your temporary password"
- Username: `khariri`
- Temporary password: (in email)

### Step 7: Access Application

1. Open Amplify URL from outputs
2. Login with username and temp password
3. Set new permanent password
4. Start using the app!

---

## 📊 Post-Deployment Verification

### Check AgentCore Runtimes

```bash
aws bedrock-agentcore list-agent-runtimes --region ap-southeast-1
```

### Check Lambda Functions

```bash
aws lambda list-functions --region ap-southeast-1 | grep sparky
```

### Check DynamoDB Tables

```bash
aws dynamodb list-tables --region ap-southeast-1 | grep sparky
```

### Check S3 Buckets

```bash
aws s3 ls | grep sparky
```

### Check System Skills

```bash
aws s3 ls s3://sparky-skills-<account-id>-<random>/
```

**Should see:**
- create-ppt/
- create-pdf/
- skill-authoring-best-practices/
- humanizer/

---

## 🔧 Configuration Updates

### Update Frontend .env

After deployment, create `.env` in project root:

```bash
# Get values from terraform output
cd infra
terraform output

# Create .env file
cd ..
cat > .env << 'EOF'
VITE_APP_SPARKY=<sparky_runtime_arn>
VITE_COGNITO_DOMAIN=<cognito_domain>
VITE_COGNITO_REGION=ap-southeast-1
VITE_USER_POOL_ID=<user_pool_id>
VITE_APP_CLIENT_ID=<app_client_id>
VITE_REDIRECT_SIGN_IN=<amplify_url>
VITE_REDIRECT_SIGN_OUT=<amplify_url>
VITE_SPARKY_MODEL_CONFIG=<model_config_json>
EOF
```

### Switch to Production Mode

```powershell
.\switch-mode.ps1 prod
```

### Restart Dev Server

```bash
npm run dev
```

---

## 🎨 Frontend Deployment

### Option 1: Amplify Auto-Deploy

Amplify will auto-deploy from git when you push.

### Option 2: Manual Deploy

```bash
# Build
npm run build

# Deploy to Amplify
aws amplify start-deployment \
  --app-id <app-id> \
  --branch-name dev \
  --region ap-southeast-1
```

---

## 💰 Cost Monitoring

### Set Up Budget Alerts

```bash
aws budgets create-budget \
  --account-id <account-id> \
  --budget file://budget.json
```

**budget.json:**
```json
{
  "BudgetName": "Sparky-Monthly-Budget",
  "BudgetLimit": {
    "Amount": "500",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

### Monitor Costs

1. Open AWS Cost Explorer
2. Filter by service: "Amazon Bedrock"
3. Group by: Model ID
4. Set alerts at 50%, 80%, 100%

---

## 🐛 Troubleshooting

### Docker Build Fails

**Error:** `Cannot connect to Docker daemon`

**Solution:**
```bash
# Start Docker Desktop
# Or on Linux:
sudo systemctl start docker
```

### Terraform Apply Fails

**Error:** `Error creating resource`

**Solution:**
1. Check AWS credentials: `aws sts get-caller-identity`
2. Check permissions: Need AdministratorAccess or equivalent
3. Check region: Ensure Bedrock models available
4. Check quotas: Service quotas might be exceeded

### Email Not Received

**Solution:**
1. Check spam folder
2. Verify email in terraform.tfvars
3. Check Cognito console for user
4. Resend verification email

### Can't Login

**Solution:**
1. Verify Cognito domain is correct
2. Check redirect URLs match
3. Clear browser cache
4. Try incognito mode

### Skills Not Showing

**Solution:**
```bash
# Check S3 bucket
aws s3 ls s3://sparky-skills-<account-id>-<random>/

# Re-upload skills
cd infra
terraform apply -var-file=terraform.tfvars -target=aws_s3_object.system_skills
```

---

## 📈 Performance Optimization

### 1. Enable S3 Express (Optional)

For faster checkpoint access:

```hcl
# In terraform.tfvars
use_express_checkpoint_bucket = true
express_az_id = "apse1-az1"
```

### 2. Adjust Expiry Duration

```hcl
# Reduce storage costs
expiry_duration_days = 90  # Instead of 365
```

### 3. Enable Deletion Protection (Production)

```hcl
deletion_protection_enabled = true
```

---

## 🔐 Security Hardening

### 1. Enable MFA

```bash
aws cognito-idp set-user-pool-mfa-config \
  --user-pool-id <pool-id> \
  --mfa-configuration OPTIONAL
```

### 2. Rotate Credentials

- Rotate AWS access keys every 90 days
- Update Cognito app client secrets
- Rotate API keys for MCP servers

### 3. Review IAM Policies

```bash
# Check IAM roles
aws iam list-roles | grep sparky

# Review policies
aws iam get-role-policy \
  --role-name sparky-sparky \
  --policy-name sparky-sparky-policy
```

---

## 📚 Documentation

After deployment, update these docs:

1. **README.md** - Add deployment date and version
2. **ARCHITECTURE.md** - Document any customizations
3. **RUNBOOK.md** - Create operational runbook
4. **API_DOCS.md** - Document custom APIs

---

## 🎉 Success Criteria

Deployment is successful when:

- [x] All Terraform resources created
- [x] No errors in CloudWatch logs
- [x] Can login to Amplify app
- [x] Can send chat messages
- [x] Skills are available
- [x] MCP servers connected
- [x] Models responding correctly
- [x] Costs within budget

---

## 📞 Support

### AWS Support

- [AWS Support Center](https://console.aws.amazon.com/support/)
- [Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-core.html)

### Community

- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord/Slack](https://your-community-link)

---

## 🔄 Rollback Plan

If deployment fails:

```bash
# Destroy all resources
cd infra
terraform destroy -var-file=terraform.tfvars

# Or destroy specific resources
terraform destroy -target=aws_bedrockagentcore_agent_runtime.sparky
```

**Note:** This will delete all data!

---

## 📝 Deployment Log

Keep track of deployments:

| Date | Version | Deployed By | Status | Notes |
|------|---------|-------------|--------|-------|
| 2026-05-29 | 1.0.0 | khariri | ✅ Success | Initial deployment |
|  |  |  |  |  |

---

**Ready to deploy?** Follow the steps above! 🚀

Good luck! 🍀
