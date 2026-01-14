# LAUTECH AgentCore - Production Deployment

AI-powered chatbot for LAUTECH university information system, deployed on AWS using Amazon Bedrock AgentCore.

## 🚀 Quick Start

### Prerequisites
- AWS account with Bedrock model access
- AWS CLI configured
- Python 3.10+
- AgentCore CLI installed

### Deploy to AWS

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_SESSION_TOKEN="your-token"  # if using temporary credentials

# Deploy agent
agentcore launch --env USE_POSTGRES=true --env DB_SECRET_NAME=lautech/rds/credentials --env AWS_REGION=us-east-1

# Test agent
agentcore invoke '{"prompt": "What is the dance fee?"}'
```

## 📁 Project Structure

```
lautech/
├── lautech_agentcore.py      # Main agent application
├── db_utils.py                # Database abstraction layer (SQLite + PostgreSQL)
├── requirements.txt           # Python dependencies
├── .bedrock_agentcore.yaml    # AgentCore configuration
├── data/                      # CSV data files
│   ├── courses.csv
│   ├── fees.csv
│   ├── academic_calendar.csv
│   └── hostels.csv
├── setup/                     # Setup and migration scripts
│   ├── setup_rds.py          # RDS PostgreSQL creation
│   ├── migrate_to_rds.py     # SQLite to PostgreSQL migration
│   ├── update_iam_for_rds.py # IAM permissions setup
│   └── request_bedrock_access.py # Helper for model access
├── docs/                      # Documentation
│   ├── PRODUCTION.md         # Production deployment guide
│   ├── RDS_SETUP_COMPLETE.md # RDS setup details
│   └── DATA_GUIDE.md         # Data structure reference
├── scripts/                   # Utility scripts
│   └── backup_database.py    # Database backup utility
└── legacy/                    # Legacy components (not needed for AgentCore)
    ├── admin_panel.py        # Old admin panel
    ├── web_dashboard.py      # Old web dashboard
    └── whatsapp_bot.py       # WhatsApp integration (optional)
```

## 🗄️ Database

**Production:** Amazon RDS PostgreSQL 16.11
- Endpoint: `lautech-agentcore-db.c2x6a0cseynp.us-east-1.rds.amazonaws.com`
- Credentials: Stored in AWS Secrets Manager (`lautech/rds/credentials`)

**Development:** SQLite (fallback)
- Database: `lautech_data.db`

## 📊 Deployment Details

### AWS Resources
- **Account:** 715841330456
- **Region:** us-east-1
- **Agent ARN:** `arn:aws:bedrock-agentcore:us-east-1:715841330456:runtime/lautech_agentcore-KLZaaW7AR6`
- **Memory:** `lautech_agentcore_mem-yeGCqwG7EM` (STM + LTM enabled)
- **ECR Repository:** `715841330456.dkr.ecr.us-east-1.amazonaws.com/bedrock-agentcore-lautech_agentcore`

### Features
- ✅ PostgreSQL RDS integration
- ✅ AWS Secrets Manager for credentials
- ✅ AgentCore Memory (STM + LTM)
- ✅ Multi-agent routing
- ✅ Course, fees, calendar, and hostel information
- ✅ CloudWatch observability

## 📖 Documentation

- **[PRODUCTION.md](docs/PRODUCTION.md)** - Complete production deployment guide
- **[RDS_SETUP_COMPLETE.md](docs/RDS_SETUP_COMPLETE.md)** - RDS setup and migration details
- **[DATA_GUIDE.md](docs/DATA_GUIDE.md)** - Database schema and data structure

## 🔧 Maintenance

### View Logs
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/lautech_agentcore-KLZaaW7AR6-DEFAULT --follow
```

### Check Status
```bash
agentcore status
```

### Backup Database
```bash
python scripts/backup_database.py
```

## 💰 Cost Estimate

**Current Configuration:**
- RDS (db.t3.micro): ~$13/month
- Storage (20 GB): ~$2.30/month
- Bedrock API calls: Variable
- **Total:** ~$15-25/month

## 🆘 Support

For issues or questions:
1. Check CloudWatch logs
2. Review [PRODUCTION.md](docs/PRODUCTION.md)
3. Check AWS Bedrock model access status

---

**Last Updated:** January 5, 2026
**Status:** ✅ Production Ready
