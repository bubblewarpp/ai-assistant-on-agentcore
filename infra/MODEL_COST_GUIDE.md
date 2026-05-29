# Model Cost Guide & Comparison

## 💰 Cost Overview

Panduan ini membantu Anda memilih model yang tepat berdasarkan budget dan kebutuhan.

---

## 📊 Model Pricing (Bedrock - ap-southeast-1)

### Amazon Nova Models (Cheapest)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Max Tokens |
|-------|----------------------|------------------------|------------|
| **Nova Lite** | ~$0.06 | ~$0.24 | 8,000 |
| **Nova Pro** | ~$0.80 | ~$3.20 | 8,000 |

### Claude Models (Premium)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Max Tokens | Limited To |
|-------|----------------------|------------------------|------------|------------|
| **Haiku 4.5** | $0.80 | $4.00 | 64,000 | 64K |
| **Sonnet 4** | $3.00 | $15.00 | 200,000 | **32K** ⚠️ |

⚠️ **Sonnet 4 dilimit ke 32K tokens untuk cost control!**

---

## 💡 Cost Comparison Examples

### Scenario 1: Simple Chat (1K tokens in, 500 tokens out)

| Model | Cost per Request | Cost per 1000 Requests |
|-------|------------------|------------------------|
| Nova Lite | $0.00018 | $0.18 |
| Nova Pro | $0.00240 | $2.40 |
| Haiku 4.5 | $0.00280 | $2.80 |
| Sonnet 4 | $0.01050 | $10.50 |

**Winner: Nova Lite** 🏆 (58x cheaper than Sonnet!)

---

### Scenario 2: Long Context (10K tokens in, 2K tokens out)

| Model | Cost per Request | Cost per 1000 Requests |
|-------|------------------|------------------------|
| Nova Lite | $0.00108 | $1.08 |
| Nova Pro | $0.01440 | $14.40 |
| Haiku 4.5 | $0.01600 | $16.00 |
| Sonnet 4 | $0.06000 | $60.00 |

**Winner: Nova Lite** 🏆 (55x cheaper than Sonnet!)

---

### Scenario 3: Code Generation (5K tokens in, 5K tokens out)

| Model | Cost per Request | Cost per 1000 Requests |
|-------|------------------|------------------------|
| Nova Lite | $0.00150 | $1.50 |
| Nova Pro | $0.02000 | $20.00 |
| Haiku 4.5 | $0.02400 | $24.00 |
| Sonnet 4 | $0.09000 | $90.00 |

**Winner: Nova Lite** 🏆 (60x cheaper than Sonnet!)

---

## 🎯 When to Use Each Model

### Amazon Nova Lite (Default) ✅
**Best for:**
- ✅ General chat conversations
- ✅ Simple Q&A
- ✅ Basic code assistance
- ✅ High-volume usage
- ✅ Cost-sensitive applications

**Limitations:**
- ❌ Max 8K tokens (shorter context)
- ❌ Less sophisticated reasoning
- ❌ May struggle with complex tasks

**Monthly Cost Estimate:**
- 10K requests/month: **$1.80**
- 50K requests/month: **$9.00**
- 100K requests/month: **$18.00**

---

### Amazon Nova Pro 💪
**Best for:**
- ✅ More complex reasoning
- ✅ Better code generation
- ✅ Improved accuracy
- ✅ Still cost-effective

**Limitations:**
- ❌ Max 8K tokens
- ❌ 13x more expensive than Lite

**Monthly Cost Estimate:**
- 10K requests/month: **$24.00**
- 50K requests/month: **$120.00**
- 100K requests/month: **$240.00**

---

### Claude Haiku 4.5 ⚡
**Best for:**
- ✅ Fast responses
- ✅ Longer context (64K)
- ✅ Good balance of speed/quality
- ✅ Complex reasoning

**Limitations:**
- ❌ More expensive than Nova
- ❌ Overkill for simple tasks

**Monthly Cost Estimate:**
- 10K requests/month: **$28.00**
- 50K requests/month: **$140.00**
- 100K requests/month: **$280.00**

---

### Claude Sonnet 4 🚀 (LIMITED)
**Best for:**
- ✅ Most sophisticated reasoning
- ✅ Complex problem solving
- ✅ High-quality code generation
- ✅ Critical tasks only

**Limitations:**
- ❌ **EXPENSIVE!** (5x more than Haiku)
- ❌ **Limited to 32K tokens** (not full 200K)
- ❌ Should be used sparingly

**Monthly Cost Estimate (with 32K limit):**
- 10K requests/month: **$105.00**
- 50K requests/month: **$525.00**
- 100K requests/month: **$1,050.00**

⚠️ **Without limit (200K tokens), costs could be 6x higher!**

---

## 🛡️ Cost Control Strategies

### 1. Token Limits (Already Configured)

```hcl
# Sonnet 4 - Limited to 32K instead of 200K
max_tokens = 32000  # Saves ~84% on max token costs!

# Budget mapping for reasoning levels
budget_mapping = {
  "1" = 8000   # Low - Cheapest
  "2" = 16000  # Medium
  "3" = 24000  # High
  "4" = 32000  # Max - Most expensive
}
```

