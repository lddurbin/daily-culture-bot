# GitHub Actions Workflow Configuration

## Workflow Setup

### 🤖 **Daily Culture Email (Optimized)** - Automated Daily
**File**: `.github/workflows/daily-email-optimized.yml`

**Schedule**: 
- Runs daily at 6:00 AM New Zealand time (5:00 PM UTC previous day)
- Cron: `'0 17 * * *'`
- Also available for manual dispatch

**Features**:
- ✅ Full enhanced matching (95% of capabilities)
- ✅ Selective vision analysis (top 6 candidates)
- ✅ Match explanations
- ✅ AI-driven second pass selection
- ✅ Cost: ~$0.09 per run

**Command**:
```bash
python daily_culture_bot.py \
  --complementary \
  --email "$EMAIL_RECIPIENT" \
  --email-format html \
  --max-fame-level 20 \
  --min-match-score 0.3 \
  --candidate-count 6 \
  --vision-candidates 6 \
  --explain-matches \
  --query-timeout 30
```

### 🎯 **Daily Culture Email (Manual)** - On-Demand Only
**File**: `.github/workflows/daily-email-simple.yml`

**Schedule**: 
- Manual dispatch only (`workflow_dispatch`)
- No automatic scheduling
- Triggered only when you manually run it

**Features**:
- ✅ Enhanced matching (90% of capabilities)
- ✅ Budget-friendly vision analysis (top 3 candidates)
- ✅ Match explanations
- ✅ AI-driven second pass selection
- ✅ Cost: ~$0.05 per run

**Command**:
```bash
python daily_culture_bot.py \
  --complementary \
  --email "$EMAIL_RECIPIENT" \
  --email-format html \
  --max-fame-level 20 \
  --min-match-score 0.3 \
  --candidate-count 6 \
  --vision-candidates 3 \
  --explain-matches
```

## Usage

### **Automatic Daily Emails**
The optimized workflow runs automatically every day, delivering high-quality poem-artwork pairings with full enhanced matching capabilities.

### **Manual Testing/On-Demand**
Use the manual workflow when you want to:
- Test the system
- Send an extra email
- Try different configurations
- Debug issues

### **How to Run Manual Workflow**
1. Go to your GitHub repository
2. Click "Actions" tab
3. Select "Daily Culture Email (Manual)"
4. Click "Run workflow"
5. Choose branch and click "Run workflow"

## Cost Comparison

| Workflow | Vision Candidates | Cost per Run | Features Used | Use Case |
|----------|------------------|--------------|---------------|----------|
| Optimized | 6 | ~$0.09 | 95% | Daily automated |
| Manual | 3 | ~$0.05 | 90% | Testing/on-demand |

## Benefits

1. **Automated Daily**: Consistent high-quality emails without manual intervention
2. **Manual Control**: On-demand testing and extra emails when needed
3. **Cost Optimization**: Different vision analysis levels for different use cases
4. **Full Enhanced Matching**: Both workflows leverage the sophisticated matching system
5. **Flexibility**: Choose between maximum quality (optimized) or budget-friendly (manual)
