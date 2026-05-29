# Quick Start Guide

## 5-Minute Setup

### 1. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., ap-southeast-1)
# Enter output format: json
```

### 2. Create Configuration File

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` - **ONLY CHANGE THESE 4 LINES:**

```hcl
email        = "your-actual-email@example.com"  # ← Change this
given_name   = "YourFirstName"                  # ← Change this
family_name  = "YourLastName"                   # ← Change this
region       = "ap-southeast-1"                 # ← Change if needed
```

### 3. Deploy

```bash
# Initialize Terraform
terraform init

# Deploy everything
terraform apply -var-file=terraform.tfvars
```

Type `yes` when prompted.

⏱️ **Deployment takes ~15-20 minutes**

### 4. Get Your App URL

```bash
terraform output amplify_app_url
```

### 5. Access the App

1. Open the URL from step 4
2. Sign in with:
   - Username: `admin`
   - Password: Check your email for temporary password
3. Set a new password when prompted

## That's It! 🎉

Your AI assistant is now running on AWS.

---

## Common Issues

### "Docker not found"
```bash
# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop
```

### "bash: command not found" (Windows)
```bash
# Install Git Bash
# Download from: https://git-scm.com/download/win
```

### "Insufficient permissions"
```bash
# Ensure your AWS user has AdministratorAccess or equivalent
# Check in AWS Console → IAM → Users → Your User → Permissions
```

### "Model not available in region"
```bash
# Change region in terraform.tfvars to us-east-1 or us-west-2
region = "us-east-1"
```

---

## Next Steps

- 📖 Read [README.md](./README.md) for detailed configuration
- 🔧 Customize models in `terraform.tfvars`
- 🎨 Configure frontend in project root `.env`
- 📊 Monitor costs in AWS Cost Explorer

## Cleanup

To delete everything:

```bash
terraform destroy -var-file=terraform.tfvars
```

Type `yes` when prompted.