### 2. Default to Cheaper Models

```hcl
# Use Nova Lite as default
default_model_id = "amazon-nova-lite"
```

### 3. Model Selection Strategy

**Recommended Flow:**
1. **Start with Nova Lite** for all requests
2. **Upgrade to Nova Pro** if quality is insufficient
3. **Use Haiku 4.5** for complex reasoning
4. **Reserve Sonnet 4** for critical tasks only

### 4. Monitor Usage

Track costs in AWS Cost Explorer:
- Filter by service: "Amazon Bedrock"
- Group by: Model ID
- Set budget alerts

---

## 📈 Cost Projection Calculator

### Formula:
```
Cost = (Input_Tokens × Input_Price) + (Output_Tokens × Output_Price)
```

### Example Calculation (Sonnet 4):
```
Input: 10,000 tokens × $3.00/1M = $0.03
Output: 5,000 tokens × $15.00/1M = $0.075
Total: $0.105 per request
```

### Monthly Projection:
```
Daily requests: 100
Monthly requests: 3,000
Monthly cost: 3,000 × $0.105 = $315
```

---

## 💰 Budget Recommendations

### Startup/Testing ($50/month)
- **Primary**: Nova Lite (unlimited)
- **Secondary**: Nova Pro (limited use)
- **Premium**: Haiku 4.5 (rare)
- **Avoid**: Sonnet 4

### Small Business ($200/month)
- **Primary**: Nova Lite (high volume)
- **Secondary**: Nova Pro (moderate use)
- **Premium**: Haiku 4.5 (regular use)
- **Rare**: Sonnet 4 (critical only)

### Enterprise ($1000+/month)
- **Primary**: Nova Pro (high volume)
- **Secondary**: Haiku 4.5 (regular use)
- **Premium**: Sonnet 4 (frequent use)
- **Unlimited**: All models available

---

## 🔧 How to Change Limits

### Increase Sonnet 4 Limit (Not Recommended)

Edit `infra/terraform.tfvars`:

```hcl
{
  id         = "claude-sonnet-4"
  max_tokens = 64000  # Increase from 32K to 64K
  # WARNING: This doubles your max cost!
}
```

### Add More Budget Levels

```hcl
budget_mapping = {
  "1" = 4000   # Extra Low
  "2" = 8000   # Low
  "3" = 16000  # Medium
  "4" = 24000  # High
  "5" = 32000  # Max
}
```

### Remove Sonnet 4 Entirely

Delete the Sonnet 4 block from `sparky_models.models` array.

---

## 📊 Real-World Cost Examples

### Example 1: Customer Support Bot
- **Volume**: 10,000 chats/month
- **Avg tokens**: 1K in, 500 out
- **Model**: Nova Lite
- **Monthly cost**: **$1.80**

### Example 2: Code Assistant
- **Volume**: 1,000 requests/month
- **Avg tokens**: 5K in, 5K out
- **Model**: Nova Pro
- **Monthly cost**: **$20.00**

### Example 3: Complex Analysis
- **Volume**: 500 requests/month
- **Avg tokens**: 10K in, 5K out
- **Model**: Sonnet 4 (32K limit)
- **Monthly cost**: **$52.50**

---

## ⚠️ Cost Warnings

### 1. Sonnet 4 Without Limits
```
Full 200K tokens = $600 per request!
10 requests = $6,000
100 requests = $60,000
```

### 2. Accidental High Volume
```
1M requests × $0.105 = $105,000
Always set budget alerts!
```

### 3. Long Context Abuse
```
Using max tokens on every request
= Unnecessary costs
= Use only what you need
```

---

## 🎯 Best Practices

1. **Start Cheap** - Use Nova Lite by default
2. **Upgrade Selectively** - Only when quality matters
3. **Monitor Costs** - Check AWS Cost Explorer weekly
4. **Set Alerts** - Budget alerts at 50%, 80%, 100%
5. **Limit Tokens** - Don't use max unless needed
6. **Cache Results** - Avoid duplicate requests
7. **Batch Requests** - Combine when possible

---

## 📚 Additional Resources

- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [AWS Cost Explorer](https://console.aws.amazon.com/cost-management/)
- [AWS Budgets](https://console.aws.amazon.com/billing/home#/budgets)

---

## 🎉 Summary

**Current Configuration:**
- ✅ Nova Lite (default) - Cheapest
- ✅ Nova Pro - Good balance
- ✅ Haiku 4.5 - Fast & capable
- ✅ Sonnet 4 - **Limited to 32K** for cost control

**Estimated Monthly Cost (moderate use):**
- Nova Lite: $10-20
- Nova Pro: $50-100
- Haiku 4.5: $50-100
- Sonnet 4: $100-200
- **Total: $210-420/month**

**Without Sonnet 4 limit:**
- Could easily exceed $1,000-2,000/month!

**You're protected!** 🛡️
